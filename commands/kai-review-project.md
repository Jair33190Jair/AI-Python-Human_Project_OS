---
description: Audit a project's AI system against brigade conventions and project-structure rules. Reports PASS/FAIL per check with fix actions.
argument-hint: "[project-root-path]"
status: draft
owner: kai
---

# /kai-review-project

Audit any project's AI system for convention compliance and quality issues.
Use when onboarding a new project, after structural changes, or to spot-check convention compliance.
Read-only — never edits files.

## Arguments

`$ARGUMENTS` — absolute or relative path to the project root.
Defaults to the current working directory if omitted.

## Blocked conditions

Stop and print `Blocked: <reason>` if:
- No `README_AI.md` found at the resolved project root.
- A required convention file cannot be read.

## Execution

### 1. Resolve project root

Use `$ARGUMENTS` as the project root. If empty, use the current working directory.
Confirm `README_AI.md` exists there or stop with Blocked.

### 2. Load conventions

Read in parallel — stop with Blocked if either is missing:
- `~/.claude/ai_lounge/02_conventions/11_project_structure.md`
- `~/.claude/ai_lounge/02_conventions/00_md_editing_context.md`

### 3. Map the project

Run `find <root> -maxdepth 4 -not -path '*/.git/*'` to get the actual tree.
Read `README_AI.md` from the project root.

### 4. Run checks

Report each check as **PASS**, **FAIL**, or **WARN**.
FAIL = rule is violated. WARN = smell or missing best-practice, not a hard rule.

#### A. Root files

| Check | Rule |
|---|---|
| `README_AI.md` present | Required |
| `ai_tasks_open.md` present | Required |
| `ai_tasks_closed.md` present | Required |
| `.claude/commands/` present | Required |

#### B. Agent Context Model

| Check | Rule |
|---|---|
| `README_AI.md` has agent domain paths table (`Agent \| Domain path`) | Required |
| Every agent in the table has its domain `README_AI.md` on disk | Required |
| No per-project agent files at `project/<agent>.md` | Required — context belongs in domain `README_AI.md` |
| Domain `README_AI.md` files contain no generic agent traits | Required — brigade files own those |

#### C. Project layer (`project/`)

| Check | Rule |
|---|---|
| `project/010_vision/` present | Required |
| No undeclared subfolders (not in ai_README layout) | WARN if found |

#### D. Product layer (`product/`)

| Check | Rule |
|---|---|
| `product/` present | Required |
| Primary core domain folder (`product/010_*/`) present | Required |
| `coordinator.md` present in core domain folder | Required |
| `product/020_workflows/` present | Required |
| `product/030_templates/` present | Required |
| No undeclared subfolders (not in ai_README layout) | WARN if found |
| No empty directories | WARN if found |

#### E. Slash commands

| Check | Rule |
|---|---|
| All commands listed in `README_AI.md` slash commands table resolve to real files | Required |
| All `.md` files in `commands/` or `.claude/commands/` are listed in `README_AI.md` | WARN if unlisted |

#### F. Markdown conventions

Read all `.md` files under `project/` and `product/`. If more than 20 exist, read the first 20 sorted by path and note the limit in the output.
Apply the frontmatter (`owner:` required) and path (`../` forbidden) rules from the loaded `00_md_editing_context.md`.
Flag any file that contains more than 2 distinct path references to other `.md` files as a potential chain-depth smell (WARN; note this is an approximation).

| Check | Rule |
|---|---|
| Every file has `owner:` in frontmatter | Required |
| No `../` path references | Required |
| Files with > 2 outbound `.md` path references | WARN (chain depth approximation) |

#### G. ai_README accuracy

| Check | Rule |
|---|---|
| Every folder listed in the ai_README layout section exists on disk | Required |
| Every folder on disk (non-hidden, non-tooling) is listed in ai_README layout | WARN if undocumented |

### 5. Report

Print the full audit as a compact table:

```
## /kai-review-project — <project-root>

### Results

| Check | Status | Note |
|---|---|---|
| README_AI.md present | PASS | |
| Agent domain paths table | FAIL | Add table to README_AI.md |
| ... | ... | ... |

### Fix list

1. <specific fix>
2. <specific fix>

### Summary

X checks: Y PASS · Z FAIL · W WARN
```

Only include failing and warning checks in the Fix list.
If all checks pass, print `All checks passed.` and stop.

## Hard rules

- Never edit any file.
- Never invent paths — only report what `find` and file reads confirm.
- If a check is ambiguous, mark WARN and state the ambiguity.
- Flag any check whose rule comes from a convention file that could not be read.
