---
description: Review an AI instruction asset for minimalism, completeness, portability, redundancy, context size, compatibility, and hallucination resistance. Findings only, no auto-fix.
argument-hint: <path/to/SKILL.md|path/to/command.md|path/to/skill-folder>
---

You are running a **skill-review** audit.

Anchor: `$ARGUMENTS` — a skill, slash command, or other
AI instruction file, or a skill folder.

**Output: a findings table, then a decision.
Findings only — no edits, no auto-fix.**

---

## Before starting — load

Read these conventions so your checks are grounded:

- `~/.claude/ai_lounge/02_conventions/00_md_editing_context.md`

Then resolve the anchor:

- If `$ARGUMENTS` is a folder, read its `SKILL.md`.
- If `$ARGUMENTS` is a file, read that file.
- If missing, stop:

  ```text
  Blocked: instruction anchor not found — pass a file or folder.
  ```

Do not assume a specific runtime. Review the anchor as a portable
AI instruction asset.

---

## Phase 1 — Collect references

From the anchor, extract:

- Required input paths.
- Optional references or bundled files.
- Output rules.
- Validation gates.
- Upstream and downstream commands, skills, or generated files.
- Any project-specific names, paths, tools, or runtime assumptions.

For slash commands, treat `$ARGUMENTS`, output rules, file writes,
and fields consumed by downstream commands as contracts.

Read only referenced files required to verify the workflow.
Do not crawl the project.

Also run a targeted stale-copy scan on the anchor and directly
referenced instruction files:
- old project/product names;
- non-resolving paths;
- duplicate templates or format blocks;
- instructions that say to paste/write output somewhere stale.

---

## Phase 2 — Run 10 checks

Record: check | finding | severity (High / Med / Low) |
location | suggested fix.

Skip checks that pass cleanly.

**S1 — Trigger clarity**
The asset must say when to use it, not only what it does.
Fail = vague trigger or missing frontmatter / opening purpose.
Severity: Med.

**S2 — Scope boundary**
The asset must define its task boundary, inputs, output, and
stop condition.
Fail = agent can keep expanding scope or invent missing inputs.
Severity: High.

**S3 — Completeness**
Every required context source, validation step, and output rule
needed to execute the asset must be present.
Fail = missing source or hidden prerequisite. Severity: High.

**S4 — Minimalism**
Flag generic advice, repeated principles, long examples, or
support files that do not change execution.
Severity: Low.

**S5 — No redundancy / contradiction**
Compare the anchor against loaded conventions and referenced files.
Fail = duplicated rule, stale copy, or contradiction.
Severity: Med for contradiction, Low for duplication.

Also flag multiple canonical homes for the same workflow rule
(for example a slash command plus a project-local template saying
the same thing differently). Severity: Med.

**S6 — Portability**
Flag project-specific paths, names, tools, or runtime assumptions
unless marked as examples or resolved from the active project.
Severity: Med.

**S7 — Hallucination resistance**
The asset must require reading sources before factual claims and
must tell the agent how to handle missing or uncertain facts.
Fail = invites guessing, invented paths, invented APIs, or
unverified project facts. Also fail when it requires citation or
source evidence but gives the output schema no place to put it.
Severity: High.

**S8 — Context size**
The anchor body should stay lean. Optional or
variant-specific material belongs in directly referenced files
only when needed.
Fail = bloated body, deep reference chain, or always-loaded
context that is rarely needed. Severity: Med.

**S9 — Compatibility**
If the asset produces output consumed by another skill, command,
or script, verify the producer/consumer contract.
Fail = mismatched file lookup, required fields missing, incompatible
format, or downstream command cannot find the output.
Severity: High.

**S10 — Change strategy**
The asset must say how to handle existing outputs or existing
instruction files when rerun or reviewed.
Fail = always overwrites, always regenerates, or has no
no-op / patch / regenerate decision gate.
Severity: Med.

---

## Phase 3 — Output

Print a markdown findings table:

| Check | Finding | Severity | Location | Suggested fix |
|---|---|---|---|---|

Then one decision line:

- **No-op** — reviewed file is already fit for purpose.
- **Patch** — findings are localized and fixable in place.
- **Regenerate** — scope, trigger, or workflow structure is
  unclear enough that patching would be noisier than rewriting.

**Hard rules:**
- No prose between checks or after the decision.
- Do NOT edit any file.
- Do NOT queue tasks.
- Flag stale duplicate support files when their only role is to
  restate the anchor.
