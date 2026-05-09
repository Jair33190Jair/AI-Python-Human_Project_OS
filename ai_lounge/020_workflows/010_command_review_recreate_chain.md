---
owner: kai
---

**Version:** v0.1 — 2026-05-07
**Status:** Draft
**Reviewer:** unassigned

# Command Review Recreate Chain

Use when `/ai-review-command` returns `Decision: Recreate` for
a slash command.

## Contract

`/ai-review-command` emits the validated review output first.
After the metrics block, AI asks:

```text
Run /ai-create-command with this review output? <yes/no>
```

If the human confirms, AI loads
`~/.claude/commands/ai-create-command.md` and runs it with this
`$ARGUMENTS` envelope:

```text
Source anchor: <resolved anchor from ai-review-command preflight>

<complete ai-review-command output>
```

## Rules

- Do not chain on `Patch` or `No change`.
- Do not chain without human confirmation.
- Preserve the complete review output unchanged inside the envelope.
- `/ai-create-command` treats `Source anchor:` as the draft to read.
