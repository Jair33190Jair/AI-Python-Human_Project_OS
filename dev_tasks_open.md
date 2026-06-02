---
owner: kai
description: Global task queue for cross-project and brigade-level work.
---

# Global Task Queue

Async inbox for handoffs between agents.
Newest on top. Done/obsolete → `dev_tasks_closed.md`.

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

`task_count = 8`

---

## TASK-0008 — Create `/bob-fix-references` command + `fix.sh` script
- Date: 05-26
- Requested by: user (via kai + /ai-create-command)
- Target agent: bob
- What: Build a global slash command that renames a file/dir and repairs all references
  to the old name across a git repo. When called without rename args, infers renames
  from `git diff --name-status HEAD` and staged changes.
- Status: done
- Tag: tooling
- Depends on: —
- Shipped as: `~/.claude/commands/bob-fix-references.md` + `bob-fix-references/fix.sh`

### Deliverables

**`~/.claude/commands/bob-fix-references.md`**

```markdown
---
description: Rename a file/dir and repair all text references in a git repo. Infers renames from git when no args given.
argument-hint: "[repo_root] [old_path new_path]"
status: draft
owner: kai
---

Rename a file or directory in a git repo and fix every reference to the old
name across all tracked text files.

## Arguments

| Arg | Required | Description |
|---|---|---|
| `repo_root` | no | Repo root path. Defaults to `$PWD`. |
| `old_path` | no* | Old file or directory path (relative to repo root). |
| `new_path` | no* | New file or directory path (relative to repo root). |

\*Omit both to infer rename pairs from `git diff HEAD` + staged changes.

## Resolve

Confirm `repo_root` is a git repository:

```bash
git -C "${ARGUMENTS[0]:-$PWD}" rev-parse --show-toplevel
```

Stop with `Blocked: <path> is not a git repo.` if it fails.

## Execute

With explicit args:

```bash
bash ~/.claude/commands/bob-fix-references/fix.sh "$REPO_ROOT" "$OLD_PATH" "$NEW_PATH"
```

With no rename args (infer from git):

```bash
bash ~/.claude/commands/bob-fix-references/fix.sh "$REPO_ROOT"
```

## Output

Print the script's stdout verbatim. No additional commentary.

## Hard Rules

- Never operate outside the resolved repo root.
- Skip binary files.
- Do not auto-commit.
- If no renames detected and no args given, stop and say so.
```

---

**`~/.claude/commands/bob-fix-references/fix.sh`**

```bash
#!/usr/bin/env bash
# Rename a file/dir and repair all text references in a git repo.
# Usage: fix.sh <repo_root> [<old_path> <new_path>]
set -euo pipefail

REPO="${1:-.}"
shift || true
cd "$REPO"

OLD_PATHS=()
NEW_PATHS=()

if [[ $# -ge 2 ]]; then
  OLD_PATHS+=("$1")
  NEW_PATHS+=("$2")
else
  while IFS=$'\t' read -r old new; do
    OLD_PATHS+=("$old")
    NEW_PATHS+=("$new")
  done < <(
    { git diff --name-status HEAD 2>/dev/null
      git diff --name-status --cached 2>/dev/null; } \
    | awk -F'\t' '$1 ~ /^R/ { print $2"\t"$3 }' \
    | sort -u
  )
fi

[[ ${#OLD_PATHS[@]} -gt 0 ]] || { echo "No renames to process."; exit 0; }

FILES_RENAMED=0
FILES_UPDATED=0

for i in "${!OLD_PATHS[@]}"; do
  OLD="${OLD_PATHS[$i]}"
  NEW="${NEW_PATHS[$i]}"
  OLD_BASE="$(basename "$OLD")"
  NEW_BASE="$(basename "$NEW")"

  printf '\n[rename] %s  →  %s\n' "$OLD" "$NEW"

  if [[ -e "$OLD" ]]; then
    mkdir -p "$(dirname "$NEW")"
    git mv -- "$OLD" "$NEW" 2>/dev/null || mv -- "$OLD" "$NEW"
    (( FILES_RENAMED++ )) || true
  fi

  while IFS= read -r f; do
    [[ -f "$f" && -r "$f" ]] || continue
    grep -qI '' "$f" 2>/dev/null || continue  # skip binary

    BEFORE="$(md5sum "$f")"
    [[ "$OLD" != "$OLD_BASE" ]] && sed -i "s|${OLD}|${NEW}|g" "$f"
    sed -i "s|${OLD_BASE}|${NEW_BASE}|g" "$f"
    AFTER="$(md5sum "$f")"

    [[ "$BEFORE" != "$AFTER" ]] && {
      printf '  refs: %s\n' "$f"
      (( FILES_UPDATED++ )) || true
    }
  done < <(git ls-files)
done

printf '\nDone: %d file(s) renamed, %d file(s) updated.\n' "$FILES_RENAMED" "$FILES_UPDATED"
```

### Notes for Bob

- Make `fix.sh` executable (`chmod +x`).
- Run `/bob-review-command` on the finished command markdown before marking done.
- Related: TASK-0006 (`/ai-restructure`) covers the AI-driven JSON-plan variant;
  this command is the simpler explicit-rename path. No overlap in deliverables.

---

## TASK-0007 — Refine `/bob-review-command` to converge in one pass
- Date: 2026-05-09
- Requested by: user
- Target agent: kai
- What: Stop the review-patch oscillation cycle. Files:
  `~/.claude/commands/bob-review-command.md`,
  `~/.claude/commands/bob-review-command/rubric.md`,
  `~/.claude/commands/bob-review-command/preflight.py`. Changes:
  (1) **Risk-only Low bar** — flag Low only when not fixing it
  carries real risk (broken contract, ambiguous output, drift); strip
  cosmetic flagging from rubric S4/S5/S10/S11. (2) **Mandatory
  script-deep-read** — `## Collect` must read every `.py` referenced
  by or sibling to the anchor before judging S3, so buried contracts
  surface in the first pass. (3) **Convergence decision** — tighten
  "No change" to fire when zero High/Med and only risk-bearing Lows
  remain, instead of listing nits. (4) **Carry-forward context**
  (optional) — accept a `last-review:` frontmatter field or sibling
  file so the same finding is not relitigated. (5) **Preflight deep
  ref scan** — extend `preflight.py` to walk referenced scripts and
  conventions one hop deep and flag contracts that look unmentioned
  in the anchor body. Acceptance: re-running `/bob-review-command` on
  a freshly rewritten target three times yields "No change" each
  time. Plan: `~/.claude/plans/this-is-so-frustrating-jaunty-avalanche.md`.
- Status: open
- Tag: tooling, reviewer
- Depends on: —

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

