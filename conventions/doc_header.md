---
name: doc_header
description: Standard header block for agent-generated documents
---

# Document Header Convention

Every document an agent produces as a deliverable
(design doc, decision record, spec, legal doc, runbook)
starts with this header:

```
**Version:** v<MAJOR>.<MINOR> — YYYY-MM-DD
**Status:** <Entwurf | In Review | Approved | Deprecated>
**Reviewer:** <human name(s), comma-separated, or "unassigned">
```

## Rules

- Bump MINOR on content edits within the same draft cycle.
- Bump MAJOR when a new cycle starts after Approved.
- Date is the date of the last write, not the first.
- Status vocabulary is fixed. Do not invent new values.
- Reviewer is always a human. An AI agent cannot be a
  reviewer (it can draft, suggest, or sign off as author —
  never review its own or another agent's work).

## Where it does NOT apply

- `README.md`, `ai_context.md` — orientation files, not
  deliverables.
- `todos.md`, `learnings.log`, `decisions/*` — running
  logs and records with their own format.
- Code files.

If a document is an internal agent scratchpad, omit the
header entirely — do not fake it.
