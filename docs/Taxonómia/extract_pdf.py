#!/usr/bin/env python3
"""
Extract text from every PDF in a folder.

Usage:
    python extract_pdf_text.py /path/to/pdfs
    python extract_pdf_text.py /path/to/pdfs -o /path/to/output -r
    python extract_pdf_text.py /path/to/pdfs --combined all_text.txt

Requires:
    pip install pypdf
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("Missing dependency: run  pip install pypdf")


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from PDFs in a folder.")
    parser.add_argument("folder", type=Path, help="Folder containing PDFs")
    parser.add_argument("-o", "--output", type=Path,
                        help="Output folder for .txt files (default: <folder>/extracted_text)")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Also search subfolders")
    parser.add_argument("--combined", type=Path,
                        help="Write everything into this single .txt file instead")
    parser.add_argument("--password", help="Password for encrypted PDFs")
    args = parser.parse_args()

    if not args.folder.is_dir():
        sys.exit(f"Not a folder: {args.folder}")

    pattern = "**/*" if args.recursive else "*"
    pdfs = sorted(p for p in args.folder.glob(pattern)
                  if p.is_file() and p.suffix.lower() == ".pdf")
    if not pdfs:
        sys.exit(f"No PDFs found in {args.folder}")

    out_dir = args.output or args.folder / "extracted_text"
    if not args.combined:
        out_dir.mkdir(parents=True, exist_ok=True)

    combined_parts = []
    ok, failed, empty = 0, [], []

    for pdf in pdfs:
        rel = pdf.relative_to(args.folder)
        try:
            text = extract_text(pdf, args.password)
        except Exception as e:
            failed.append((rel, str(e)))
            print(f"  FAIL  {rel}: {e}")
            continue

        # Little or no text usually means a scanned (image-only) PDF
        if len(text.replace("--- Page", "").strip()) < 20:
            empty.append(rel)

        if args.combined:
            combined_parts.append(f"===== {rel} =====\n\n{text}")
        else:
            txt_path = out_dir / rel.with_suffix(".txt")
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            txt_path.write_text(text, encoding="utf-8")

        ok += 1
        print(f"  OK    {rel}")

    if args.combined:
        args.combined.write_text("\n\n\n".join(combined_parts), encoding="utf-8")
        print(f"\nWrote combined text to {args.combined}")
    else:
        print(f"\nWrote text files to {out_dir}")

    print(f"Done: {ok} extracted, {len(failed)} failed.")
    if empty:
        print("\nThese had little or no text (likely scanned images, need OCR):")
        for rel in empty:
            print(f"  - {rel}")


if __name__ == "__main__":
    main()