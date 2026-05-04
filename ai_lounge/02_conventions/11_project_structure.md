---
owner: kai
name: project_structure
description: Standard two-layer folder structure for all new AI projects
---

# Project Structure

Every new AI project follows a two-layer structure.

## Two Layers

**Project layer** (`project/`) — creator-facing. Used to build and
manage the product. Agent files, architecture, compliance, decisions.

**Product layer** (`product/`) — user-facing. What the end user
touches. Roles, workflows, templates, customer data, engine, app.

## Root Files

Always present at the project root:

```
CLAUDE.md          ← auto-loaded by Claude Code on launch
ai_context.md      ← human entry point — load this first
ai_tasks_open.md   ← open tasks for all agents
ai_tasks_closed.md ← closed tasks
.claude/commands/  ← slash commands (auto-discovered by Claude Code)
```

## Project Layer

```
project/
  010_vision/            ← always present
    steve.md             ← project driver agent
    product_brief.md
    roadmap.md
    decisions.md
  020_architecture/      ← add when Leo has real architecture work
    leo.md
  030_compliance/        ← add when Saul has real compliance work
    saul.md
  # 040_builder/         ← add when Bob is building automation or app
  #   bob.md
```

Agent files live in their domain folder. The agent IS the entry
point to that domain — do not create a separate agents folder.

## Product Layer

```
product/
  010_<core_domain>/     ← primary product capability
    coordinator.md       ← orchestrator: unnumbered, sits at top
    010_role.md          ← numbered peer domain roles
    ...
  020_workflows/
  030_templates/
  040_customer_runs/     ← operational: one subfolder per customer
  # 050_engine/          ← add when workflows become automation code
  # 060_app/             ← add when building a standalone app
```

## Rules

- Create a folder only when it has real files to hold.
- Commented-out folders signal "planned — not yet created."
- Orchestrators are unnumbered and sit at the top of their
  folder. They read all other outputs and own the final call.
- Domain reviewers / specialist roles are numbered peers.
- Use three-digit sparse prefixes for numbered folders.
  See `09_numbering.md`.
- Do not create `050_engine/` or `060_app/` before the
  workflow has been validated with a real user.
