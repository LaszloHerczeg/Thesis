import csv

file_hazassag = "lemma_frequencies_házasság.csv"
file_munkaviszony = "lemma_frequencies_munkaviszony.csv"

# Sum variables, created before reading the lines
sum_hazassag = 0
sum_munkaviszony = 0

# 1. pass: sum of the numbers in each file
with open(file_hazassag, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)  # skip header line
    for row in reader:
        sum_hazassag += int(row[1])

with open(file_munkaviszony, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)  # skip header line
    for row in reader:
        sum_munkaviszony += int(row[1])

# 2. pass: dictionaries with normalized values (per 100,000)
hazassag_dict = {}
with open(file_hazassag, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)  # skip header line
    for row in reader:
        lemma = row[0]
        hazassag_dict[lemma] = int(row[1]) * (100000 / sum_hazassag)

munkaviszony_dict = {}
with open(file_munkaviszony, encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)  # skip header line
    for row in reader:
        lemma = row[0]
        munkaviszony_dict[lemma] = int(row[1]) * (100000 / sum_munkaviszony)

print("sum_hazassag:", sum_hazassag)
print("sum_munkaviszony:", sum_munkaviszony)
print("hazassag_dict:", len(hazassag_dict), "lemmas")
print("munkaviszony_dict:", len(munkaviszony_dict), "lemmas")
