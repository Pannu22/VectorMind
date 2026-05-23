"""Experiment: recursively parse PDFs and print extraction summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

from vectormind import PDFParseError, PDFParser


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively parse PDFs with VectorMind's experimental PDF text parser."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        help="Directory to scan recursively.",
    )
    parser.add_argument(
        "--preview-chars",
        default=0,
        type=int,
        help="Print the first N extracted characters for each PDF.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    directory = args.directory.expanduser()

    if not directory.exists():
        print(f"Directory not found: {directory}")
        return 1
    if not directory.is_dir():
        print(f"Path is not a directory: {directory}")
        return 1

    pdf_paths = sorted(directory.rglob("*.pdf"))
    if not pdf_paths:
        print(f"No PDF files found under: {directory}")
        return 0

    parser = PDFParser()
    parsed_count = 0
    failed_count = 0

    for pdf_path in pdf_paths:
        try:
            document = parser.parse(pdf_path)
        except (FileNotFoundError, PDFParseError) as exc:
            failed_count += 1
            print(f"[FAIL] {pdf_path}: {exc}")
            continue

        parsed_count += 1
        extracted_chars = sum(len(page.text) for page in document.pages)
        print(
            f"[OK] {pdf_path}: {document.page_count} pages, {extracted_chars:,} chars"
        )

        if args.preview_chars > 0:
            preview = "\n".join(page.text for page in document.pages)
            print(preview[: args.preview_chars].strip())
            print("-" * 80)

    print(f"Parsed {parsed_count} PDF(s); failed {failed_count}.")
    return 0 if failed_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
