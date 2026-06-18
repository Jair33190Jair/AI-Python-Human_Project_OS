#!/usr/bin/env python3
"""Run deterministic legal-PDF checks and generate page previews."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

try:
    import fitz
except ImportError as error:
    raise SystemExit("PyMuPDF is required for legal PDF verification") from error


A4_POINTS = (595.28, 841.89)
BLANK_VALUES = {"", "off", "false", "no", "0"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--preview-dir", type=Path)
    return parser.parse_args()


def find_project_root(source: Path) -> Path:
    for directory in (source.parent, *source.parents):
        if (directory / ".git").exists():
            return directory
    return source.parent


def resolve_project_path(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def validate_inputs(pdf: Path, profile: Path, source: Path) -> list[str]:
    failures = []
    for label, path in (("PDF", pdf), ("profile", profile), ("source", source)):
        if not path.is_file():
            failures.append(f"{label} not found: {path}")
    for tool in ("pdffonts", "pdftoppm"):
        if shutil.which(tool) is None:
            failures.append(f"required verification tool not found: {tool}")
    return failures


def load_profile(path: Path) -> tuple[dict, list[str]]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), []
    except (OSError, tomllib.TOMLDecodeError) as error:
        return {}, [f"invalid profile: {error}"]


def find_document(profile: dict, source: Path) -> dict:
    root = find_project_root(source)
    for config in profile.get("documents", {}).values():
        if resolve_project_path(root, config.get("source", "")) == source:
            return config
    return {}


def check_page_size(page, number: int, verification: dict, failures: list[str]) -> None:
    if verification.get("page_size", "a4").lower() != "a4":
        return
    width, height = page.rect.width, page.rect.height
    if abs(width - A4_POINTS[0]) > 2 or abs(height - A4_POINTS[1]) > 2:
        failures.append(f"page {number} is not A4: {width:.2f} x {height:.2f}")


def check_margins(page, number: int, page_profile: dict, failures: list[str]) -> None:
    left = float(page_profile.get("margin_left_mm", 0)) * 72 / 25.4
    right = float(page_profile.get("margin_right_mm", 0)) * 72 / 25.4
    for block in page.get_text("blocks"):
        text = str(block[4]).strip()
        if text and not text.isdigit() and (block[0] < left - 8 or block[2] > page.rect.width - right + 8):
            failures.append(f"page {number} text exceeds configured horizontal margins")
            return


def collect_widgets(page, number: int, failures: list[str]) -> tuple[list[str], list[str]]:
    names, populated = [], []
    for widget in page.widgets() or []:
        name = widget.field_name or ""
        if not name:
            failures.append(f"page {number} contains an unnamed form field")
        if not page.rect.contains(widget.rect):
            failures.append(f"page {number} form field is clipped: {name or 'unnamed'}")
        names.append(name)
        value = str(widget.field_value or "").strip()
        if value.lower() not in BLANK_VALUES:
            populated.append(name)
    return names, populated


def inspect_pdf(pdf: Path, profile: dict, document_config: dict, failures: list[str]):
    verification = profile.get("verification", {})
    fields, populated, text_parts = [], [], []
    with fitz.open(pdf) as document:
        pages = len(document)
        if not pages:
            failures.append("PDF has no pages")
        for number, page in enumerate(document, 1):
            check_page_size(page, number, verification, failures)
            check_margins(page, number, profile.get("page", {}), failures)
            text_parts.append(page.get_text())
            page_fields, page_populated = collect_widgets(page, number, failures)
            fields.extend(page_fields)
            populated.extend(page_populated)
        required = document_config.get("require_acroform", verification.get("require_acroform", False))
        if required and not document.is_form_pdf:
            failures.append("profile requires an AcroForm but none exists")
    return pages, fields, populated, "\n".join(text_parts)


def check_fields(fields: list[str], required: list[str], failures: list[str]) -> None:
    duplicates = sorted(name for name, count in Counter(fields).items() if count > 1)
    invalid = sorted(name for name in fields if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name))
    missing = sorted(set(required) - set(fields))
    if duplicates:
        failures.append("duplicate form field names: " + ", ".join(duplicates))
    if invalid:
        failures.append("non-portable form field names: " + ", ".join(invalid))
    if missing:
        failures.append("required form fields missing: " + ", ".join(missing))


def check_text(text: str, verification: dict, failures: list[str]) -> None:
    if not text.strip():
        failures.append("PDF has no parseable text")
    patterns = verification.get("unresolved_patterns", [r"human_[A-Za-z0-9_]+", r"PDF_FIELD_"])
    for pattern in patterns:
        if re.search(pattern, text):
            failures.append(f"unresolved placeholder pattern found: {pattern}")
    for phrase in verification.get("forbidden_text", []):
        if phrase and phrase in text:
            failures.append(f"forbidden internal text found: {phrase}")


def check_fonts(pdf: Path, required: list[str], failures: list[str]) -> None:
    completed = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True, check=False)
    if completed.returncode:
        failures.append("pdffonts could not inspect the PDF")
        return
    for font in required:
        if font.lower() not in completed.stdout.lower():
            failures.append(f"required embedded font not found: {font}")
    for line in completed.stdout.splitlines()[2:]:
        match = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        if match and match.group(1) != "yes":
            failures.append("font is not embedded: " + line.strip())


def render_previews(pdf: Path, directory: Path | None, pages: int, failures: list[str]) -> list[str]:
    preview_dir = directory or Path(tempfile.mkdtemp(prefix="legal-pdf-preview-"))
    preview_dir.mkdir(parents=True, exist_ok=True)
    prefix = preview_dir / pdf.stem
    completed = subprocess.run(["pdftoppm", "-png", "-r", "130", str(pdf), str(prefix)], check=False)
    previews = sorted(str(path) for path in preview_dir.glob(pdf.stem + "-*.png"))
    if completed.returncode:
        failures.append("pdftoppm could not render page previews")
    elif len(previews) != pages:
        failures.append(f"preview count {len(previews)} does not match page count {pages}")
    return previews


def inspect_registered_pdf(pdf, profile, document_config, failures):
    try:
        return inspect_pdf(pdf, profile, document_config, failures)
    except (RuntimeError, ValueError) as error:
        failures.append(f"unreadable PDF: {error}")
        return None


def verify(args: argparse.Namespace) -> tuple[dict, int]:
    pdf, profile_path, source = (path.expanduser().resolve() for path in (args.pdf, args.profile, args.source))
    if failures := validate_inputs(pdf, profile_path, source):
        return {"status": "fail", "failures": failures}, 2
    profile, failures = load_profile(profile_path)
    if failures:
        return {"status": "fail", "failures": failures}, 2
    document_config = find_document(profile, source)
    if profile.get("documents") and not document_config:
        return {"status": "fail", "failures": ["source is not registered in profile documents"]}, 2
    inspection = inspect_registered_pdf(pdf, profile, document_config, failures)
    if inspection is None:
        return {"status": "fail", "failures": failures}, 2
    pages, fields, populated, text = inspection
    check_fields(fields, document_config.get("required_fields", []), failures)
    check_text(text, profile.get("verification", {}), failures)
    check_fonts(pdf, profile.get("fonts", {}).get("required_pdf_fonts", []), failures)
    previews = render_previews(pdf, args.preview_dir, pages, failures)
    payload = {"status": "fail" if failures else "pass", "pdf": str(pdf), "pages": pages, "field_count": len(fields), "populated_fields": populated, "preview_files": previews, "failures": failures, "warnings": []}
    return payload, 1 if failures else 0


def main() -> int:
    payload, exit_code = verify(parse_args())
    print(json.dumps(payload, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
