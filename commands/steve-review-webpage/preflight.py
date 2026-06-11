#!/usr/bin/env python3
"""Preflight checks for /steve-review-webpage.

Usage: python3 preflight.py <html_file> <written_guide> <visual_guide> [content_file]

Exits 0 on success. Prints Blocked: <reason> and exits 2 on failure.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

VENV_PYTHON = Path.home() / ".claude/lib/.venv/bin/python"


def resolve(raw: str) -> Path:
    p = Path(raw).expanduser()
    return p.resolve() if not p.is_absolute() else p


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 3:
        print(
            "Missing: html_file written_guide visual_guide — "
            "usage: /steve-review-webpage <html_file> <written_guide> <visual_guide> [content_file]",
            file=sys.stderr,
        )
        return 2

    html_file, written_guide, visual_guide = args[0], args[1], args[2]
    content_file = args[3] if len(args) > 3 else None

    checks = [
        (html_file, "html_file"),
        (written_guide, "written_guide"),
        (visual_guide, "visual_guide"),
    ]
    if content_file:
        checks.append((content_file, "content_file"))

    for raw, label in checks:
        path = resolve(raw)
        if not path.exists():
            print(f"Blocked: {label} not found — {path}", file=sys.stderr)
            return 2

    if not VENV_PYTHON.exists():
        print(
            f"Blocked: venv not found — run: bash ~/.claude/lib/bootstrap.sh",
            file=sys.stderr,
        )
        return 2

    html_abs = resolve(html_file)
    screenshot_path = html_abs.parent / "_review_desktop.png"

    print("steve-review-webpage preflight")
    print(f"html_file: {html_abs}")
    print(f"written_guide: {resolve(written_guide)}")
    print(f"visual_guide: {resolve(visual_guide)}")
    print(f"content_file: {resolve(content_file) if content_file else 'none'}")
    print(f"screenshot_path: {screenshot_path}")
    print(f"screenshot_exists: {'yes — will overwrite' if screenshot_path.exists() else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
