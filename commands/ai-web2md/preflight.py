#!/usr/bin/env python3
"""Deterministic preflight for /ai-web2md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / "helpers/.venv/bin/python"
FETCH = ROOT / "helpers/fetch.py"
BOOTSTRAP = ROOT / "helpers/bootstrap.sh"


def valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate URL and helper paths for /ai-web2md."
    )
    parser.add_argument("url", nargs="?", help="URL to fetch.")
    args = parser.parse_args()

    url = (args.url or "").strip()
    if not url:
        print("Blocked: missing URL — pass one http(s) URL.", file=sys.stderr)
        return 2
    if not valid_url(url):
        print(f"Blocked: invalid URL — {url}", file=sys.stderr)
        return 2

    missing = [path for path in (PYTHON, FETCH) if not path.exists()]
    if missing:
        print("Blocked: helper environment missing.", file=sys.stderr)
        for path in missing:
            print(f"- {path}", file=sys.stderr)
        print(f"Run: {BOOTSTRAP}", file=sys.stderr)
        return 2

    print("ai-web2md preflight")
    print(f"url: {url}")
    print(f"python: {PYTHON}")
    print(f"fetch: {FETCH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
