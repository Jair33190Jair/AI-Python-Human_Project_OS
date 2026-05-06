#!/usr/bin/env python3
"""Deterministic preflight for /ai-review-skill."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUPPORT_RUBRIC = ROOT / "commands/ai-review-skill/rubric.md"

PATH_TOKEN = re.compile(r"(?<![\w.-])(?:~/?|[A-Za-z0-9_./-]+/)[A-Za-z0-9_./~-]+")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
STALE_TEXT = re.compile(r"Findings only,\S+|TODO|FIXME|old project|old product", re.IGNORECASE)


def resolve_path(raw: str, base: Path) -> Path:
    raw = raw.strip().strip("\"'")
    if raw.startswith("~"):
        return Path(os.path.expanduser(raw)).resolve()
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def resolve_anchor(raw: str) -> tuple[Path | None, str | None]:
    path = resolve_path(raw, ROOT)
    if path.is_dir():
        skill = path / "SKILL.md"
        return (skill if skill.exists() else None, f"folder missing SKILL.md: {path}")
    if path.is_file():
        return path, None
    return None, f"instruction anchor not found: {raw}"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def reference_base(anchor: Path) -> Path:
    try:
        anchor.relative_to(ROOT)
        return ROOT
    except ValueError:
        pass

    parts = anchor.parts
    if ".claude" in parts:
        index = parts.index(".claude")
        if index > 0 and index + 1 < len(parts) and parts[index + 1] == "commands":
            return Path(*parts[:index])
    return ROOT


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def context_label(files_loaded: int, chain_depth: int, anchor_lines: int) -> str:
    if files_loaded <= 2 and chain_depth <= 1 and anchor_lines <= 100:
        return "Light"
    if files_loaded <= 5 or chain_depth == 2 or 100 <= anchor_lines <= 200:
        return "Moderate"
    return "Heavy"


def path_candidates(text: str) -> set[str]:
    values: set[str] = set()
    for match in CODE_SPAN.findall(text):
        values.add(match)
    for match in MARKDOWN_LINK.findall(text):
        values.add(match)
    for match in PATH_TOKEN.findall(text):
        values.add(match)
    return values


def looks_like_path(value: str) -> bool:
    if " " in value or value.startswith("path/to/"):
        return False
    if value.startswith(("http://", "https://", "mailto:")):
        return False
    if "<" in value or ">" in value or "$" in value:
        return False
    if value in {"SKILL.md", "README.md"}:
        return False
    return "/" in value or value.startswith("~")


def instruction_file(path: Path) -> bool:
    return path.suffix == ".md" and path.exists() and path.is_file()


def direct_references(anchor: Path, text: str, base: Path) -> tuple[list[Path], list[str]]:
    refs: list[Path] = []
    missing: list[str] = []
    for raw in sorted(path_candidates(text)):
        if not looks_like_path(raw):
            continue
        candidate = resolve_path(raw, base)
        if instruction_file(candidate):
            refs.append(candidate)
        elif not candidate.exists() and raw.endswith((".md", ".py", ".json", ".yaml", ".yml")):
            missing.append(raw)
    return sorted(set(refs) - {anchor}), missing


def stale_scan(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if STALE_TEXT.search(line):
                findings.append(f"{display_path(path)}:{number}: {line.strip()}")
    return findings


def print_list(title: str, values: list[str]) -> None:
    print(f"{title}:")
    if not values:
        print("- none")
        return
    for value in values:
        print(f"- {value}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic checks for /ai-review-skill."
    )
    parser.add_argument("anchor", help="Skill/command file or skill folder.")
    args = parser.parse_args()

    anchor, error = resolve_anchor(args.anchor)
    if error:
        print(f"Blocked: {error}", file=sys.stderr)
        return 2

    assert anchor is not None
    text = anchor.read_text(encoding="utf-8")
    base = reference_base(anchor)
    refs, missing = direct_references(anchor, text, base)
    files = [anchor, SUPPORT_RUBRIC, *refs]
    files = sorted(set(files))
    anchor_lines = line_count(anchor)
    label = context_label(len(files), 1 if len(files) > 1 else 0, anchor_lines)
    stale = stale_scan([anchor, *refs])

    print("ai-review-skill preflight")
    print(f"anchor: {display_path(anchor)}")
    print(f"anchor_lines: {anchor_lines}")
    print(f"support_rubric: {'ok' if SUPPORT_RUBRIC.exists() else 'missing'}")
    print(f"context_load: {label} — {len(files)} files loaded, chain depth 1")
    print_list("direct_instruction_refs", [display_path(path) for path in refs])
    print_list("missing_path_refs", missing)
    print_list("stale_scan", stale)

    return 1 if missing or stale or not SUPPORT_RUBRIC.exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
