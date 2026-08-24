#!/usr/bin/env python3
"""Convert an XLSX to a PDF with the same name, overwriting if present."""
import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: xlsx_to_pdf.py <path/to/file.xlsx>")
    xlsx_path = Path(sys.argv[1])
    subprocess.run(
        [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(xlsx_path.parent),
            str(xlsx_path),
        ],
        check=True,
    )
    print(f"wrote {xlsx_path.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
