#!/usr/bin/env python3
"""Convert a CSV to a landscape PDF with the same name, overwriting if present."""
import subprocess
import sys
import tempfile
from pathlib import Path

from csv_to_xlsx import write_xlsx


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: csv_to_pdf.py <path/to/file.csv>")
    csv_path = Path(sys.argv[1])
    pdf_path = csv_path.with_suffix(".pdf")
    with tempfile.TemporaryDirectory() as tmp:
        xlsx_path = Path(tmp) / csv_path.with_suffix(".xlsx").name
        write_xlsx(csv_path, xlsx_path)
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(xlsx_path)],
            check=True,
        )
        (Path(tmp) / pdf_path.name).replace(pdf_path)
    print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
