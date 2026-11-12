#!/usr/bin/env python3
"""
Find short lemmas that are ambiguous across two legal categories.

Short lemmas (n=1, n=2) come from both FULL lists; longer phrases come from both
FILTERED lists. A short lemma is ambiguous if, after all filters, it still
matches at least one longer phrase from EACH category.

Usage:
    python ambiguous_lemmas.py CAT1 FULL1.csv FILTERED1.csv CAT2 FULL2.csv FILTERED2.csv
        [-o OUT.csv] [--stoplist STOP.txt] [--min-weight 3] [--max-matches 20]
        [--min-diff 50] [--top-n 3] [--delimiter ","]

Standard library only.
"""
import argparse
import csv
import sys
from collections import defaultdict


# ---------------------------------------------------------------- reading

def norm(text):
    """Trim and collapse internal whitespace."""
    return " ".join(text.split())


def to_number(text):
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return 0.0


def read_csv(path, required):
    """Read a UTF-8 (optionally BOM) CSV with "," or ";" as delimiter."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            first_line = f.readline()
            delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)
            header = [h.strip().lower() for h in next(reader, [])]
            missing = [c for c in required if c not in header]
            if missing:
                sys.exit(f"ERROR: {path} is missing column(s): {', '.join(missing)}")
            rows = []
            for row in reader:
                if any(cell.strip() for cell in row):
                    rows.append(dict(zip(header, (cell.strip() for cell in row))))
            return rows
    except FileNotFoundError:
        sys.exit(f"ERROR: file not found: {path}")


def load_full_list(path, short):
    """Collect n=1 and n=2 lemmas into short = {lemma: [n, score, score_text]},
    keeping the highest total_d seen across both full lists."""
    for row in read_csv(path, ["lemma", "n", "total_d"]):
        lemma = norm(row["lemma"])
        if not lemma:
            continue
        try:
            n = int(float(row["n"]))
        except ValueError:
            n = len(lemma.split())
        if n not in (1, 2) or len(lemma.split()) != n:
            continue
        score = to_number(row["total_d"])
        if lemma not in short or score > short[lemma][1]:
            short[lemma] = [n, score, row["total_d"]]


def load_filtered_list(path, category, entries, seen):
    """Append longer phrases as dicts; same phrase in both categories = two entries."""
    for row in read_csv(path, ["lemma", "total_d"]):
        phrase = norm(row["lemma"])
        if not phrase or (phrase, category) in seen:
            continue
        seen.add((phrase, category))
        entries.append({
            "phrase": phrase,
            "words": phrase.split(),
            "category": category,
            "weight": to_number(row["total_d"]),
            "weight_text": row["total_d"],
        })


def load_stoplist(path):
    """One lemma per line; blank lines and lines starting with # are ignored."""
    if not path:
        return set()
    try:
        with open(path, encoding="utf-8-sig") as f:
            return {norm(line) for line in f if norm(line) and not line.lstrip().startswith("#")}
    except FileNotFoundError:
        sys.exit(f"ERROR: stoplist not found: {path}")


# ---------------------------------------------------------------- matching

def build_indexes(entries, single_words):
    """
    word_idx:     word -> phrases (n=2/3) containing that exact word          (rule a)
    compound_idx: part -> phrases (n=1/2/3) with a word that starts or ends
                  with `part`, where the remaining part is an n=1 lemma        (rules a, b)
    bigram_idx:   (w1, w2) -> phrases (n=3) with those consecutive words      (rule c)
    """
    word_idx = defaultdict(set)
    compound_idx = defaultdict(set)
    bigram_idx = defaultdict(set)
    for i, e in enumerate(entries):
        words = e["words"]
        n = len(words)
        if n not in (1, 2, 3):
            continue
        for w in words:
            for cut in range(1, len(w)):
                head, tail = w[:cut], w[cut:]
                if tail in single_words:   # short lemma at the start, e.g. tartás|díj
                    compound_idx[head].add(i)
                if head in single_words:   # short lemma at the end, e.g. albérlet|szerződés
                    compound_idx[tail].add(i)
        if n in (2, 3):
            for w in words:
                word_idx[w].add(i)
        if n == 3:
            bigram_idx[(words[0], words[1])].add(i)
            bigram_idx[(words[1], words[2])].add(i)
    return word_idx, compound_idx, bigram_idx


