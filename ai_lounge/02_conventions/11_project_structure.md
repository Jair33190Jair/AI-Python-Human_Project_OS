---
owner: kai
name: project_structure
description: Standard two-layer folder structure for all new AI projects
---

# Project Structure

Every new AI project follows a two-layer structure.

## Two Layers

**Project layer** (`project/`) — creator-facing. Used to build and
manage the product. Architecture, compliance, decisions.

**Product layer** (`product/`) — user-facing. What the end user
touches. Roles, workflows, templates, customer data, engine, app.

## Root Files

Always present at the project root:

```
CLAUDE.md          ← auto-loaded by Claude Code on launch
README_AI.md       ← shared project context + agent domain path mapping
ai_tasks_open.md   ← open tasks for all agents
ai_tasks_closed.md ← closed tasks
.claude/commands/  ← slash commands (auto-discovered by Claude Code)
```

## Agent Context Model

Brigade agents are generic and reusable. No per-project agent files.

When an agent is invoked on a project, Kai loads in parallel:
1. The agent's brigade file
2. The project root `README_AI.md` — shared context for all agents
3. The agent's domain `README_AI.md` if listed in the root `README_AI.md`

The root `README_AI.md` must include an **agent domain paths table**:

```markdown
| Agent | Domain path |
|-------|-------------|
| Steve | `01_project/README_AI.md` |
| Leo   | `02_architecture/README_AI.md` |
| Saul  | `03_compliance/README_AI.md` |
```

Omit an agent from the table if they have no domain-specific context
in this project.

## Project Layer

```
project/
  010_vision/            ← always present
    README_AI.md         ← Steve's domain context
    product_brief.md
    roadmap.md
    decisions.md
  020_architecture/      ← add when Leo has real architecture work
    README_AI.md         ← Leo's domain context
  030_compliance/        ← add when Saul has real compliance work
    README_AI.md         ← Saul's domain context
  # 040_builder/         ← add when Bob is building automation or app
```

Domain `README_AI.md` files are created only when the agent has
real domain-specific context to add beyond the root `README_AI.md`.

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

## Agent Naming

Brigade agents:

```text
~/.claude/ai_lounge/01_ai_brigade/NNN_<domain>/<agent>.md
```

Do not include `ai_agent`, `core`, or `project_agent` in file
names when the folder already gives that context.

Project context lives in `README_AI.md` files, not in
per-agent files. Never create `<project>_<agent>.md`.

## Commands As Buttons

Slash commands are runnable buttons.

Reusable commands live globally:

```text
~/.claude/commands/<agent>-<verb-object>.md
```

Project-only commands live in the project:

```text
<project>/.claude/commands/<project>-<verb-object>.md
```

Use global first. A project-local command is a fallback when no
global command with that name exists.

Keep commands thin. A command may contain a simple one-step
procedure. Once it coordinates multiple commands or human steps,
move the procedure into a workflow and make the command load it.

Do not put executable slash commands inside agent or domain
folders.
