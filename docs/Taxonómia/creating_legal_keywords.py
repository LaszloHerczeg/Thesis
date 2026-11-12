#!/usr/bin/env python3
"""
jogi_kulcsszavak.py - characteristic lemmas / n-grams of a legal field.

Compares a TARGET folder of Hungarian case descriptions (.txt, one case per
file, UTF-8) with a REFERENCE folder of general cases and finds 1-, 2- and
3-word lemma sequences that are over-represented in the target field.

Two sub-commands:

  extract  - lemmatizes both folders with HuSpaCy (hu_core_news_lg) and writes
             the full table (step 1). This is the slow part.
  filter   - reads the step-1 CSV and keeps the lemmas that pass the
             thresholds (step 2). No text processing, runs in seconds.

Examples:
  python jogi_kulcsszavak.py extract csaladjog/ altalanos/ -o step1_teljes.csv
  python jogi_kulcsszavak.py filter step1_teljes.csv -o step2_szurt.csv
  python jogi_kulcsszavak.py filter step1_teljes.csv -o step2_szurt.csv --min-docs 5 --min-log-ratio 1.5
"""

# TODO: normalize total_d

import argparse
import csv
import io
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path

MODEL_NAME = "hu_core_news_lg"
MAX_N = 3

# Tokens with these POS tags end the current run of words, so no n-gram can
# contain or span across them (punctuation, numerals, symbols).
BREAK_POS = {"PUNCT", "NUM", "SYM"}

# A valid lemma is made of letters only, optionally joined by a hyphen or an
# apostrophe (e.g. "ptk", "szülői", "kft", "e-mail"). [^\W\d_] = any Unicode
# letter, so á, é, ő, ű etc. are all included.
WORD_RE = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")
DIGIT_RE = re.compile(r"\d")
WHITESPACE_RE = re.compile(r"\s+")

STEP1_COLUMNS = ["lemma", "n", "d", "N_d", "r", "N_r", "log_ratio", "total_d"]
STEP2_COLUMNS = ["lemma", "total_d"]


# --------------------------------------------------------------------------
# Reading files
# --------------------------------------------------------------------------

def read_folder(folder: Path, label: str):
    """Return [(file name, normalized text)] for every .txt file in the folder."""
    if not folder.is_dir():
        sys.exit(f"ERROR: the {label} folder does not exist: {folder}")
    files = sorted(p for p in folder.iterdir()
                   if p.is_file() and p.suffix.lower() == ".txt")
    if not files:
        sys.exit(f"ERROR: no .txt files found in the {label} folder: {folder}")

    docs = []
    for path in files:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8-sig")          # also strips a BOM if present
        except UnicodeDecodeError:
            print(f"  WARNING: {path.name} is not valid UTF-8; "
                  f"undecodable bytes were replaced.", file=sys.stderr)
            text = raw.decode("utf-8-sig", errors="replace")
        # Line breaks (and any other whitespace run) become a single space,
        # so an n-gram can continue on the next line.
        text = WHITESPACE_RE.sub(" ", text).strip()
        if not text:
            print(f"  WARNING: {path.name} is empty (still counted as a document).",
                  file=sys.stderr)
        docs.append((path.name, text))
    return docs


# --------------------------------------------------------------------------
# NLP
# --------------------------------------------------------------------------

def load_model():
    try:
        import spacy
    except ImportError:
        sys.exit("ERROR: spaCy is not installed. Run: pip install huspacy")
    try:
        nlp = spacy.load(MODEL_NAME)
    except OSError:
        sys.exit(f"ERROR: the {MODEL_NAME} model is not installed.\n"
                 f'Run: python -c "import huspacy; huspacy.download(\'{MODEL_NAME}\')"')

    # Named entity recognition is not needed; switching it off saves time.
    unneeded = [name for name in ("ner",) if name in nlp.pipe_names]
    if unneeded:
        nlp.select_pipes(disable=unneeded)

    # Make sure sentence boundaries are available; add a rule-based
    # sentencizer only if the model itself does not set them.
    probe = nlp("Ez az első mondat. Ez a második mondat.")
    if not probe.has_annotation("SENT_START"):
        nlp.add_pipe("sentencizer", first=True)

    from spacy.lang.hu.stop_words import STOP_WORDS
    return nlp, frozenset(w.lower() for w in STOP_WORDS)


