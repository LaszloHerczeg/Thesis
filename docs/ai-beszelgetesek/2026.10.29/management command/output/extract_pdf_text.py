import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pypdf import PdfReader

from classification.management.commands.extract_keywords import confirm_overwrite

PAGE_MARKER_RE = re.compile(r"^--- Page \d+ ---$", re.MULTILINE)


def extract_text(pdf_path: Path, password: str | None = None) -> str:
    """Return the text of a PDF, with a marker between pages."""
    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        # Many "encrypted" PDFs open fine with an empty password
        if not reader.decrypt(password or ""):
            raise ValueError("encrypted (wrong or missing password)")

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"--- Page {i} ---\n{text.strip()}")
    return "\n\n".join(pages)


def available_law_fields(pdf_root: Path) -> list[str]:
    """Return the names of the legal field folders under data/pdf/."""
    return sorted(
        p.name for p in pdf_root.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


class Command(BaseCommand):
    """
    Reads every PDF from   <DATA_DIR>/pdf/<jogterulet>/
    and writes the text to <DATA_DIR>/txt/<jogterulet>/

    Examples:
        python manage.py extract_pdf_text csaladjog
        python manage.py extract_pdf_text csaladjog -r
        python manage.py extract_pdf_text csaladjog --combined
    """
    help = "Extract text from every PDF of a legal field into .txt files."

    def add_arguments(self, parser):
        parser.add_argument(
            "jogterulet",
            help="Legal field, i.e. the folder name under data/pdf/ (e.g. csaladjog)",
        )
        parser.add_argument("-r", "--recursive", action="store_true",
                            help="Also search subfolders")
        parser.add_argument("--combined", action="store_true",
                            help="Write everything into data/txt/<jogterulet>_combined.txt "
                                 "instead of one .txt per PDF")
        parser.add_argument("--password", help="Password for encrypted PDFs")
        parser.add_argument("-y", "--yes", action="store_true",
                            help="Overwrite existing .txt files without asking")

    def handle(self, *args, **options):
        jogterulet = options["jogterulet"]
        data_dir = Path(settings.DATA_DIR)
        pdf_root = data_dir / "pdf"
        txt_root = data_dir / "txt"

        if not pdf_root.is_dir():
            raise CommandError(f"PDF root folder not found: {pdf_root}")

        # Validate the legal field; list the available ones if it is wrong
        fields = available_law_fields(pdf_root)
        if jogterulet not in fields:
            if not fields:
                raise CommandError(
                    f"Unknown legal field: '{jogterulet}'. "
                    f"No legal field folders found in {pdf_root}"
                )
            listing = "\n".join(f"  - {name}" for name in fields)
            raise CommandError(
                f"Unknown legal field: '{jogterulet}'\n"
                f"Available legal fields:\n{listing}"
            )

        in_dir = pdf_root / jogterulet
        out_dir = txt_root / jogterulet
        combined_path = txt_root / f"{jogterulet}_combined.txt"

        pattern = "**/*" if options["recursive"] else "*"
        pdfs = sorted(p for p in in_dir.glob(pattern)
                      if p.is_file() and p.suffix.lower() == ".pdf")
        if not pdfs:
            raise CommandError(f"No PDFs found in {in_dir}")

        # Collect the output files this run would write and that already exist
        if options["combined"]:
            planned = [combined_path]
        else:
            planned = [out_dir / pdf.relative_to(in_dir).with_suffix(".txt") for pdf in pdfs]
        existing = [path for path in planned if path.exists()]
        if not confirm_overwrite(self, existing, options["yes"]):
            return

        if options["combined"]:
            txt_root.mkdir(parents=True, exist_ok=True)
        else:
            out_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(f"Reading {len(pdfs)} PDF(s) from {in_dir}\n")

        combined_parts = []
        ok, failed, empty = 0, [], []

        for pdf in pdfs:
            rel = pdf.relative_to(in_dir)
            try:
                text = extract_text(pdf, options["password"])
            except Exception as e:
                failed.append((rel, str(e)))
                self.stderr.write(f"  FAIL  {rel}: {e}")
                continue

            # Little or no text usually means a scanned (image-only) PDF
            if len(PAGE_MARKER_RE.sub("", text).strip()) < 20:
                empty.append(rel)

            if options["combined"]:
                combined_parts.append(f"===== {rel} =====\n\n{text}")
            else:
                txt_path = out_dir / rel.with_suffix(".txt")
                txt_path.parent.mkdir(parents=True, exist_ok=True)
                txt_path.write_text(text, encoding="utf-8")

            ok += 1
            self.stdout.write(f"  OK    {rel}")

        if options["combined"]:
            combined_path.write_text("\n\n\n".join(combined_parts), encoding="utf-8")
            self.stdout.write(f"\nWrote combined text to {combined_path}")
        else:
            self.stdout.write(f"\nWrote text files to {out_dir}")

        self.stdout.write(f"Done: {ok} extracted, {len(failed)} failed.")
        if failed:
            self.stdout.write("\nFailed files:")
            for rel, err in failed:
                self.stdout.write(f"  - {rel}: {err}")
        if empty:
            self.stdout.write("\nThese had little or no text (likely scanned images, need OCR):")
            for rel in empty:
                self.stdout.write(f"  - {rel}")
