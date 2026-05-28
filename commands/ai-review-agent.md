---
owner: kai
description: Audit any project agent's profile quality — references, load chain, conventions, minimalism. Findings only, no auto-fix.
argument-hint: <path/to/project_agent.md>
---

You are running an **agent-review** audit.

Anchor: `$ARGUMENTS` — a project agent `.md` file.

**Scope: the anchor file + its "load every session" chain (depth 1).**
Do not crawl the full project tree.

**Output: a findings table, then one summary line. No prose, no auto-fix.**

---

## Before starting — load

Read these conventions so your checks are grounded:

- `~/.claude/ai_lounge/02_conventions/00_md_editing_context.md`

Then read the anchor file in full.

---

## Phase 1 — Collect load chain

Extract every file path from the anchor's "load every session" block.
Also extract all "load on demand" file paths.
Store both lists separately.

---

## Phase 2 — Run 7 checks

Run every check. Record finding | severity (High/Med/Low) | file | suggested fix.
If a check passes cleanly, do not include it in the output.

**C1 — Session files exist**
`ls` each path in the "load every session" list.
Fail = file not found. Severity: High.

**C2 — On-demand files exist**
`ls` each path in the "load on demand" list.
Fail = file not found. Severity: Med.

**C3 — No ambiguous paths**
Flag any path that is:
- filename-only (no directory prefix), or
- relative without a clear anchor comment.
Severity: Med.

**C4 — No blank flags**
`grep` for `<!-- clarify:` across the anchor file and its session load chain.
Fail = flag with no question after the colon (blank or whitespace only). Severity: Med.

**C5 — Ownership declared**
Check that every file in the session chain has `owner:` in its frontmatter.
Fail = missing field. Severity: Low.

**C6 — Minimalism: no cross-layer duplication**
Read each file in the session chain.
Flag any rule, sentence, or section that restates something
already defined in a higher-layer file (global CLAUDE.md, core agent, conventions).
Severity: Low. Requires judgment — only flag clear restatements, not extensions.

**C7 — Dead task references**
`grep` for every `TASK-NNNN` reference in the anchor file.
For each referenced TASK-ID, verify it appears in either
`ai_tasks_open.md` or `ai_tasks_closed.md` in the project.
Fail = ID not found in either file. Severity: Med.

---

## Phase 3 — Output

Print a markdown table:

| Check | Finding | Severity | File | Suggested fix |
|---|---|---|---|---|

Then one line:

`Agent review complete — N findings (H high, M med, L low).`

If no findings: `Agent review complete — no findings.`

**Hard rules:**
- No prose between checks or after the summary line.
- Do NOT edit any file.
- Do NOT queue tasks on behalf of the user — report only.
