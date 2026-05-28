---
owner: kai
---

# Global — Closed tasks

## TASK-0002 — Rename helpers/ to lib/
- Date: 2026-05-06
- Closed: 2026-05-06
- Requested by: user
- Target agent: bob
- Resolution: `~/.claude/helpers/` was already renamed to
  `~/.claude/lib/`. smoke_fetch passed (fedlex-dsg 79/79,
  eurlex-gdpr 99/99, basel-gesg 81/81, ticino-regpsi 21/21).
- Tag: housekeeping

## TASK-0001 — bob-web2md: Implement Playwright Tier 3
- Date: 2026-05-05
- Closed: 2026-05-05
- Requested by: user
- Target agent: bob
- Resolution: Implemented Playwright+Chromium Tier 3 for
  `/bob-web2md`. Helper layer created at `~/.claude/lib/`
  (`web-render.py`, `bootstrap.sh`, `requirements.txt`,
  `README.md`). venv self-bootstraps on first run. Tier 3
  stub in `bob-web2md.md` updated with exact bash invocation.
  `tier_used` extended to `1 | 2 | 3`. Fallback chain
  updated. Smoke-tested: 1767 words rendered from HN.
  Moved out of `commands/` to prevent harness from
  indexing venv files as slash commands.
