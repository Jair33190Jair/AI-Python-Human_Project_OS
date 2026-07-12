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

## Bundle context

If source is under `project_docs_adapted/`, read before spawning subagents:

1. `project/040_compliance/legal_docs/project_docs_adapted/README.md`
2. `project/040_compliance/legal_docs/00_doc_drafting_prompts/bundle_map.md`
3. The lowest-ID adapted doc in the same sub-bundle folder (primary contract anchor)

Include the content of all three in the brief you send to each subagent so they
review with full bundle awareness — instruct each subagent to skip their own
Bundle context step (context already provided).
Skip silently if source is not under `project_docs_adapted/`.
If source is under it but any required path is missing or unreadable, stop:
`Error: required bundle context is unreadable: <path>`.
(Paths are maindi-specific — move to project-local command if reused on another project.)

## Delegate

Read `~/.claude/commands/saul-review-legal-doc.md` and
`~/.claude/commands/steve-review-legal-doc.md`. Spawn Saul and Steve as
subagents **in parallel**, briefing each with the full source text, their
command spec, and the loaded bundle context content.

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
```

Omit [5] row if `--pdf` was not provided.

## Hard rules

- Never change legal meaning or remove `human_` placeholders.
- Trim suggestions are flags only — no edits.
- Missing optional guide → SKIPPED is valid; do not invent checks.
- Never claim [5] PASS without the PDF subagent having read every page.
- Suppress a `<!-- confirm with lawyer: ... -->` finding only when the contiguous
  metadata comments immediately after it include `<!-- risk-accepted: ... -->`
  or `<!-- resolved: ... -->` with a substantive value other than `[pending]`.
  Instruct subagents accordingly.
