---
owner: kai
description: Global task queue for cross-project and brigade-level work.
---

# Global Task Queue

Async inbox for handoffs between agents.
Newest on top. Done/obsolete → `ai_tasks_closed.md`.

### Schema

```
## TASK-NNNN — <short title>
- Date: YYYY-MM-DD
- Requested by: <agent or "user">
- Target agent: <agent>
- What: <one sentence; link to file if detail lives there>
- Status: open
- Tag: <optional>
- Depends on: <optional>
```

### Status

`open` · `done` · `obsolete`

Task IDs are append-only sparse. Increment `task_count`
for each new task. Never renumber.

`task_count = 2`

---

## TASK-0001 — Rename helpers/ to lib/
- Date: 2026-05-06
- Requested by: user
- Target agent: bob
- What: Rename `~/.claude/helpers/` to `~/.claude/lib/` — it's
  a proper Python package now (resolvers/, extractors/). Update
  all references in commands/ and README. Run smoke_fetch after.
- Status: open
- Tag: housekeeping

---