def clean_lemma(tok):
    """Lowercased lemma of a word token, or None if the token breaks n-grams."""
    if tok.is_punct or tok.pos_ in BREAK_POS or DIGIT_RE.search(tok.text):
        return None
    lemma = (tok.lemma_ or tok.text).strip().lower()
    lemma = lemma.strip(".")                 # abbreviations: "Ptk." -> "ptk"
    if not WORD_RE.fullmatch(lemma):
        return None
    return lemma


def word_runs(doc):
    """Yield lists of consecutive word lemmas. A run never crosses a sentence
    boundary, punctuation, a number or a symbol."""
    for sent in doc.sents:
        run = []
        for tok in sent:
            if tok.is_space:
                continue
            lemma = clean_lemma(tok)
            if lemma is None:
                if run:
                    yield run
                run = []
            else:
                run.append(lemma)
        if run:
            yield run


def ngrams_of_runs(runs, stopwords, max_n=MAX_N):
    """Count 1..max_n-grams in the runs. N-grams starting or ending with a
    stopword are dropped; stopwords inside a 3-gram are kept."""
    counts = Counter()
    for run in runs:
        length = len(run)
        for n in range(1, max_n + 1):
            for i in range(length - n + 1):
                if run[i] in stopwords or run[i + n - 1] in stopwords:
                    continue
                counts[" ".join(run[i:i + n])] += 1
    return counts


def analyze(nlp, docs, stopwords, label, batch_size, n_process):
    """Yield an n-gram Counter for each document, with progress output."""
    texts = [text for _, text in docs]
    longest = max((len(t) for t in texts), default=0)
    if longest >= nlp.max_length:
        nlp.max_length = longest + 1

    total = len(texts)
    step = max(1, total // 20)
    start = time.time()
    print(f"Lemmatizing {label} folder ({total} documents)...", file=sys.stderr)
    for i, doc in enumerate(nlp.pipe(texts, batch_size=batch_size,
                                     n_process=n_process), start=1):
        yield ngrams_of_runs(word_runs(doc), stopwords)
        if i % step == 0 or i == total:
            elapsed = time.time() - start
            print(f"  {label}: {i}/{total} documents ({elapsed:.0f} s)",
                  file=sys.stderr)


# --------------------------------------------------------------------------
# CSV helpers
# --------------------------------------------------------------------------

def write_csv(path: Path, header, rows, delimiter):
    # utf-8-sig writes a BOM, which makes Excel recognise UTF-8 so that
    # á, é, ő, ű etc. display correctly.
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(rows)


def read_csv(path: Path):
    """Read a step-1 CSV written with either ',' or ';' as delimiter.
    Returns (rows as dicts, delimiter)."""
    if not path.is_file():
        sys.exit(f"ERROR: file not found: {path}")
    text = path.read_text(encoding="utf-8-sig")
    first_line = text.split("\n", 1)[0]
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter)
    missing = {"lemma", "d", "log_ratio", "total_d"} - set(reader.fieldnames or [])
    if missing:
        sys.exit(f"ERROR: {path} is not a step-1 table "
                 f"(missing columns: {', '.join(sorted(missing))}).")
    return list(reader), delimiter


def to_float(value: str) -> float:
    return float(value.strip().replace(",", "."))   # accepts decimal comma too


# --------------------------------------------------------------------------
# Step 1: extract
# --------------------------------------------------------------------------

