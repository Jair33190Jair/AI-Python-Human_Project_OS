---
owner: kai
name: project_structure
description: Single-tree folder structure for a new AI project — one repo, code and planning together.
---

# Project Structure

One repository, one tree. Code and planning docs live together. This replaces
the old `project/` + `product/` two-layer split: a solo project does not need
two navigable trees, and the split forced a "which layer?" call on every file.

Naming *within* this tree — code, artifacts, records — is
[13_naming_conventions.md](13_naming_conventions.md). This file owns the tree.

## The tree

```
<repo>/
├── README.md          canonical map — structure, routing, agent context. Single source of truth.
├── CLAUDE.md          stub — points at README.md, never copies it
├── dev_tasks_open.md  cross-agent task queue
├── dev_tasks_closed.md
├── .claude/commands/  project-local slash commands
│
├── strategy.md        brief, roadmap, priorities, decision log      (Steve)
├── architecture/      system decisions, component boundaries, ADRs  (Leo)
├── compliance/        regulatory analysis, DPIA, draft legal text   (Saul)
├── brand/             voice, visual guide, positioning, copy source (Steve)
├── finance/           model, runway, pricing rationale              (Warren)
├── operations/        runbooks, deploy and on-call notes
├── reviews/           cross-cutting review outputs
│
├── business/          DATED permanent records — never overwritten (see 13)
│   ├── finance/       sent invoices, filings
│   ├── legal/         signed contracts + <name>.meta.json sidecars
│   └── compliance/    submitted or authoritative compliance records
│
├── apps/             product code — backend, frontend, landing-page
├── pipeline/          shared data-pipeline code (see 13)
└── runs/             pipeline runtime data — gitignored, one folder per run
```

## Start small

Create a folder only when it holds real files. A new project starts with about:

```
README.md  CLAUDE.md  dev_tasks_open.md  strategy.md  architecture/  apps/
```

- **No numeric prefixes.** They are browse-ordering for a large doc set a team
  scans; solo they buy nothing and every reorder becomes a rename sweep. Reading
  order comes from the README table, not filenames.
- A domain is a single root `.md` (`finance.md`, `brand.md`) until it crosses
  about three files. Then promote it to a folder (`finance/`).
- `compliance/`, `business/`, `pipeline/`, `runs/` appear the day work lands in
  them — not before. No commented-out placeholder folders.

## Routing — where does X go?

Place by what the thing *is*:

| Thing | Home |
|---|---|
| Pricing rationale, runway model | `finance/` |
| A sent invoice, a tax filing | `business/finance/` |
| Regulation analysis, DPIA, draft legal language | `compliance/` |
| A signed contract | `business/legal/` |
| Brand voice guide, positioning | `brand/` |
| Landing-page copy source of truth | `brand/` — rendered in `apps/landing-page/` |
| System or ADR decision | `architecture/` |
| Product scope, roadmap, closed decisions | `strategy.md` |
| Pipeline code with more than one caller | `pipeline/` (sibling of `apps/`) |
| Pipeline code called by one app only | inside it (`apps/backend/pipeline/`) |
| A run's input + generated artifacts | `runs/<id>/` (gitignored) |

Unsure? It is one of these. Do not add a top-level folder without updating
`README.md` first.

## Keep thinking domains separate

`strategy`, `architecture`, `compliance`, `brand`, `finance` stay separate
folders even when small. Different readers, different lifecycles, different agent
owners. Merging them (for example "business + engineering rationale in one
folder") saves one folder and costs every reader a wade through another domain's
content; un-merging later is the painful direction.

`business/` is the one deliberate cross-domain folder: it groups by lifecycle —
dated, immutable, audit-facing — not by topic.

## Agent context

`README.md` is the canonical context file for humans and agents. It carries the
agent domain-path table:

```markdown
| Agent  | Domain |
|--------|--------|
| Steve  | strategy.md, brand/ |
| Leo    | architecture/ |
| Saul   | compliance/ |
| Warren | finance/ |
```

A domain folder adds its own `README_AI.md` only when it has context beyond the
root file. Keep the load chain to two hops or fewer.

Note: the brigade invocation contract (`~/.claude/CLAUDE.md`,
`~/.claude/product/README.md`) still loads a project-root `README_AI.md` by
name. Until that is harmonized, a brigade project keeps `README_AI.md` as the
canonical file, or makes it a one-line stub pointing to `README.md`.
