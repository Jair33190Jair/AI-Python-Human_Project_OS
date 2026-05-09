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
- Date: MM-YY
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

`task_count = 6`

---

## TASK-0006 — Convention-migration skill (file rename + restructure)
- Date: 2026-05-09
- Requested by: user
- Target agent: bob
- What: Build a `/ai-restructure` slash command that migrates a project's
  files when conventions change. Shape: (1) AI phase — reads current
  file tree and the new convention spec, outputs a JSON rename/move plan
  (dry-run, reviewable); (2) Python phase — a script (`lib/restructure.py`)
  that executes the plan: renames files, updates internal references
  (import paths, cross-links in `.md` files), and emits a diff summary.
  AI involvement is capped to the mapping step; bulk I/O is pure Python.
  Deliverable: command `.md` + `lib/restructure.py` + a short test against
  one real convention change in this repo.
- Status: open
- Tag: tooling, conventions
- Depends on: —

## TASK-0005 — Firecrawl vs Playwright eval for form/web commands
- Date: 2026-05-09
- Requested by: user
- Target agent: bob
- What: Integrate Firecrawl as an alternative scraping backend and benchmark it against the current Playwright solution for `ai-fill-form` and `ai-web2md` commands — with emphasis on JS-heavy/multi-step forms (reference test: https://www.mobiliar.ch/unternehmen/kontakt-und-services/cybersicherheit-pruefen/cybercheck?survey_id=2c8f8d86-4409-4052-905d-d9f332f99c0c). Deliverable: (1) Firecrawl adapter wired into both commands; (2) side-by-side comparison of output quality, latency, and reliability for the test URL; (3) recommendation on which backend to default.
- Status: open
- Tag: tooling, scraping

## TASK-0004 — EU regulatory monitoring pipeline for Saul
- Date: 2026-05-08
- Requested by: user
- Target agent: saul (global)
- What: Design and implement a recurring process for Saul to monitor the EU regulatory pipeline — specifically MDR (Reg. (EU) 2017/745) amendments, EU AI Act delegated acts, and European Parliament legislative tracker updates — and keep the extracted content folder current. Deliverable: (1) list of official URLs and feeds to monitor (EUR-Lex, EP legislative observatory, EC AI Office); (2) a fetch schedule (e.g. monthly `/ai-web2md` runs); (3) a changelog convention so Saul knows when a local extract was last refreshed vs. the live regulation.
- Status: open
- Tag: compliance-infrastructure

## TASK-0003 — Project-agent discovery at session start
- Date: 2026-05-08
- Requested by: user
- Target agent: kai
- What: Define how Kai discovers projects and their agents at session start — no registry, no agent self-registration. Two parts: (1) document where projects live (known root: `~/dev/projects/`); (2) define the glob pattern that finds project agents by convention (e.g. `~/dev/projects/**/ai_project_agent_*.md`). Deliverable: short rule added to CLAUDE.md covering project root(s) and agent discovery pattern.
- Status: open