def cmd_extract(args):
    target_docs = read_folder(Path(args.target), "target")
    ref_docs = read_folder(Path(args.reference), "reference")
    N_d, N_r = len(target_docs), len(ref_docs)

    print(f"Loading {MODEL_NAME}...", file=sys.stderr)
    nlp, stopwords = load_model()

    doc_freq_target = Counter()   # d: number of target documents containing it
    total_target = Counter()      # total_d: occurrences in all target documents
    for counts in analyze(nlp, target_docs, stopwords, "target",
                          args.batch_size, args.n_process):
        total_target.update(counts)
        doc_freq_target.update(counts.keys())

    # For the reference folder only lemmas that occur in the target matter,
    # so only those are counted (keeps memory usage low).
    vocabulary = doc_freq_target.keys()
    doc_freq_ref = Counter()      # r: number of reference documents containing it
    for counts in analyze(nlp, ref_docs, stopwords, "reference",
                          args.batch_size, args.n_process):
        doc_freq_ref.update(k for k in counts if k in vocabulary)

    rows = []
    for lemma, d in doc_freq_target.items():
        r = doc_freq_ref.get(lemma, 0)
        log_ratio = math.log2(((d + 0.5) / (N_d + 1)) / ((r + 0.5) / (N_r + 1)))
        rows.append((lemma, lemma.count(" ") + 1, d, N_d, r, N_r,
                     round(log_ratio, 3), total_target[lemma]))

    # log_ratio descending; ties: more target documents first, then alphabetical
    rows.sort(key=lambda row: (-row[6], -row[2], row[0]))

    if args.excel_hu:
        delimiter = ";"
        out_rows = [row[:6] + (f"{row[6]:.3f}".replace(".", ","),) + row[7:]
                    for row in rows]
    else:
        delimiter = ","
        out_rows = [row[:6] + (f"{row[6]:.3f}",) + row[7:] for row in rows]

    out_path = Path(args.output)
    write_csv(out_path, STEP1_COLUMNS, out_rows, delimiter)

    by_n = Counter(row[1] for row in rows)
    print()
    print("=== Summary (step 1) ===")
    print(f"Target documents:     {N_d}")
    print(f"Reference documents:  {N_r}")
    print(f"Lemmas / n-grams:     {len(rows)}  "
          f"(1-word: {by_n[1]}, 2-word: {by_n[2]}, 3-word: {by_n[3]})")
    print(f"Written to:           {out_path}")


# --------------------------------------------------------------------------
# Step 2: filter
# --------------------------------------------------------------------------

def cmd_filter(args):
    in_path = Path(args.input)
    rows, delimiter = read_csv(in_path)

    kept = []
    for row in rows:
        try:
            d = int(row["d"])
            log_ratio = to_float(row["log_ratio"])
            total_d = int(row["total_d"])
        except (TypeError, ValueError):
            print(f"  WARNING: skipping unreadable row: {row}", file=sys.stderr)
            continue
        if d >= args.min_docs and log_ratio >= args.min_log_ratio:
            kept.append((row["lemma"], total_d))

    kept.sort(key=lambda item: (-item[1], item[0]))   # total_d descending

    out_path = Path(args.output)
    write_csv(out_path, STEP2_COLUMNS, kept, delimiter)

    n_docs_info = ""
    if rows:
        n_docs_info = (f"Target documents:     {rows[0].get('N_d', '?')}\n"
                       f"Reference documents:  {rows[0].get('N_r', '?')}\n")
    print("=== Summary (step 2) ===")
    print(n_docs_info, end="")
    print(f"Thresholds:           d >= {args.min_docs}, "
          f"log_ratio >= {args.min_log_ratio}")
    print(f"Lemmas before filter: {len(rows)}")
    print(f"Lemmas after filter:  {len(kept)}")
    print(f"Written to:           {out_path}")


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Find lemmas and n-grams characteristic of a legal field "
                    "by comparing two folders of Hungarian case descriptions.")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("extract", help="Step 1: lemmatize and build the full table.")
    p1.add_argument("target", help="Folder with .txt files of the analysed field")
    p1.add_argument("reference", help="Folder with .txt files of general cases")
    p1.add_argument("-o", "--output", default="step1_full.csv",
                    help="Output CSV (default: step1_full.csv)")
    p1.add_argument("--excel-hu", action="store_true",
                    help="Use ';' as delimiter and a decimal comma, for Excel "
                         "with Hungarian regional settings")
    p1.add_argument("--batch-size", type=int, default=16,
                    help="Documents per spaCy batch (default: 16)")
    p1.add_argument("--n-process", type=int, default=1,
                    help="Parallel processes for lemmatization (default: 1)")
    p1.set_defaults(func=cmd_extract)

    p2 = sub.add_parser("filter", help="Step 2: filter the step-1 table.")
    p2.add_argument("input", help="CSV written by the extract step")
    p2.add_argument("-o", "--output", default="step2_filtered.csv",
                    help="Output CSV (default: step2_filtered.csv)")
    p2.add_argument("--min-docs", type=int, default=3,
                    help="Minimum number of target documents, d (default: 3)")
    p2.add_argument("--min-log-ratio", type=float, default=1.0,
                    help="Minimum log_ratio (default: 1.0)")
    p2.set_defaults(func=cmd_filter)
    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()