#!/usr/bin/env python3
"""
Live smoke checks for lib/fetch.py.

Requires network access. Exits non-zero on extraction regressions.
"""
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PYTHON = HERE / ".venv" / "bin" / "python"
FETCH = HERE / "fetch.py"

CASES = [
    (
        "fedlex-dsg",
        "https://www.fedlex.admin.ch/eli/cc/2022/491/de",
        r"^## (?:Art\.|Anhang)",
        79,
    ),
    (
        "eurlex-gdpr",
        "https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng",
        r"^## Article",
        99,
    ),
    (
        "basel-gesg",
        "https://www.gesetzessammlung.bs.ch/app/de/texts_of_law/300.100",
        r"^#### §",
        81,
    ),
    (
        "ticino-regpsi",
        "https://m3.ti.ch/CAN/RLeggi/public/index.php/raccolta-leggi/pdfatto/atto/12123",
        r"^## Art\.",
        21,
    ),
]


def main() -> int:
    failed = False
    for name, url, pattern, expected in CASES:
        proc = subprocess.run(
            [str(PYTHON), str(FETCH), url],
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            print(f"{name}: exit {proc.returncode}: {proc.stderr.strip()}")
            failed = True
            continue

        count = len(re.findall(pattern, proc.stdout, re.MULTILINE))
        status = "ok" if count == expected else "FAIL"
        print(f"{name}: {status} ({count}/{expected})")
        failed = failed or count != expected

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
