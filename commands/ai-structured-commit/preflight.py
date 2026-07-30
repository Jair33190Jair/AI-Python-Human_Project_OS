#!/usr/bin/env python3
"""Resolve and validate /ai-structured-commit inputs."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

TASK_QUEUE_TEMPLATE = """---
owner: kai
---

# Cross-agent todos queue

Async inbox for handoffs between agents.
Newest on top. Done/obsolete → `dev_tasks_closed.md`.

### Schema

```
## TASK-NNNN — <short title>
- Date: MM-YY
- Requested by: <agent or "user">
- Target agent: <agent>
- What: <one sentence; link to file if detail lives there>
- Status: open
- Tag: <optional>
- Depends on: <optional>
```

### Status

`open` · `done` · `obsolete`
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", nargs="?", default=".", type=Path)
    parser.add_argument(
        "--init-task-queue",
        action="store_true",
        help="create dev_tasks_open.md at the repo root if it doesn't exist",
    )
    parser.add_argument(
        "--verify-staged",
        nargs="*",
        default=None,
        metavar="FILE",
        help="expected staged file list; exit non-zero on any mismatch",
    )
    return parser.parse_args()


def run(args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, check=False
    )
    return result.returncode, (result.stdout or result.stderr).strip()


def find_repo_root(path: Path, blocked: list[str]) -> Path | None:
    code, out = run(["git", "rev-parse", "--show-toplevel"], cwd=path)
    if code != 0:
        blocked.append(f"not a git repository: {path}")
        return None
    return Path(out)


def find_pre_commit_hook(root: Path) -> str | None:
    code, hooks_path = run(["git", "config", "core.hooksPath"], cwd=root)
    candidates = []
    if code == 0 and hooks_path:
        candidates.append(Path(hooks_path))
        if not Path(hooks_path).is_absolute():
            candidates.append(root / hooks_path)
    candidates.append(root / ".git" / "hooks")
    for hooks_dir in candidates:
        hook = hooks_dir / "pre-commit"
        if hook.is_file():
            return str(hook)
    return None


def find_first_existing(root: Path, names: tuple[str, ...]) -> str | None:
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return str(candidate)
    return None


def init_task_queue(root: Path, task_queue: str | None) -> str:
    if task_queue is not None:
        return task_queue
    path = root / "dev_tasks_open.md"
    path.write_text(TASK_QUEUE_TEMPLATE)
    return str(path)


def verify_staged(root: Path, expected: list[str]) -> dict:
    code, out = run(["git", "diff", "--cached", "--name-only"], cwd=root)
    actual = sorted(line for line in out.splitlines() if line.strip())
    expected_sorted = sorted(expected)
    missing = sorted(set(expected_sorted) - set(actual))
    unexpected = sorted(set(actual) - set(expected_sorted))
    return {
        "status": "match" if not missing and not unexpected else "mismatch",
        "expected": expected_sorted,
        "actual": actual,
        "missing": missing,
        "unexpected": unexpected,
    }


def build_payload(args: argparse.Namespace) -> dict:
    blocked: list[str] = []
    resolved_path = args.repo_path.resolve()
    root = find_repo_root(resolved_path, blocked)

    diff: list[str] = []
    task_queue = None
    hook = None

    if root is not None:
        code, status = run(["git", "status", "--porcelain", "-uall"], cwd=root)
        diff = [line for line in status.splitlines() if line.strip()]
        if not diff:
            blocked.append("no pending changes — nothing to split")

        task_queue = find_first_existing(
            root, ("dev_tasks_open.md", "tasks_open.md")
        )
        if args.init_task_queue:
            task_queue = init_task_queue(root, task_queue)
        hook = find_pre_commit_hook(root)

    return {
        "status": "blocked" if blocked else "ready",
        "repo_root": str(root) if root else None,
        "diff_entry_count": len(diff),
        "diff": diff,
        "task_queue": task_queue,
        "task_queue_exists": task_queue is not None,
        "pre_commit_hook": hook,
        "blocked": blocked,
    }


def main() -> int:
    args = parse_args()

    if args.verify_staged is not None:
        resolved_path = args.repo_path.resolve()
        blocked: list[str] = []
        root = find_repo_root(resolved_path, blocked)
        if root is None:
            print(json.dumps({"status": "blocked", "blocked": blocked}, indent=2))
            return 2
        result = verify_staged(root, args.verify_staged)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "match" else 2

    payload = build_payload(args)
    print(json.dumps(payload, indent=2))
    return 2 if payload["blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
