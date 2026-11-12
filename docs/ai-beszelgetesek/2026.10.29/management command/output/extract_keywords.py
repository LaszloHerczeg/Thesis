import csv
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


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

# Folder names under DATA_DIR
TXT_DIR_NAME = "txt"
FULL_CSV_DIR_NAME = "full csv"

# At most this many existing files are listed before asking to overwrite
MAX_LISTED_FILES = 10


# TODO: normalize total_d

def load_model():
    try:
        import spacy
    except ImportError:
        raise CommandError("ERROR: spaCy is not installed. Run: pip install huspacy")
    try:
        nlp = spacy.load(settings.MODEL_NAME)
    except OSError:
        raise CommandError(f"ERROR: the {settings.MODEL_NAME} model is not installed.\n"
                           f'Run: python -c "import huspacy; huspacy.download(\'{settings.MODEL_NAME}\')"')

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
    """Count 1...max_n-grams in the runs. N-grams starting or ending with a
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


def clean_lemma(tok):
    """Lowercased lemma of a word token, or None if the token breaks n-grams."""
    if tok.is_punct or tok.pos_ in BREAK_POS or DIGIT_RE.search(tok.text):
        return None
    lemma = (tok.lemma_ or tok.text).strip().lower()
    lemma = lemma.strip(".")  # abbreviations: "Ptk." -> "ptk"
    if not WORD_RE.fullmatch(lemma):
        return None
    return lemma


def write_csv(path: Path, header, rows, delimiter):
    # utf-8-sig writes a BOM, which makes Excel recognise UTF-8 so that
    # á, é, ő, ű etc. display correctly.
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(rows)


def confirm_overwrite(command: BaseCommand, existing: list[Path], assume_yes: bool) -> bool:
    """Warn about output files that already exist and ask whether to continue.

    Returns True if the command may go on (nothing to overwrite, --yes was
    given, or the user answered yes), False if the user declined.
    """
    if not existing:
        return True

    command.stdout.write(command.style.WARNING(
        f"WARNING: {len(existing)} output file(s) already exist and will be "
        f"completely overwritten:"))
    for path in existing[:MAX_LISTED_FILES]:
        command.stdout.write(f"  - {path}")
    if len(existing) > MAX_LISTED_FILES:
        command.stdout.write(f"  ... and {len(existing) - MAX_LISTED_FILES} more")

    if assume_yes:
        command.stdout.write("Overwriting (--yes was given).")
        return True

    if not sys.stdin.isatty():
        raise CommandError("ERROR: output files already exist and there is no terminal "
                           "to confirm. Re-run with --yes to overwrite them.")
    try:
        answer = input("Are you sure you want to continue? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        command.stdout.write("")
        answer = ""

    if answer in ("y", "yes"):
        return True
    command.stdout.write("Aborted. No files were overwritten.")
    return False


def available_law_types(root: Path) -> list[str]:
    """Return the names of the legal field folders under the given root."""
    return sorted(
        p.name for p in root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def resolve_law_type(root: Path, law_type: str, label: str) -> Path:
    """Return root/<law_type>, or raise a CommandError listing the available ones."""
    law_types = available_law_types(root)
    if law_type in law_types:
        return root / law_type
    if not law_types:
        raise CommandError(f"ERROR: unknown {label} legal field: '{law_type}'. "
                           f"No legal field folders found in {root}")
    listing = "\n".join(f"  - {name}" for name in law_types)
    raise CommandError(f"ERROR: unknown {label} legal field: '{law_type}'\n"
                       f"Available legal fields:\n{listing}")


class Command(BaseCommand):
    """
    extract_keywords.py - characteristic lemmas / n-grams of a legal field.

    Extracts 1-, 2- and 3-word lemma sequences from the .txt files of a TARGET
    legal field (Hungarian case descriptions, one case per file, UTF-8) and of a
    REFERENCE legal field of general cases, and stores their n, d, N_d, r, N_r,
    log_ratio and total_d in a csv file sorted by log_ratio.

    Input:   <DATA_DIR>/txt/<law_type>/        and <DATA_DIR>/txt/<reference>/
    Output:  <DATA_DIR>/full csv/<law_type>/<output>

    - d = number of target documents containing it
    - N_d = total number of target documents
    - r = number of reference documents containing it
    - N_r = total number of reference documents
    - log_ratio = log2( ((d + 0.5) / (N_d + 1)) / ((r + 0.5) / (N_r + 1)) )
    - total_d = total number of occurrences in the target documents

    Lemmatizes both folders with HuSpaCy (hu_core_news_lg) and writes the full
    table (step 1). This is the slow part.

    Examples:
      python manage.py extract_keywords csaladjog altalanos
      python manage.py extract_keywords csaladjog altalanos -o step1_teljes.csv --excel-hu
    """
    help = ("Compares word frequencies of 1-, 2- and 3-word lemma sequences of two "
            "legal fields. Results are stored in a csv file.")

    def add_arguments(self, parser):
        parser.add_argument("law_type",
                            help="Analysed legal field, i.e. the folder name under "
                                 "data/txt/ (e.g. csaladjog)")
        parser.add_argument("reference",
                            help="Reference legal field of general cases, i.e. the folder "
                                 "name under data/txt/ (e.g. altalanos)")
        parser.add_argument("-o", "--output", default="step1_full.csv",
                            help="Output CSV file name, written to "
                                 "data/full csv/<law_type>/ (default: step1_full.csv)")
        parser.add_argument("--excel-hu", action="store_true",
                            help="Use ';' as delimiter and a decimal comma, for Excel "
                                 "with Hungarian regional settings")
        parser.add_argument("--batch-size", type=int, default=4,
                            help="Documents per spaCy batch (default: 4)")
        parser.add_argument("--n-process", type=int, default=1,
                            help="Parallel processes for lemmatization (default: 1)")
        parser.add_argument("-y", "--yes", action="store_true",
                            help="Overwrite an existing output file without asking")

    def handle(self, *args, **options):
        law_type = options["law_type"]
        reference = options["reference"]
        data_dir = Path(settings.DATA_DIR)
        txt_root = data_dir / TXT_DIR_NAME

        if not txt_root.is_dir():
            raise CommandError(f"ERROR: text root folder not found: {txt_root}")
        if law_type == reference:
            raise CommandError("ERROR: the target and the reference legal field "
                               "must be different.")

        target_dir = resolve_law_type(txt_root, law_type, "target")
        ref_dir = resolve_law_type(txt_root, reference, "reference")

        # Only a file name is accepted, the folder is always data/full csv/<law_type>/
        out_dir = data_dir / FULL_CSV_DIR_NAME / law_type
        out_path = out_dir / Path(options["output"]).name

        # Ask before the slow lemmatization, not after it
        existing = [out_path] if out_path.exists() else []
        if not confirm_overwrite(self, existing, options["yes"]):
            return

        target_docs = self.read_folder(target_dir, "target")
        ref_docs = self.read_folder(ref_dir, "reference")
        N_d, N_r = len(target_docs), len(ref_docs)

        self.stderr.write(f"Loading {settings.MODEL_NAME}...")
        nlp, stopwords = load_model()

        doc_freq_target = Counter()  # d: number of target documents containing it
        total_target = Counter()  # total_d: occurrences in all target documents
        for counts in self.analyze(nlp, target_docs, stopwords, "target",
                                   options["batch_size"], options["n_process"]):
            total_target.update(counts)
            doc_freq_target.update(counts.keys())

        # For the reference folder only lemmas that occur in the target folder
        # are counted (keeps memory usage low).
        vocabulary = doc_freq_target.keys()
        doc_freq_ref = Counter()  # r: number of reference documents containing it
        for counts in self.analyze(nlp, ref_docs, stopwords, "reference",
                                   options["batch_size"], options["n_process"]):
            doc_freq_ref.update(k for k in counts if k in vocabulary)

        rows = []
        for lemma, d in doc_freq_target.items():
            r = doc_freq_ref.get(lemma, 0)
            log_ratio = math.log2(((d + 0.5) / (N_d + 1)) / ((r + 0.5) / (N_r + 1)))
            rows.append((lemma, lemma.count(" ") + 1, d, N_d, r, N_r,
                         round(log_ratio, 3), total_target[lemma]))

        # log_ratio descending; ties: more target documents first, then alphabetical
        rows.sort(key=lambda row: (-row[6], -row[2], row[0]))

        if options["excel_hu"]:
            delimiter = ";"
            out_rows = [row[:6] + (f"{row[6]:.3f}".replace(".", ","),) + row[7:]
                        for row in rows]
        else:
            delimiter = ","
            out_rows = [row[:6] + (f"{row[6]:.3f}",) + row[7:] for row in rows]

        out_dir.mkdir(parents=True, exist_ok=True)
        write_csv(out_path, STEP1_COLUMNS, out_rows, delimiter)

        by_n = Counter(row[1] for row in rows)
        self.stdout.write("")
        self.stdout.write("=== Summary (step 1) ===")
        self.stdout.write(f"Target field:         {law_type} ({N_d} documents)")
        self.stdout.write(f"Reference field:      {reference} ({N_r} documents)")
        self.stdout.write(f"Lemmas / n-grams:     {len(rows)}  "
                          f"(1-word: {by_n[1]}, 2-word: {by_n[2]}, 3-word: {by_n[3]})")
        self.stdout.write(f"Written to:           {out_path}")

    def read_folder(self, folder: Path, label: str):
        """Return [(file name, normalized text)] for every .txt file in the folder."""
        files = sorted(p for p in folder.iterdir()
                       if p.is_file() and p.suffix.lower() == ".txt")
        if not files:
            raise CommandError(f"ERROR: no .txt files found in the {label} folder: {folder}")

        docs = []
        for path in files:
            raw = path.read_bytes()
            try:
                text = raw.decode("utf-8-sig")  # also strips a BOM if present
            except UnicodeDecodeError:
                self.stderr.write(f"  WARNING: {path.name} is not valid UTF-8; "
                                  f"undecodable bytes were replaced.")
                text = raw.decode("utf-8-sig", errors="replace")
            # Line breaks (and any other whitespace run) become a single space,
            # so an n-gram can continue on the next line.
            text = WHITESPACE_RE.sub(" ", text).strip()
            if not text:
                self.stderr.write(f"  WARNING: {path.name} is empty "
                                  f"(still counted as a document).")
            docs.append((path.name, text))
        return docs

    def analyze(self, nlp, docs, stopwords, label, batch_size, n_process):
        """Yield an n-gram Counter for each document, with progress output."""
        texts = [text for _, text in docs]
        longest = max((len(t) for t in texts), default=0)
        if longest >= nlp.max_length:
            nlp.max_length = longest + 1

        total = len(texts)
        step = max(1, total // 20)
        start = time.time()
        self.stderr.write(f"Lemmatizing {label} folder ({total} documents)...")
        for i, doc in enumerate(nlp.pipe(texts, batch_size=batch_size,
                                         n_process=n_process), start=1):
            yield ngrams_of_runs(word_runs(doc), stopwords)
            if i % step == 0 or i == total:
                elapsed = time.time() - start
                self.stderr.write(f"  {label}: {i}/{total} documents ({elapsed:.0f} s)")
