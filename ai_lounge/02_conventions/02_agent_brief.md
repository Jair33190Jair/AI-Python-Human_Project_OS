---
owner: kai
name: agent_brief
description: Task entry template for briefing a subagent
---

### Immediate vs queued

**Queue it when** the user is mid-flow, the task
depends on an in-progress decision, or context-switch
cost outweighs the value of resolving it now.

**Spawn immediately when** the answer unblocks the
current turn or it's a quick fact-check.

The subagent starts cold. Every field matters.

### Queue file — `ai_tasks_open.md`

Located at `<project-root>/ai_tasks_open.md`.
Example: `assisther/01_project/ai_tasks_open.md`.

Projects without a queue opt out — convention still
loads, but nothing to read or write.

Task IDs are append-only sparse IDs. Use the next
`task_count` value for new tasks; never renumber existing
tasks to close gaps.

### Schema

Newest on top when practical:

```
## TASK-NNNN — <short title>
- Date: YYYY-MM-DD
- Requested by: <agent name or "user">
- Target agent: <agent name>
- What: <one sentence. Refer to a file if instructions
        live elsewhere. Add detail only when essential.>
- Status: open
- Tag: <optional — enables batched resolution>
- Depends on: <optional — task sequencing>
```

### Status workflow

Statuses: `open` · `done` · `obsolete`

- **open** — created, not yet acted on
- **done** — executed successfully
- **obsolete** — no longer relevant

**Locations:**
- Open tasks live in `ai_tasks_open.md` (newest on top)
- Done/obsolete tasks move to `ai_tasks_closed.md`
  (same directory)
