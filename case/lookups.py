import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

# TODO: átnevezni a függvényt
def normalize_lemmas():


    print("normalizing lemmas")
    # TODO: cache dicts
    # TODO: csv file megadása paraméterként
    # TODO: MappingProxyType visszaadása?
    # TODO: hatékonyabbra megcsinálni
    file_hazassag = "step2_filtered_hazassag.csv"
    file_munkaviszony = "step2_filtered_munkaviszony.csv"

    # Sum variables, created before reading the lines
    sum_hazassag = 0
    sum_munkaviszony = 0

    # 1. pass: sum of the numbers in each file
    with open(DATA_DIR / file_hazassag, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        for row in reader:
            sum_hazassag += int(row[1])

    with open(DATA_DIR / file_munkaviszony, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        for row in reader:
            sum_munkaviszony += int(row[1])

    # 2. pass: dictionaries with normalized values (per 100,000)
    hazassag_dict = {}
    with open(DATA_DIR / file_hazassag, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        for row in reader:
            lemma = row[0]
            hazassag_dict[lemma] = int(row[1]) * (100000 / sum_hazassag)

    munkaviszony_dict = {}
    with open(DATA_DIR / file_munkaviszony, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # skip header line
        for row in reader:
            lemma = row[0]
            munkaviszony_dict[lemma] = int(row[1]) * (100000 / sum_munkaviszony)

    print("sum_hazassag:", sum_hazassag)
    print("sum_munkaviszony:", sum_munkaviszony)
    print("hazassag_dict:", len(hazassag_dict), "lemmas")
    print("munkaviszony_dict:", len(munkaviszony_dict), "lemmas")

    return hazassag_dict, munkaviszony_dict

def create_ambiguous_keyword_dictionary():



    # TODO: cache dicts
    # TODO: csv file megadása paraméterként
    # TODO: MappingProxyType visszaadása?
    file_name = "ambiguous_keywords.csv"

    ambiguous_keyword_dict = {}

    with open(DATA_DIR / file_name, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            if len(row) < 2 or row[0] == "substring":
                continue
            ambiguous_keyword_dict.setdefault(row[0], []).append(row[1])
    return ambiguous_keyword_dict