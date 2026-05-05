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

`task_count = 1`

---
