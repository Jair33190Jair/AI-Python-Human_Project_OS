---
name: agent_brief
description: Six-field template for briefing a subagent
---

# Agent Brief Template

Use this whenever spawning a subagent. Fill every field.
Missing fields = wasted spawn.

## Template

```
**Agent:** <steve | leo | bob | saul | paul>
**Project:** <project path or short name>
**Goal:** <one sentence; the outcome that defines success>
**Inputs:** <file paths to read, in order of importance>
**Expected artifact:** <output path + format: markdown doc,
  decision record, patch, etc.>
**Constraints:** <out of scope, deadlines, conventions to
  respect, max length>
```

## Subagent first moves (in order)

1. Load base context:
   `~/.claude/CLAUDE.md` + `~/.claude/conventions/*.md`
   + `~/.claude/agents/<own-name>.md`
   + `<project>/ai_context.md`
   + `<project>/agent_contexts/<own-name>.md`
2. Read every path in **Inputs**.
3. Produce the **Expected artifact** at the specified path.
4. Return a 3-line summary: what you did, what you assumed,
   what's open.

No exploration beyond Inputs unless the brief explicitly
invites it. If Inputs look insufficient, stop and ask —
don't improvise.

## Why this exists

Subagents are stateless. Every spawn starts cold. A sharp
brief is the only thing that compensates. Loose briefs
produce generic work and burn tokens.
