#!/usr/bin/env python3
"""Starter project-local legal Markdown to PDF renderer."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        parser.error(f"source not found: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    tools = Path(__file__).resolve().parent
    subprocess.run(
        [
            "pandoc", str(source), "-o", str(output),
            "--pdf-engine=xelatex",
            "--include-in-header", str(tools / "print.tex"),
            "--lua-filter", str(tools / "forms.lua"),
            "--variable=papersize:a4",
            "--variable=geometry:top=18mm",
            "--variable=geometry:bottom=18mm",
            "--variable=geometry:left=17mm",
            "--variable=geometry:right=17mm",
        ],
        check=True,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
