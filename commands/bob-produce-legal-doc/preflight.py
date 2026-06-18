#!/usr/bin/env python3
"""Resolve and validate /bob-produce-legal-doc inputs."""
from __future__ import annotations

import argparse
import json
import shutil
import tomllib
from pathlib import Path


REQUIRED_PROFILE_KEYS = (
    ("profile", "version"),
    ("render", "command"),
    ("verification", "page_size"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def find_project_root(source: Path) -> Path:
    directories = (source.parent, *source.parents)
    for directory in directories:
        if (directory / ".git").exists():
            return directory
    candidates = [path for path in directories if (path / "README_AI.md").exists()]
    return candidates[-1] if candidates else source.parent


def find_profile(source: Path) -> Path | None:
    for directory in (source.parent, *source.parents):
        candidate = directory / "legal_print_profile.toml"
        if candidate.is_file():
            return candidate
    return None


def nested(mapping: dict, path: tuple[str, ...]):
    current = mapping
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def resolve_project_path(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def load_profile(path: Path | None, blocked: list[str]) -> dict:
    if path is None:
        blocked.append("legal_print_profile.toml not found; scaffold requires confirmed directory")
        return {}
    if not path.is_file():
        blocked.append(f"profile not found: {path}")
        return {}
    try:
        profile = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        blocked.append(f"invalid profile: {error}")
        return {}
    for key_path in REQUIRED_PROFILE_KEYS:
        if nested(profile, key_path) in (None, "", []):
            blocked.append("profile missing " + ".".join(key_path))
    return profile


def find_document(profile: dict, root: Path, source: Path) -> tuple[str | None, dict]:
    for document_id, config in profile.get("documents", {}).items():
        if resolve_project_path(root, config.get("source", "")) == source:
            return document_id, config
    return None, {}


def filled_fields(pdf: Path) -> list[str]:
    if not pdf.is_file():
        return []
    try:
        import fitz
    except ImportError:
        return ["unknown: PyMuPDF unavailable"]
    names = []
    try:
        with fitz.open(pdf) as document:
            for page in document:
                for widget in page.widgets() or []:
                    value = str(widget.field_value or "").strip()
                    if value and value.lower() not in {"off", "false", "no", "0"}:
                        names.append(widget.field_name or "unnamed")
    except (RuntimeError, ValueError):
        return ["unknown: output is not a readable PDF"]
    return names


def resolve_output(args: argparse.Namespace, root: Path, document: dict) -> Path:
    if args.output:
        return args.output.expanduser().resolve()
    if document.get("output"):
        return resolve_project_path(root, document["output"])
    return args.source.expanduser().resolve().with_suffix(".pdf")


def validate_render(profile: dict, root: Path, blocked: list[str]) -> tuple[list[str], Path]:
    render = profile.get("render", {})
    command = render.get("command", [])
    valid = isinstance(command, list) and all(isinstance(part, str) and part for part in command)
    if command and not valid:
        blocked.append("render.command must be a non-empty TOML string array")
        command = []
    working_directory = resolve_project_path(root, render.get("working_directory", "."))
    if profile and not working_directory.is_dir():
        blocked.append(f"render working directory not found: {working_directory}")
    return command, working_directory


def validate_tools(profile: dict, blocked: list[str]) -> None:
    required = profile.get("tools", {}).get("required", [])
    missing = [tool for tool in required if shutil.which(tool) is None]
    if missing:
        blocked.append("missing required tools: " + ", ".join(missing))


def resolve_references(profile: dict, root: Path, blocked: list[str]) -> list[dict]:
    groups = (
        ("context", profile.get("project", {}).get("context_files", [])),
        ("brand", profile.get("brand", {}).get("references", [])),
        ("visual", profile.get("brand", {}).get("visual_references", [])),
        ("style", profile.get("render", {}).get("style_files", [])),
    )
    references = []
    for group, values in groups:
        for raw in values:
            path = resolve_project_path(root, raw)
            references.append({"type": group, "path": str(path)})
            if not path.is_file():
                blocked.append(f"missing {group} reference: {path}")
    return references


def output_state(output: Path, completed: list[str], inputs: list[Path]) -> str:
    if completed:
        return "completed"
    if not output.is_file():
        return "missing"
    mtimes = [path.stat().st_mtime for path in inputs if path and path.is_file()]
    if not mtimes:
        return "blank_stale"
    newest_input = max(mtimes)
    return "blank_fresh" if output.stat().st_mtime >= newest_input else "blank_stale"


def build_payload(args: argparse.Namespace) -> dict:
    source = args.source.expanduser().resolve()
    blocked = []
    validate_source(source, blocked)
    profile_path = args.profile.expanduser().resolve() if args.profile else find_profile(source)
    profile = load_profile(profile_path, blocked)
    root = find_project_root(source)
    document_id, document, output, completed = resolve_document(args, source, profile, root, blocked)
    command, working_directory = validate_render(profile, root, blocked)
    validate_tools(profile, blocked)
    references = resolve_references(profile, root, blocked)
    inputs = [source, profile_path, *(Path(item["path"]) for item in references if item["type"] == "style")]
    return make_payload(
        source, output, profile_path, root, document_id, document,
        command, working_directory, output_state(output, completed, inputs),
        references, blocked,
    )


def resolve_document(args, source, profile, root, blocked):
    document_id, document = find_document(profile, root, source)
    if profile.get("documents") and document_id is None:
        blocked.append("source is not registered in profile documents")
    output = resolve_output(args, root, document)
    completed = filled_fields(output)
    if completed:
        blocked.append("output contains completed form values; use --output with a new path: " + ", ".join(completed))
    return document_id, document, output, completed


def validate_source(source: Path, blocked: list[str]) -> None:
    if not source.is_file() or source.suffix.lower() != ".md":
        blocked.append(f"approved Markdown source not found: {source}")


def make_payload(source, output, profile, root, document_id, document, command, working_directory, state, references, blocked):
    return {
        "status": "blocked" if blocked else "ready",
        "source": str(source),
        "output": str(output),
        "output_state": state,
        "profile": str(profile) if profile else None,
        "project_root": str(root),
        "document_id": document_id,
        "document": document,
        "references": references,
        "render_working_directory": str(working_directory),
        "render_command": command,
        "blocked": blocked,
    }


def main() -> int:
    payload = build_payload(parse_args())
    print(json.dumps(payload, indent=2))
    return 2 if payload["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
