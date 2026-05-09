#!/usr/bin/env python3
"""Deterministic preflight for /ai-create-command."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

CODE_SPAN = re.compile(r"`([^`\n]+)`")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
PATH_TOKEN = re.compile(r"(?<![\w.-])(?:~/?|[A-Za-z0-9_./-]+/)[A-Za-z0-9_./~-]+")
STALE_TEXT = re.compile(r"TODO|FIXME|old project|old product|copy of", re.IGNORECASE)
SOURCE_ANCHOR = re.compile(r"^Source anchor:\s*(.+)$", re.MULTILINE)


def resolve_path(raw: str, base: Path = ROOT) -> Path:
    raw = raw.strip().strip("\"'")
    if raw.startswith("~"):
        return Path(os.path.expanduser(raw)).resolve()
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def looks_like_missing_path(raw: str) -> bool:
    if " " in raw or "$" in raw or "<" in raw or ">" in raw:
        return False
    if raw.startswith(("http://", "https://", "mailto:", "path/to/")):
        return False
    return "/" in raw or raw.endswith(".md")


def classify_anchor(raw: str) -> tuple[str, Path | None, str | None]:
    if not raw.strip():
        return "Missing", None, None

    candidate = resolve_path(raw)
    if candidate.is_file() and candidate.suffix == ".md":
        return "Draft", candidate, None

    if looks_like_missing_path(raw):
        return "Missing", None, f"draft path not found: {raw}"

    if "Decision: Recreate" in raw:
        match = SOURCE_ANCHOR.search(raw)
        if match:
            source = resolve_path(match.group(1))
            if source.is_file() and source.suffix == ".md":
                return "Review", source, None
            return "Missing", None, f"source anchor not found: {match.group(1)}"
        return "Review", None, None

    if "| Check | Finding | Severity |" in raw or "Decision:" in raw:
        return "Missing", None, "review anchor must contain Decision: Recreate"

    return "Intent", None, None


def path_candidates(text: str) -> set[str]:
    values: set[str] = set()
    values.update(CODE_SPAN.findall(text))
    values.update(MARKDOWN_LINK.findall(text))
    values.update(PATH_TOKEN.findall(text))
    return values


def looks_like_reference(raw: str) -> bool:
    if " " in raw or raw.startswith("path/to/"):
        return False
    if raw.startswith(("http://", "https://", "mailto:")):
        return False
    if "<" in raw or ">" in raw or "$" in raw:
        return False
    return "/" in raw or raw.startswith("~")


def reference_base(anchor: Path) -> Path:
    parts = anchor.parts
    if ".claude" in parts:
        index = parts.index(".claude")
        if index > 0 and index + 1 < len(parts) and parts[index + 1] == "commands":
            return Path(*parts[:index])
    return ROOT


def direct_references(anchor: Path, text: str) -> tuple[list[Path], list[str]]:
    base = reference_base(anchor)
    refs: list[Path] = []
    missing: list[str] = []
    for raw in sorted(path_candidates(text)):
        if not looks_like_reference(raw):
            continue
        candidate = resolve_path(raw, base)
        if candidate.exists() and candidate.is_file() and candidate.suffix == ".md":
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


def placement_hint(anchor: Path | None, raw: str) -> str:
    if anchor is not None:
        try:
            rel = anchor.relative_to(ROOT)
        except ValueError:
            return "project - outside ~/.claude"
        return "global" if rel.parts[:1] == ("commands",) else "project"
    if any(token in raw for token in ("project", "task queue", "agent", "domain path")):
        return "project"
    return "unknown - decide during intake"


def print_list(title: str, values: list[str]) -> None:
    print(f"{title}:")
    if not values:
        print("- none")
        return
    for value in values:
        print(f"- {value}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic checks for /ai-create-command."
    )
    parser.add_argument("anchor", nargs="*", help="Intent, review output, or draft command path.")
    args = parser.parse_args()

    raw = " ".join(args.anchor).strip()
    anchor_type, draft, error = classify_anchor(raw)

    if error:
        print(f"Blocked: {error}", file=sys.stderr)
        return 2

    refs: list[Path] = []
    missing: list[str] = []
    stale: list[str] = []
    lines = 0
    if draft is not None:
        text = draft.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        refs, missing = direct_references(draft, text)
        stale = stale_scan([draft, *refs])

    print("ai-create-command preflight")
    print(f"anchor_type: {anchor_type}")
    print(f"anchor: {display_path(draft) if draft else raw[:120] or 'none'}")
    print(f"draft_lines: {lines if draft else 'n/a'}")
    print(f"placement_hint: {placement_hint(draft, raw)}")
    print_list("direct_instruction_refs", [display_path(path) for path in refs])
    print_list("missing_path_refs", missing)
    print_list("stale_scan", stale)

    return 1 if missing or stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
