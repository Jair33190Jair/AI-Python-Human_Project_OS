#!/usr/bin/env python3
"""Compress scanned PDFs with the cross-project archive profile."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def format_size(size_bytes: int) -> str:
    return f"{size_bytes / 1024 / 1024:.1f} MB"


def ghostscript_command(input_pdf: Path, output_pdf: Path) -> list[str]:
    return [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-r150",
        f"-sOutputFile={output_pdf}",
        str(input_pdf),
    ]


def compress_pdf(input_pdf: Path, output_pdf: Path) -> None:
    if shutil.which("gs") is None:
        raise SystemExit("Ghostscript not found: install `gs` to compress PDFs.")
    if not input_pdf.exists():
        raise SystemExit(f"Input PDF not found: {input_pdf}")
    if input_pdf.resolve() == output_pdf.resolve():
        raise SystemExit("Input and output must differ; use --in-place instead.")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(ghostscript_command(input_pdf, output_pdf), check=True)


def compress_in_place(input_pdf: Path, backup_suffix: str) -> Path:
    backup_pdf = input_pdf.with_name(input_pdf.stem + backup_suffix + input_pdf.suffix)
    if backup_pdf.exists():
        raise SystemExit(f"Backup already exists: {backup_pdf}")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        temp_pdf = Path(tmp.name)

    try:
        compress_pdf(input_pdf, temp_pdf)
        input_pdf.rename(backup_pdf)
        temp_pdf.replace(input_pdf)
    finally:
        temp_pdf.unlink(missing_ok=True)

    return backup_pdf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compress scanned PDFs with a readable 150 DPI archive profile."
    )
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", nargs="?", type=Path)
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="replace input and keep a backup beside it",
    )
    parser.add_argument(
        "--backup-suffix",
        default=".backup",
        help="suffix used by --in-place before .pdf",
    )
    args = parser.parse_args(argv)

    input_pdf = args.input_pdf
    before = input_pdf.stat().st_size if input_pdf.exists() else 0

    if args.in_place:
        if args.output_pdf:
            parser.error("output_pdf cannot be used with --in-place")
        backup_pdf = compress_in_place(input_pdf, args.backup_suffix)
        output_pdf = input_pdf
        print(f"Backup: {backup_pdf}")
    else:
        if not args.output_pdf:
            parser.error("pass output_pdf or --in-place")
        output_pdf = args.output_pdf
        compress_pdf(input_pdf, output_pdf)

    after = output_pdf.stat().st_size
    print(f"Input: {input_pdf}")
    print(f"Output: {output_pdf}")
    print(f"Size: {format_size(before)} -> {format_size(after)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
