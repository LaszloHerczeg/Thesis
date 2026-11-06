import csv
from functools import lru_cache
from pathlib import Path

from classification.models import Rule

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_rules():
    """
    Loads rules from db into a dictionary

    e.g.:
    rules = {
        "expression1": {"category1_id": 0.8, "category2_id": 0.5},
        "expression2": {"category1_id": 0.3},
    }
    """
    rules =  {}

    rows = (Rule.objects
                  .filter(is_active=True)
                  .values_list("id", "expression", "category_id", "weight"))

    for rule_id, expression, category_id, weight in rows:
        rules.setdefault(expression, {})[category_id] = (weight, rule_id)
    return rules

@lru_cache(maxsize=1)
def get_rules():
    return _load_rules()

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