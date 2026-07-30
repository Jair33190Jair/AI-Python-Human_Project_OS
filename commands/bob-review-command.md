---
description: Review a skill or slash command for instruction quality and scriptability. Not for agent profiles or drafting prompts. Findings only — no auto-fix.
argument-hint: <path/to/SKILL.md|path/to/command.md|path/to/skill-folder>
status: refining  # human flips to `stable` when satisfied
owner: bob
---

You are running a **skill-review** audit.

Anchor: `$ARGUMENTS` — a skill or slash command file or folder.

Findings only.

If the decision is `Recreate`, ask whether to run
`/bob-create-command` with the complete review output.

---

## Resolve

If `--with-scripts` appears anywhere in `$ARGUMENTS`, note the
flag and strip it before processing the anchor path.

Run preflight first:

```bash
python3 ~/.claude/commands/bob-review-command/preflight.py "$ANCHOR"
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

Read `~/.claude/commands/bob-review-command/rubric.md`
and run S1–S13 from it.
Skip checks that pass cleanly.

Record:

- S1–S11, S13: `check | finding | severity | location | suggested fix`
- S12: `step | effort | frequency | impact | verdict`

**Suggested fix must be diff-precise**: exact text to add,
remove, or replace — not a direction. If the fix cannot be
stated at that level, the finding is not ready to emit.

**Sort S1–S11 rows**: High severity first, then Med, then
Low. Within a severity, order by check number.

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
answering focused AI questions or drafting from existing sources,
and that it would run via `/bob-create-command`.
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

If `--with-scripts` was set, load and execute
`~/.claude/commands/bob-review-command/script-review.md`.

## Final Validation

Before emitting, write the drafted report to a temp file and run:

```bash
python3 ~/.claude/commands/bob-review-command/validate_output.py "$DRAFT"
```

It checks table headers, decision-label format, metrics format, and
the Recreate handoff prompt. If it prints `FAIL:` lines, fix the
output and rerun before responding.

Also verify by hand: preflight coverage and workflow contract
compliance (these are not scripted).

Hard rules:

- No prose between output sections.
- No prose after the metrics except the recreate handoff prompt.
- Do not edit files.
- Do not queue tasks.
- Flag stale duplicate support files that only restate the anchor.
