---
name: doc_header
description: Standard header block for agent-generated deliverables
---

# Document Header

Every deliverable (design doc, decision record, spec,
legal doc, runbook) opens with:

```
**Version:** v<MAJOR>.<MINOR> — YYYY-MM-DD
**Status:** <Draft | In Review | Approved | Deprecated>
**Reviewer:** <human name(s), comma-separated, or "unassigned">
```

## Rules

- MINOR bumps on edits within a draft cycle; MAJOR on a
  new cycle after Approved.
- Date = last write, not first.
- Status vocabulary is fixed — don't invent new values.
- Reviewer is always human. Agents draft or sign off as
  author — they never review.
- Always use english attributes, never translate

## Does NOT apply to

- `README.md`, `ai_context.md` — orientation files.
- `friction.md` and other running logs.
- Conventions and other non-deliverables.
- Code files.

Internal scratchpads: omit the header entirely — don't
fake it.
