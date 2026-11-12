import csv
import io
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from classification.management.commands.extract_keywords import (
    FULL_CSV_DIR_NAME,
    STEP2_COLUMNS,
    confirm_overwrite,
    resolve_law_type,
    write_csv,
)

# Folder name under DATA_DIR
FILTERED_CSV_DIR_NAME = "filtered csv"

# Normalized frequency: occurrences per this many kept occurrences
PER_N_WORDS = 100_000


def read_csv(path: Path):
    """Read a step-1 CSV written with either ',' or ';' as delimiter.
    Returns (rows as dicts, delimiter)."""
    text = path.read_text(encoding="utf-8-sig")
    first_line = text.split("\n", 1)[0]
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter)
    missing = {"lemma", "d", "log_ratio", "total_d"} - set(reader.fieldnames or [])
    if missing:
        raise CommandError(f"ERROR: {path} is not a step-1 table "
                           f"(missing columns: {', '.join(sorted(missing))}).")
    return list(reader), delimiter


def to_float(value: str) -> float:
    return float(value.strip().replace(",", "."))  # accepts decimal comma too


def resolve_input_file(folder: Path, file_name: str) -> Path:
    """Return folder/<file_name>, or raise a CommandError listing the CSVs there."""
    path = folder / file_name
    if path.is_file():
        return path
    csv_files = sorted(p.name for p in folder.iterdir()
                       if p.is_file() and p.suffix.lower() == ".csv")
    if not csv_files:
        raise CommandError(f"ERROR: file not found: {path}\n"
                           f"No CSV files in {folder}. Run extract_keywords first.")
    listing = "\n".join(f"  - {name}" for name in csv_files)
    raise CommandError(f"ERROR: file not found: {path}\n"
                       f"Available CSV files:\n{listing}")


class Command(BaseCommand):
    """
    filter_keywords - characteristic lemmas / n-grams of a legal field (step 2).

    Reads the step-1 CSV written by the extract_keywords command and keeps only
    the 1-, 2- and 3-word lemma sequences that pass the thresholds. No text
    processing, runs in seconds.

    Input:   <DATA_DIR>/full csv/<law_type>/<input>
    Output:  <DATA_DIR>/filtered csv/<law_type>/<output>

    Examples:
      python manage.py filter_keywords csaladjog
      python manage.py filter_keywords csaladjog -i step1_teljes.csv -o step2_szurt.csv
      python manage.py filter_keywords csaladjog --min-docs 5 --min-log-ratio 1.5
    """
    help = ("Keeps only the 1-, 2- and 3-word lemma sequences of a legal field "
            "that pass the thresholds, and writes them to a new csv file.")

    def add_arguments(self, parser):
        parser.add_argument("law_type",
                            help="Legal field, i.e. the folder name under "
                                 "data/full csv/ (e.g. csaladjog)")
        parser.add_argument("-i", "--input", default="step1_full.csv",
                            help="Step-1 CSV file name in data/full csv/<law_type>/ "
                                 "(default: step1_full.csv)")
        parser.add_argument("-o", "--output", default="step2_filtered.csv",
                            help="Output CSV file name, written to "
                                 "data/filtered csv/<law_type>/ (default: step2_filtered.csv)")
        parser.add_argument("--min-docs", type=int, default=3,
                            help="Minimum number of target documents, d (default: 3)")
        parser.add_argument("--min-log-ratio", type=float, default=1.0,
                            help="Minimum log_ratio (default: 1.0)")
        parser.add_argument("-y", "--yes", action="store_true",
                            help="Overwrite an existing output file without asking")

    def handle(self, *args: Any, **options: Any) -> str | None:
        law_type = options["law_type"]
        data_dir = Path(settings.DATA_DIR)
        full_csv_root = data_dir / FULL_CSV_DIR_NAME

        if not full_csv_root.is_dir():
            raise CommandError(f"ERROR: full csv root folder not found: {full_csv_root}\n"
                               f"Run extract_keywords first.")

        in_dir = resolve_law_type(full_csv_root, law_type, "target")
        in_path = resolve_input_file(in_dir, Path(options["input"]).name)

        # Only a file name is accepted, the folder is always data/filtered csv/<law_type>/
        out_dir = data_dir / FILTERED_CSV_DIR_NAME / law_type
        out_path = out_dir / Path(options["output"]).name

        existing = [out_path] if out_path.exists() else []
        if not confirm_overwrite(self, existing, options["yes"]):
            return

        rows, delimiter = read_csv(in_path)

        kept = []
        word_counter = 0

        for row in rows:
            try:
                d = int(row["d"])
                log_ratio = to_float(row["log_ratio"])
                total_d = int(row["total_d"])
            except (TypeError, ValueError):
                self.stderr.write(f"  WARNING: skipping unreadable row: {row}")
                continue
            if d >= options["min_docs"] and log_ratio >= options["min_log_ratio"]:
                kept.append((row["lemma"], total_d))
                word_counter += total_d

        kept.sort(key=lambda item: (-item[1], item[0]))  # total_d descending

        # Normalize total_d to occurrences per PER_N_WORDS kept occurrences.
        # Keep the decimal separator consistent with the input file.
        decimal_comma = delimiter == ";"
        out_rows = []
        for lemma, total_d in kept:
            value = f"{total_d * PER_N_WORDS / word_counter:.2f}"
            if decimal_comma:
                value = value.replace(".", ",")
            out_rows.append((lemma, value))

        out_dir.mkdir(parents=True, exist_ok=True)
        write_csv(out_path, STEP2_COLUMNS, out_rows, delimiter)

        self.stdout.write("=== Summary (step 2) ===")
        self.stdout.write(f"Legal field:          {law_type}")
        if rows:
            self.stdout.write(f"Target documents:     {rows[0].get('N_d', '?')}")
            self.stdout.write(f"Reference documents:  {rows[0].get('N_r', '?')}")
        self.stdout.write(f"Thresholds:           d >= {options['min_docs']}, "
                          f"log_ratio >= {options['min_log_ratio']}")
        self.stdout.write(f"Lemmas before filter: {len(rows)}")
        self.stdout.write(f"Lemmas after filter:  {len(kept)}")
        self.stdout.write(f"Read from:            {in_path}")
        self.stdout.write(f"Written to:           {out_path}")
        if not kept:
            self.stdout.write(self.style.WARNING(
                "No lemmas passed the thresholds; the output only has a header."))