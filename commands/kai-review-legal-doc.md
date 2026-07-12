---
description: Full legal-document review — orchestrates Saul (legal) and Steve (content) in parallel, with optional visual check. Not for drafting or changing legal meaning.
argument-hint: <source.md> [--written-guide <path>] [--pdf <path>] [--visual-guide <path>]
status: draft
owner: kai
model: sonnet
---

You are orchestrating a full legal-document review.

Anchor: `$ARGUMENTS` — one Markdown contract plus optional flags.

## Resolve

Parse `$ARGUMENTS`:

- `source` — required Markdown contract.
  If source is missing, stop: `Error: <source.md> is required.`
- `--written-guide` — optional; passed to Steve.
- `--pdf` — optional; triggers visual check if also `--visual-guide` present.
- `--visual-guide` — optional; triggers visual check if also `--pdf` present.

## Delegate

Read `~/.claude/commands/saul-review-legal-doc.md` and
`~/.claude/commands/steve-review-legal-doc.md`. Spawn Saul and Steve as
subagents **in parallel**, briefing each with the full source text and their
command spec.

If both `--pdf` and `--visual-guide` are provided, also spawn a third Steve
subagent following `~/.claude/commands/steve-review-legal-pdf.md`.

## Output

Merge all subagent results into exactly this block. No prose outside it.

```
Source: <path>

[0] Voice         PASS / WARN / FAIL / SKIPPED
[1] Legal refs    PASS / WARN / FAIL
[2] Completeness  PASS / WARN / FAIL
[3] Grammar       PASS / WARN / FAIL
[4] Trim          PASS / WARN / FAIL
[5] Visual        PASS / WARN / FAIL / SKIPPED

Findings:
<N>  <one-line finding>
...

Summary: <N> passed · <M> warnings · <K> failures
```

Omit [5] row if neither `--pdf` nor `--visual-guide` was provided.

## Hard rules

- Never change legal meaning or remove `human_` placeholders.
- Trim suggestions are flags only — no edits.
- Missing optional guide → SKIPPED is valid; do not invent checks.
- Never claim [5] PASS without the PDF subagent having read every page.
