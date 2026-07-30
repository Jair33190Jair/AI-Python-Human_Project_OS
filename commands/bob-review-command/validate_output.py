#!/usr/bin/env python3
"""Deterministic Final Validation check for /bob-review-command output.

Reads a drafted review report (stdin or a file path) and checks the
output contract: decision line, table headers, and metrics format.
Exit 0 and print "ok" if valid; otherwise print each violation and
exit 1.
"""

from __future__ import annotations

import argparse
import re
import sys

DECISION_RE = re.compile(r"^Decision: (Patch|Recreate|No change) — .+$", re.MULTILINE)
FINDINGS_HEADER = "| Check | Finding | Severity | Location | Suggested fix |"
S12_HEADER = "| Step | Effort | Frequency | Impact | Verdict |"
CONTEXT_RE = re.compile(r"^Context load: `(Light|Moderate|Heavy)` — .+$", re.MULTILINE)
CLARITY_RE = re.compile(r"^Instruction clarity: `(Clear|Mixed|Unclear)` — .+$", re.MULTILINE)


def validate(text: str) -> list[str]:
    errors = []
    if FINDINGS_HEADER not in text:
        errors.append(f"missing findings table header: {FINDINGS_HEADER}")
    if not DECISION_RE.search(text):
        errors.append("missing or malformed Decision line")
    if not CONTEXT_RE.search(text):
        errors.append("missing or malformed Context load metric")
    if not CLARITY_RE.search(text):
        errors.append("missing or malformed Instruction clarity metric")
    if "S12" in text and S12_HEADER not in text:
        errors.append(f"S12 referenced but missing table header: {S12_HEADER}")
    decision_match = DECISION_RE.search(text)
    if decision_match and decision_match.group(1) == "Recreate":
        if "/bob-create-command" not in text and "ai questions" not in text.lower():
            errors.append(
                "Recreate decision missing handoff prompt "
                "(focused AI questions or /bob-create-command)"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate /bob-review-command output.")
    parser.add_argument("report", nargs="?", help="Path to drafted report; omit to read stdin.")
    args = parser.parse_args()

    text = open(args.report, encoding="utf-8").read() if args.report else sys.stdin.read()
    errors = validate(text)

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
