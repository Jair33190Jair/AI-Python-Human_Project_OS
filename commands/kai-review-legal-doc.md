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
- `--pdf` — optional; triggers visual check.
- `--visual-guide` — optional; passed to the visual check. Without it, the
  PDF command uses its default guide.

For a Maindi source under
`project/040_compliance/legal_docs/docs/02_platform-psychologist/` or
`project/040_compliance/legal_docs/docs/03_psychologist-patient/`, default
`--written-guide` to
`project/020_business/brand/content_guide_written.md`. An explicit flag wins.

Set `review_only = true` when the source filename starts with `051_`.

## Bundle context

If source is under `project/040_compliance/legal_docs/docs/`, read before
spawning subagents:

1. `project/040_compliance/legal_docs/bundle_map.md`
2. The lowest-ID canonical document in the same bundle folder

Include both in each subagent brief and instruct the subagent to skip its own
Bundle context step. If either is missing or unreadable, stop:
`Error: required bundle context is unreadable: <path>`.

Skip this step for non-Maindi sources.

## Delegate

Read `~/.claude/product/010_agents/040_compliance_saul/saul.md` and
`~/.claude/commands/steve-review-legal-doc.md`. Spawn Saul and Steve as
subagents **in parallel**, briefing each with the full source text, their
spec (Saul: his agent profile and its Quality Gate; Steve: his command spec),
and the loaded bundle context content. Instruct Saul's subagent to report
checks [1] Legal refs and [2] Completeness in the output format below.

If `--pdf` is provided, also spawn a third Steve subagent following
`~/.claude/commands/steve-review-legal-pdf.md`.

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
Release: BLOCKED — 051 is a draft/unapproved review-only document
```

Omit [5] row if `--pdf` was not provided.
Omit the `Release:` line unless `review_only = true`.

## Hard rules

- Never change legal meaning or remove `human_` placeholders.
- Trim suggestions are flags only — no edits.
- Missing optional guide → SKIPPED is valid; do not invent checks.
- Never claim [5] PASS without the PDF subagent having read every page.
- Never describe document 051 as approved, releasable, signable, or production-ready.
- Suppress a `<!-- confirm with lawyer: ... -->` finding only when the contiguous
  metadata comments immediately after it include `<!-- risk-accepted: ... -->`
  or `<!-- resolved: ... -->` with a substantive value other than `[pending]`.
  Instruct subagents accordingly.
