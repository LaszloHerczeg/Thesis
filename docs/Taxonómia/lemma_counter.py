#!/usr/bin/env python3
"""
Lemmatize Hungarian .txt files with HuSpaCy (hu_core_news_lg) and count lemma frequencies.

Usage:
    python lemma_counter.py <input_folder> [-o output.csv] [--no-stopwords] [--recursive]

Output: a CSV file with two columns: lemma, count (most frequent first).
Besides single lemmas, every pair of adjacent lemmas (e.g. "házasság megszüntetés")
is counted as its own row. Pairs can span line breaks, but never punctuation or numbers.

Requirements:
    pip install huspacy
    python -c "import huspacy; huspacy.download('hu_core_news_lg')"
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

import spacy

MODEL_NAME = "hu_core_news_lg"
CHUNK_CHARS = 100_000  # keep each piece well under spaCy's max_length


def load_model():
    """Load the HuSpaCy model, downloading it if it isn't installed yet."""
    try:
        nlp = spacy.load(MODEL_NAME)
    except OSError:
        print(f"Model '{MODEL_NAME}' not found, downloading via huspacy...")
        import huspacy
        huspacy.download(MODEL_NAME)
        nlp = spacy.load(MODEL_NAME)

    # Components not needed for lemmatization; disabling them speeds things up a lot.
    unneeded = [p for p in ("parser", "ner", "experimental_arc_predicter",
                            "experimental_arc_labeler") if p in nlp.pipe_names]
    if unneeded:
        nlp.select_pipes(disable=unneeded)
    return nlp


def read_text(path: Path) -> str:
    """Read a text file, trying UTF-8 first and falling back to common Hungarian encodings."""
    for enc in ("utf-8-sig", "cp1250", "iso-8859-2"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def split_into_chunks(text: str, size: int = CHUNK_CHARS):
    """Split long text on paragraph boundaries so no piece exceeds `size` characters."""
    chunk, length = [], 0
    for para in text.split("\n"):
        if length + len(para) > size and chunk:
            yield "\n".join(chunk)
            chunk, length = [], 0
        # A single huge paragraph gets hard-split
        while len(para) > size:
            yield para[:size]
            para = para[size:]
        chunk.append(para)
        length += len(para) + 1
    if chunk:
        yield "\n".join(chunk)


def main():
    parser = argparse.ArgumentParser(description="Lemmatize Hungarian .txt files and count lemmas.")
    parser.add_argument("folder", help="Folder containing the .txt files")
    parser.add_argument("-o", "--output", default="lemma_frequencies.csv",
                        help="Output CSV file (default: lemma_frequencies.csv)")
    parser.add_argument("--no-stopwords", action="store_true",
                        help="Leave out stopwords (a, az, és, hogy, ...)")
    parser.add_argument("--recursive", action="store_true",
                        help="Also read .txt files in subfolders")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        sys.exit(f"Error: '{folder}' is not a folder.")

    pattern = "**/*.txt" if args.recursive else "*.txt"
    files = sorted(p for p in folder.glob(pattern) if p.is_file())
    if not files:
        sys.exit(f"No .txt files found in '{folder}'.")

    print(f"Loading {MODEL_NAME}...")
    nlp = load_model()

    lemma_counts = Counter()   # single lemmas
    bigram_counts = Counter()  # pairs of adjacent lemmas, e.g. "házasság megszüntetés"
    words_per_file = {}

    for i, path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {path.name}")
        text = read_text(path)
        file_words = 0
        # Kept across chunks too, since chunks are cut at line breaks
        prev_lemma = None  # previous word lemma, if it is directly adjacent
        for doc in nlp.pipe(split_into_chunks(text), batch_size=8):
            for token in doc:
                # Line breaks and extra spaces are ignored: two words with a line
                # break between them still form a pair.
                if token.is_space:
                    continue
                # Only real words count. Punctuation, numbers and symbols are skipped
                # AND break adjacency, so no pair spans e.g. a comma or a full stop.
                if not token.is_alpha:
                    prev_lemma = None
                    continue
                # A skipped stopword also breaks adjacency, so pairs are always
                # two words that really stand next to each other in the text.
                if args.no_stopwords and token.is_stop:
                    prev_lemma = None
                    continue
                lemma = (token.lemma_ or token.text).lower()
                lemma_counts[lemma] += 1
                file_words += 1
                if prev_lemma is not None:
                    bigram_counts[f"{prev_lemma} {lemma}"] += 1
                prev_lemma = lemma
        words_per_file[path.name] = file_words

    total_words = sum(words_per_file.values())

    # Single lemmas and pairs go into one list (a pair always contains a space,
    # a single lemma never does, so they can't collide)
    all_counts = lemma_counts + bigram_counts

    # utf-8-sig adds a BOM so Excel shows Hungarian accented letters correctly
    with open(args.output, "w", encoding="utf-8-sig", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["lemma", "count"])
        for lemma, count in sorted(all_counts.items(), key=lambda x: (-x[1], x[0])):
            writer.writerow([lemma, count])

    # Summary goes to the console so the CSV stays a clean two-column table
    print("\nWords per document:")
    for name, count in words_per_file.items():
        print(f"  {name}: {count}")
    print(f"\nDone. {len(files)} documents, {total_words} words, "
          f"{len(lemma_counts)} distinct lemmas, {len(bigram_counts)} distinct lemma pairs"
          f"{' (stopwords excluded)' if args.no_stopwords else ''} -> {args.output}")


if __name__ == "__main__":
    main()