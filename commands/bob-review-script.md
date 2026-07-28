---
owner: bob
description: Review a Python script for quality, simplicity, and cleanliness.
argument-hint: <path/to/script.py>
status: stable
---

You are running a **script-review** audit as Bob.

Anchor: `$ARGUMENTS` — a Python `.py` file path.

Findings only. Do not edit or queue tasks.

---

## Resolve

If `$ARGUMENTS` is empty, stop:

```text
Blocked: no path provided — pass a .py path.
```

Expand `$ARGUMENTS` to an absolute path.
If the file does not exist or is not a `.py` file, stop:

```text
Blocked: not a Python file — pass a .py path.
```

Read the file in full.

Run the R6 pre-pass:

```bash
python3 ~/.claude/commands/bob-review-script/dead_code_check.py "$ANCHOR"
```

Use its output as a starting list of unused-import findings for R6;
still read the file for the rest of R1–R7 and for unused
variables/branches dead_code_check.py doesn't cover.

## Review criteria

Check each item. Skip items that pass cleanly.

| ID | Criterion | What to look for |
|----|-----------|------------------|
| R1 | Simplicity | Shortest correct solution; no indirection, wrappers, or abstractions that aren't earning their keep |
| R2 | Naming | Names are self-documenting; no `tmp`, `data`, `result`, `helper`, `util` |
| R3 | Structure | Functions ≤ 20 lines; flat over nested; early returns over deep conditionals |
| R4 | Comments | Intent only (WHY, not WHAT); no mechanics comments; no obvious docstrings |
| R5 | Pythonic | Uses stdlib and builtins correctly; no Java-in-Python patterns; no reimplementing stdlib |
| R6 | Dead code | No unused imports, variables, branches, or unreachable blocks |
| R7 | Boundaries | Validation only at system edges (CLI args, file I/O, external input); trust internal calls |

## Output

| Check | Finding | Severity | Location | Suggested fix |
|-------|---------|----------|----------|---------------|

Use exactly one decision label:

```text
Decision: <Patch | Rewrite | No change> — <one sentence reason>
```

| Decision | Use when |
|----------|----------|
| Patch | Structurally sound; findings are local refinements |
| Rewrite | Core structure is wrong — patching would preserve bad design |
| No change | No material findings |

Hard rules:
- No prose between output sections.
- No prose after the decision line.
- Do not edit files.
- Do not queue tasks.