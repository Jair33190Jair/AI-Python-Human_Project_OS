---
owner: kai
name: project_structure
description: Standard two-layer folder structure for all new AI projects
---

# Project Structure

Every new AI project follows a two-layer structure.

## Two Layers

**Project layer** (`project/`) — creator-facing. Used to steer,
fund, and manage the product. Strategy, business, architecture,
compliance, decisions.

**Product layer** (`product/`) — user-facing. What the end user
touches. Roles, workflows, templates, customer data, engine, app,
landing page, public site.

## Root Files

Always present at the project root:

```
CLAUDE.md          ← auto-loaded by Claude Code on launch
README_AI.md       ← shared project context + agent domain path mapping
dev_tasks_open.md   ← open tasks for all agents
dev_tasks_closed.md ← closed tasks
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
| Steve | `project/010_strategy/README_AI.md` |
| Leo   | `project/030_architecture/README_AI.md` |
| Saul  | `project/040_compliance/README_AI.md` |
```

Omit an agent from the table if they have no domain-specific context
in this project.

## Project Layer

```
project/
  010_strategy/          ← always present
    README_AI.md         ← Steve's domain context
    product_brief.md
    roadmap.md
    decisions.md
  020_business/          ← add when there is real commercial work
    README_AI.md
    business_plan.md
    pricing_model.md
    marketing_plan.md
    brand.md
    funding.md
    # brand/              ← add when brand has multiple artifacts
    # funding/            ← add when funding has multiple artifacts
  030_architecture/      ← add when Leo has real architecture work
    README_AI.md         ← Leo's domain context
  040_compliance/        ← add when Saul has real compliance work
    README_AI.md         ← Saul's domain context
  # 050_builder/         ← add when Bob is building automation or app
```

Domain `README_AI.md` files are created only when the agent has
real domain-specific context to add beyond the root `README_AI.md`.

Use `010_strategy/`, not `010_vision/`, for reusable AI-software
projects. Strategy covers the product brief, roadmap, priorities,
and decisions without making the folder sound aspirational.

Use `020_business/` for the commercial side: business plan, pricing,
marketing, brand strategy, and funding. Keep each as a single file
until it needs multiple artifacts. Then expand that topic into a
subfolder, for example `brand/` or `funding/`. Actual user-facing
copy, site files, or app assets live in `product/`.

Use `030_architecture/` for internal system decisions: component
boundaries, data flow, security, database, integrations, and ADRs.
Do not use it for product or UX design.

## Product Layer

```
product/
  010_core/              ← primary product capability
    coordinator.md       ← orchestrator: unnumbered, sits at top
    010_role.md          ← numbered peer domain roles
    ...
  020_experience/        ← UX flows, onboarding, product copy
  030_content/           ← templates, examples, reusable user content
  040_customer_runs/     ← operational: one subfolder per customer
  # 050_engine/          ← add when workflows become automation code
  # 060_app/             ← add when building a standalone app
  # 070_site/            ← add for landing page or public site
```

The landing page belongs in `product/070_site/`. Keep it in the
same repository by default while the product is being validated.
Split it into a separate GitHub repository only when it has its
own deployment lifecycle, collaborators, or public/private boundary.

Product and UX design belong in `product/020_experience/`: flows,
screens, onboarding, dashboard behavior, consent flows, review
flows, and product copy. Built app code belongs in `product/060_app/`.

## Rules

- **Colocate staged-pipeline artifacts.** For any staged pipeline (synthetic
  fixtures, dev/debug output, generated drafts), keep input, intermediate, and
  output artifacts numbered together in one folder per case — not spread
  across separate input/processing/output folders.
- Create a folder only when it has real files to hold.
- Commented-out folders signal "planned — not yet created."
- Orchestrators are unnumbered and sit at the top of their
  folder. They read all other outputs and own the final call.
- Domain reviewers / specialist roles are numbered peers.
- Use three-digit sparse prefixes for numbered folders.
  See `09_numbering.md`.
- Do not create `050_engine/` or `060_app/` before the
  workflow has been validated with a real user.
- Do not create `070_site/` for brand notes or marketing strategy.
  Those belong in `project/020_business/`. Use `070_site/` for
  actual landing-page or public-site artifacts.

## Agent Naming

Brigade agents:

```text
~/.claude/product/010_agents/NNN_<domain>_<agent>/<agent>.md
```

Do not include `ai_agent`, `core`, or `project_agent` in file or
folder names when the path already gives that context.

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
