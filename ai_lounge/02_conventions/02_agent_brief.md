---
name: agent_brief
description: Six-field template for briefing a subagent
---

# Agent Brief

Every subagent spawn starts cold. The brief is the only
thing that compensates. Fill every field — missing fields
burn tokens and produce generic work.

## Template

```
**Agent:** <path>
**Project:** <path or short name>
**Goal:** <one sentence; the outcome that defines success>
**Inputs:** <file paths to read, in priority order>
**Expected artifact:** <output path + format>
**Constraints:** <scope, deadlines, conventions, length>
```

## Subagent first moves

1. Load the session global config `~/.claude/CLAUDE.md` + agent instructions from path and its attached references.
2. Read every path in **Inputs**.
3. Produce the **Expected artifact** at its path.
4. Return a 3-line summary: *did / assumed / open.*

No exploration beyond Inputs unless the brief invites it.
If Inputs look insufficient — stop and ask. Don't
improvise.
