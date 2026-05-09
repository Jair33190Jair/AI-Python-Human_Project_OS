---
description: Review a skill or slash command for instruction quality and scriptability. Not for agent profiles or drafting prompts. Findings only — no auto-fix.
argument-hint: <path/to/SKILL.md|path/to/command.md|path/to/skill-folder>
status: refining  # human flips to `stable` when satisfied
owner: kai
---

You are running a **skill-review** audit.

Anchor: `$ARGUMENTS` — a skill or slash command file or folder.

Findings only. Do not edit or queue tasks.

If the decision is `Recreate`, ask whether to run
`/ai-create-command` with the complete review output.
Load workflow:
`~/.claude/ai_lounge/020_workflows/010_command_review_recreate_chain.md`.

---

## Resolve

If `--with-scripts` appears anywhere in `$ARGUMENTS`, note the
flag and strip it before processing the anchor path.

Run preflight first:

```bash
python3 ~/.claude/commands/ai-review-command/preflight.py "$ANCHOR"
```

where `$ANCHOR` is `$ARGUMENTS` with `--with-scripts` removed.

Use its resolved anchor, support check, context label, and
stale-scan output.

If the anchor is missing, stop:

```text
Blocked: instruction anchor not found — pass a file or folder.
```

- If a file referenced inside the anchor cannot be read,
  record it as S3 High at the relevant line and continue.

Do not assume a specific runtime. Review the anchor as a portable
AI instruction asset.

## Collect

From the anchor, extract:

- required input paths;
- optional references or bundled files;
- output rules and validation gates;
- upstream/downstream commands, skills, or generated files;
- project-specific names, paths, tools, or runtime assumptions.

For slash commands, treat `$ARGUMENTS`, output rules, file writes,
and fields consumed by downstream commands as contracts.
Apply S3 from the rubric when judging validation gates.

Read only referenced files required to verify the workflow.
Do not crawl the project.

Use preflight as the first stale-copy scan pass.
Then judge old names, duplicate templates, and stale
paste/write instructions that need human interpretation.

## Checks

Read `~/.claude/commands/ai-review-command/rubric.md`
and run S1–S12 from it.
Skip checks that pass cleanly.

Record:

- S1–S11: `check | finding | severity | location | suggested fix`
- S12: `step | effort | frequency | impact | verdict`

## Output

Print, in order: S1–S11 table; one decision line; S12 table
only if flagged; metrics block.

Use exactly one decision label:

| Decision | Use when |
|---|---|
| Patch | The asset is structurally sound and findings are local refinements. |
| Recreate | Core contracts are missing, stale, or contradictory. |
| No change | No material findings; scriptability is acceptable as-is. |

Choose `Recreate` when targeted edits would preserve a bad
structure instead of fixing the asset.

If the decision is `Recreate`, say whether the next step is
answering focused AI questions or drafting from existing sources.
This sentence must be inside the decision line.

Decision schema:

```text
Decision: <Patch | Recreate | No change> — <one sentence reason>
```

Use these schemas:

| Check | Finding | Severity | Location | Suggested fix |
|---|---|---|---|---|

| Step | Effort | Frequency | Impact | Verdict |
|---|---|---|---|---|

**Metrics**
Context load: `<Light | Moderate | Heavy>` — <N files loaded, chain depth N>
Instruction clarity: `<Clear | Mixed | Unclear>` — <1-line reason>

## Script Review

Run only if `--with-scripts` was set.

After emitting the command review output, find `.py` files
associated with the anchor:

1. If the anchor is `foo.md`, look for a sibling folder named
   `foo/` and collect all `.py` files in it (non-recursive).
2. Also include any `.py` paths referenced inside the anchor
   text that exist on disk.

For each `.py` file found, spawn `/bob-review-script` as a
subagent. Pass the file's absolute path as `$ARGUMENTS` and
include this context in the subagent briefing:

- the script's role in the command workflow (from `## Collect`)
- the inputs, outputs, and validation checks the script must
  implement per the command's contract
- any downstream fields the script's output must satisfy

Bob should flag gaps between the script's actual behavior and
the command contract as additional findings, beyond standard
R1–R7 criteria.

Append findings under a `## Script Review` heading, one
subsection per file. If no `.py` files are found, note:

```text
Script Review: no .py files found for this anchor.
```

## Final Validation

Before emitting, verify: table schema, exact decision label,
conditional S12, rubric metrics, preflight coverage, handoff
prompt when required, and workflow contract compliance.

If validation fails, fix the output before responding.

Hard rules:

- No prose between output sections.
- No prose after the metrics except the recreate handoff prompt.
- Do not edit files.
- Do not queue tasks.
- Flag stale duplicate support files that only restate the anchor.
