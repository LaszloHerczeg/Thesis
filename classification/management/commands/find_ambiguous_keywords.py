import csv
from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

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
                raise CommandError(f"ERROR: {path} is missing column(s): {', '.join(missing)}")
            rows = []
            for row in reader:
                if any(cell.strip() for cell in row):
                    rows.append(dict(zip(header, (cell.strip() for cell in row))))
            return rows
    except FileNotFoundError:
        raise CommandError(f"ERROR: file not found: {path}")


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
        raise CommandError(f"ERROR: stoplist not found: {path}")

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



class Command(BaseCommand):
    """
    Find short lemmas that are ambiguous across two legal categories.

    Short lemmas (n=1, n=2) come from both FULL lists; longer phrases come from both
    FILTERED lists. A short lemma is ambiguous if, after all filters, it still
    matches at least one longer phrase from EACH category.

    Usage:
        python manage.py find_ambiguous_keywords.py CAT1 FULL1.csv FILTERED1.csv CAT2 FULL2.csv FILTERED2.csv
            [-o OUT.csv] [--stoplist STOP.txt] [--min-weight 3] [--max-matches 20]
            [--min-diff 50] [--top-n 3] [--delimiter ","]

    Standard library only.
    """
    help = "Finds short lemmas that are ambiguous across two legal categories."
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("cat1", help="Name of the first category")
        parser.add_argument("full1", help="Path to the first full list")
        parser.add_argument("filtered1", help="Path to the first filtered list")
        parser.add_argument("cat2", help="Name of the second category")
        parser.add_argument("full2", help="Path to the second full list")
        parser.add_argument("filtered2", help="Path to the second filtered list")
        parser.add_argument("-o", "--output", default="ambiguous_lemmas.csv",
                       help="output CSV (default: ambiguous_lemmas.csv)")
        parser.add_argument("--stoplist", default=None,
                       help="text file, one lemma per line; those short lemmas are skipped")
        parser.add_argument("--min-weight", type=float, default=3,
                       help="ignore longer phrases with weight below this (default: 3)")
        parser.add_argument("--max-matches", type=int, default=20,
                       help="drop a short lemma matching more than this many different longer phrases (default: 20)")
        parser.add_argument("--min-diff", type=float, default=50,
                       help="keep a match only if the score difference is at least this many percent (default: 50)")
        parser.add_argument("--top-n", type=int, default=3,
                       help="keep the top N longer phrases per category for each short lemma (default: 3)")
        parser.add_argument("--delimiter", default=",",
                       help='output delimiter, e.g. ";" for Hungarian/German Excel (default: ,)')

    def handle(self, *args, **options):
        cat1, cat2 = norm(options['cat1']), norm(options['cat2'])
        if cat1 == cat2:
            raise CommandError("ERROR: the two category names must be different.")
        if options['top_n'] < 1 or options['max_matches'] < 1:
            raise CommandError("ERROR: --top-n and --max-matches must be at least 1.")

        # Short lemmas from both full lists (score = highest total_d)
        short = {}
        load_full_list(options['full1'], short)
        load_full_list(options['full2'], short)
        single_words = {lemma for lemma, (n, _, _) in short.items() if n == 1}  # for compound check
        total_short = len(short)

        # Longer phrases from both filtered lists
        entries, seen = [], set()
        load_filtered_list(options['filtered1'], cat1, entries, seen)
        load_filtered_list(options['filtered2'], cat2, entries, seen)

        # 1. Stoplist
        stoplist = load_stoplist(options['stoplist'])
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
            if len({m["phrase"] for m in matches}) > options['max_matches']:
                removed_general += 1
                continue

            # 4. Score difference
            if score <= 0:  # difference undefined
                removed_zero_score += 1
                continue
            scored = []
            for m in matches:
                diff = abs(m["weight"] - score) / score * 100
                if diff >= options['min_diff'] - 1e-9:
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
                top.extend(items[:options['top_n']])
                removed_top += max(0, len(items) - options['top_n'])

            # 6. Ambiguity: needs at least one phrase from each category
            if {m["category"] for m, _ in top} != both:
                removed_ambig += 1
                continue

            kept += 1
            for m, diff in top:
                rows.append((lemma, score_text, m["phrase"], m["category"], m["weight"], m["weight_text"], diff))

        rows.sort(key=lambda r: (r[0], r[3], -r[4], r[2]))

        # utf-8-sig writes a BOM so Excel shows Hungarian characters correctly
        with open(options['output'], "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=options['delimiter'])
            writer.writerow(
                ["substring", "substring_score", "longer_phrase", "category", "weight", "difference_percent"])
            for lemma, score_text, phrase, category, _, weight_text, diff in rows:
                writer.writerow([lemma, score_text, phrase, category, weight_text, f"{diff:.1f}"])

        self.stdout.write(f"Short lemmas checked:                 {total_short}")
        self.stdout.write(f"1. Stoplist:       lemmas removed     {len(removed_stop)}")
        self.stdout.write(f"2. Min weight:     phrases removed    {removed_weight}  (weight < {options['min_weight']:g})")
        self.stdout.write(f"   (lemmas with no matching phrase:   {no_match})")
        self.stdout.write(f"3. Too general:    lemmas removed     {removed_general}  (> {options['max_matches']} phrases)")
        self.stdout.write(f"4. Score diff:     matches removed    {removed_diff}  (< {options['min_diff']:g}%)")
        if removed_zero_score:
            self.stdout.write(f"   (lemmas skipped, score 0:          {removed_zero_score})")
        self.stdout.write(f"5. Top {options['top_n']}:          matches removed    {removed_top}")
        self.stdout.write(f"6. Ambiguity:      lemmas removed     {removed_ambig}")
        self.stdout.write(f"Ambiguous lemmas kept:                {kept}")
        self.stdout.write(f"Rows written:                         {len(rows)}")
        self.stdout.write(f"Output file:                          {options['output']}")

