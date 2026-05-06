---
description: Review a skill or slash command for minimalism, completeness, portability, redundancy, context size, compatibility, hallucination resistance, and scriptability. Not for agent profiles (use /ai-review-agent) or drafting prompts (use /ai-review-prompt). Findings only,commands/ai-review-skill.md no auto-fix.
argument-hint: <path/to/SKILL.md|path/to/command.md|path/to/skill-folder>
status: draft  # human flips to `stable` when satisfied
owner: kai
---

You are running a **skill-review** audit.

Anchor: `$ARGUMENTS` — a skill or slash command file,
or a skill folder.

**Output: a findings table, then a decision.
Findings only — no edits, no auto-fix.**

---

## Before starting — resolve the anchor

- If `$ARGUMENTS` is a folder, read its `SKILL.md`.
- If `$ARGUMENTS` is a file, read that file.
- If missing, stop:

  ```text
  Blocked: instruction anchor not found — pass a file or folder.
  ```
- If a file referenced inside the anchor cannot be read,
  record it as S3 High at the relevant line and continue.

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

## Phase 2 — Run 12 checks

Record: check | finding | severity (High / Med / Low) |
location | suggested fix.

Skip checks that pass cleanly.

**S1 — Trigger clarity**
The asset must say when to use it, not only what it does.
Fail = vague trigger or missing frontmatter / opening purpose.
Severity: Med.

**S2 — Scope boundary**
The asset must define its task boundary, inputs, output, and
stop condition — including an explicit input validation gate
that halts execution on bad or missing input.
Fail = agent can keep expanding scope, invent missing inputs,
or proceed silently on invalid input.
Severity: High.

**S3 — Completeness**
Every required context source, validation step, and output rule
needed to execute the asset must be present — including an
output validation gate the agent runs before emitting results.
Fail = missing source, hidden prerequisite, or no output
validation step. Severity: High.

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

**S11 — Level placement**
Determine where the anchor currently lives and whether
it belongs there.

Two valid homes:
- **Global** (`~/.claude/commands/`) — skill is generic,
  references only `~/.claude/…` paths, and would benefit
  any project equally.
- **Project** (`<project>/.claude/commands/`) — skill
  references project-specific paths, names, conventions,
  task queues, or workflows that only make sense in one
  project context.

Steps:
1. Record the anchor's current location (global or project).
2. Check for project-specific signals: hardcoded project
   paths outside `~/.claude/`, project team names, project
   task-queue references, project-specific conventions.
3. Check for global signals: all paths under `~/.claude/`,
   no project names, content applies to any project.

Fail = global skill with project-specific content, or
project skill that is fully generic and would benefit
other projects.
Severity: Med.

**S12 — Scriptability**
Flag any workflow step that is deterministic, structural,
or pattern-matchable — where a linter or script would
produce the same result at zero token cost.

Score each flagged step:
- **Effort**: Low / Med / High to automate.
- **Frequency**: how often the skill runs (per session,
  per PR, ad hoc).
- **Verdict**: Script it / Not worth it / Hybrid
  (script the check, AI interprets results).

Fail = the step is fully deterministic and runs often
enough that token cost accumulates.
Severity: Med (single step), High (most of the skill
could be a script).

---

## Phase 3 — Output

Print a markdown findings table for S1–S11:

| Check | Finding | Severity | Location | Suggested fix |
|---|---|---|---|---|

Then the decision line:

- **No-op** — reviewed file is already fit for purpose.
- **Patch** — findings are localized and fixable in place.
- **Regenerate** — scope, trigger, or workflow structure is
  unclear enough that patching would be noisier than rewriting.

Then the S12 scriptability table (omit if no steps flagged):

| Step | Effort | Frequency | Verdict |
|---|---|---|---|

Then the metrics block:

**Metrics**
Context load: `<Light | Moderate | Heavy>` — <N files loaded, chain depth N>
Instruction clarity: `<Clear | Mixed | Unclear>` — <1-line reason>

Labels are grounded — do not estimate, derive from observed facts:

*Context load*
- **Light**: ≤2 files loaded, chain depth ≤1, anchor body ≤100 lines.
- **Moderate**: 3–5 files, chain depth 2, or body 100–200 lines.
- **Heavy**: >5 files, chain depth 3+, body >200 lines, or always-loaded
  optional content.

*Instruction clarity* — based on S1/S2/S3/S7 findings only:
- **Clear**: all four pass, zero High findings total.
- **Mixed**: 1–2 High or Med findings across S1/S2/S3/S7.
- **Unclear**: 3+ High/Med findings in S1/S2/S3/S7, or S2 fails.

---

**Hard rules:**
- No prose between checks or after the decision.
- Do NOT edit any file.
- Do NOT queue tasks.
- Flag stale duplicate support files when their only role is to
  restate the anchor.