def find_matches(lemma, n, entries, word_idx, compound_idx, bigram_idx):
    if n == 1:
        hits = word_idx.get(lemma, set()) | compound_idx.get(lemma, set())
    else:
        hits = set(bigram_idx.get(tuple(lemma.split()), ()))
    return [entries[i] for i in hits if entries[i]["phrase"] != lemma]


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="Find short lemmas ambiguous across two legal categories.")
    p.add_argument("cat1")
    p.add_argument("full1")
    p.add_argument("filtered1")
    p.add_argument("cat2")
    p.add_argument("full2")
    p.add_argument("filtered2")
    p.add_argument("-o", "--output", default="ambiguous_lemmas.csv",
                   help="output CSV (default: ambiguous_lemmas.csv)")
    p.add_argument("--stoplist", default=None,
                   help="text file, one lemma per line; those short lemmas are skipped")
    p.add_argument("--min-weight", type=float, default=3,
                   help="ignore longer phrases with weight below this (default: 3)")
    p.add_argument("--max-matches", type=int, default=20,
                   help="drop a short lemma matching more than this many different longer phrases (default: 20)")
    p.add_argument("--min-diff", type=float, default=50,
                   help="keep a match only if the score difference is at least this many percent (default: 50)")
    p.add_argument("--top-n", type=int, default=3,
                   help="keep the top N longer phrases per category for each short lemma (default: 3)")
    p.add_argument("--delimiter", default=",",
                   help='output delimiter, e.g. ";" for Hungarian/German Excel (default: ,)')
    args = p.parse_args()

    cat1, cat2 = norm(args.cat1), norm(args.cat2)
    if cat1 == cat2:
        sys.exit("ERROR: the two category names must be different.")
    if args.top_n < 1 or args.max_matches < 1:
        sys.exit("ERROR: --top-n and --max-matches must be at least 1.")

    # Short lemmas from both full lists (score = highest total_d)
    short = {}
    load_full_list(args.full1, short)
    load_full_list(args.full2, short)
    single_words = {lemma for lemma, (n, _, _) in short.items() if n == 1}  # for compound check
    total_short = len(short)

    # Longer phrases from both filtered lists
    entries, seen = [], set()
    load_filtered_list(args.filtered1, cat1, entries, seen)
    load_filtered_list(args.filtered2, cat2, entries, seen)

    # 1. Stoplist
    stoplist = load_stoplist(args.stoplist)
    removed_stop = [lemma for lemma in short if lemma in stoplist]
    for lemma in removed_stop:
        del short[lemma]

    # 2. Minimum weight (longer phrases)
    before = len(entries)
    entries = [e for e in entries if e["weight"] >= args.min_weight]
    removed_weight = before - len(entries)

    word_idx, compound_idx, bigram_idx = build_indexes(entries, single_words)
    both = {cat1, cat2}

    no_match = removed_general = removed_zero_score = 0
    removed_diff = removed_top = removed_ambig = 0
    kept = 0
    rows = []

    for lemma, (n, score, score_text) in short.items():
        matches = find_matches(lemma, n, entries, word_idx, compound_idx, bigram_idx)
        if not matches:
            no_match += 1
            continue

        # 3. Too general
        if len({m["phrase"] for m in matches}) > args.max_matches:
            removed_general += 1
            continue

        # 4. Score difference
        if score <= 0:  # difference undefined
            removed_zero_score += 1
            continue
        scored = []
        for m in matches:
            diff = abs(m["weight"] - score) / score * 100
            if diff >= args.min_diff - 1e-9:
                scored.append((m, diff))
            else:
                removed_diff += 1

        # 5. Top N per category by weight
        by_cat = defaultdict(list)
        for m, diff in scored:
            by_cat[m["category"]].append((m, diff))
        top = []
        for items in by_cat.values():
            items.sort(key=lambda x: (-x[0]["weight"], x[0]["phrase"]))
            top.extend(items[:args.top_n])
            removed_top += max(0, len(items) - args.top_n)

        # 6. Ambiguity: needs at least one phrase from each category
        if {m["category"] for m, _ in top} != both:
            removed_ambig += 1
            continue

        kept += 1
        for m, diff in top:
            rows.append((lemma, score_text, m["phrase"], m["category"], m["weight"], m["weight_text"], diff))

    rows.sort(key=lambda r: (r[0], r[3], -r[4], r[2]))

    # utf-8-sig writes a BOM so Excel shows Hungarian characters correctly
    with open(args.output, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=args.delimiter)
        writer.writerow(["substring", "substring_score", "longer_phrase", "category", "weight", "difference_percent"])
        for lemma, score_text, phrase, category, _, weight_text, diff in rows:
            writer.writerow([lemma, score_text, phrase, category, weight_text, f"{diff:.1f}"])

    print(f"Short lemmas checked:                 {total_short}")
    print(f"1. Stoplist:       lemmas removed     {len(removed_stop)}")
    print(f"2. Min weight:     phrases removed    {removed_weight}  (weight < {args.min_weight:g})")
    print(f"   (lemmas with no matching phrase:   {no_match})")
    print(f"3. Too general:    lemmas removed     {removed_general}  (> {args.max_matches} phrases)")
    print(f"4. Score diff:     matches removed    {removed_diff}  (< {args.min_diff:g}%)")
    if removed_zero_score:
        print(f"   (lemmas skipped, score 0:          {removed_zero_score})")
    print(f"5. Top {args.top_n}:          matches removed    {removed_top}")
    print(f"6. Ambiguity:      lemmas removed     {removed_ambig}")
    print(f"Ambiguous lemmas kept:                {kept}")
    print(f"Rows written:                         {len(rows)}")
    print(f"Output file:                          {args.output}")


if __name__ == "__main__":
    main()