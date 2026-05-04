---
owner: kai
---

# Codex Entry Point

Canonical global instructions live in `~/.claude/CLAUDE.md`.

Read that file before acting in this workspace.

## Slash Command Compatibility

For Claude-style commands, e.g. `/article-routing BS-GesG`:

- Read `~/.claude/commands/<command>.md`.
- Treat the rest of the invocation as `$ARGUMENTS`.
- Run the command spec in order and obey its output rules.

Resolve command paths against the active project root unless
they start with `~/.claude/`. If the project root is unclear,
derive it from the summoned agent path; ask only if still
ambiguous.

For writes outside the sandbox, request the narrowest approval:
project root beats all-home access.
