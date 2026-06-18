#!/usr/bin/env python3
"""Install the starter legal-PDF profile and project tool directory."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def output_map(target: Path) -> dict[Path, Path]:
    templates = Path(__file__).resolve().parent / "templates"
    return {
        templates / "legal_print_profile.toml": target / "legal_print_profile.toml",
        templates / "tools/legal_pdf/README.md": target / "tools/legal_pdf/README.md",
        templates / "tools/legal_pdf/render.py": target / "tools/legal_pdf/render.py",
        templates / "tools/legal_pdf/print.tex": target / "tools/legal_pdf/print.tex",
        templates / "tools/legal_pdf/forms.lua": target / "tools/legal_pdf/forms.lua",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("legal_doc_dir", type=Path)
    args = parser.parse_args()
    target = args.legal_doc_dir.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    outputs = output_map(target)
    existing = [str(path) for path in outputs.values() if path.exists()]
    if existing:
        raise SystemExit("refusing to overwrite: " + ", ".join(existing))
    for source, destination in outputs.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        print(f"Created: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
