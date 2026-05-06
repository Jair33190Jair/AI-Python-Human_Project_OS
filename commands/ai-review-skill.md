---
description: Review a skill or slash command for instruction quality and scriptability. Not for agent profiles or drafting prompts. Findings only — no auto-fix.
argument-hint: <path/to/SKILL.md|path/to/command.md|path/to/skill-folder>
status: draft  # human flips to `stable` when satisfied
owner: kai
---

You are running a **skill-review** audit.

Anchor: `$ARGUMENTS` — a skill or slash command file or folder.

Findings only. Do not edit or queue tasks.

---

## Resolve

Run preflight first:

```bash
python3 ~/.claude/commands/support/ai-review-skill-preflight.py "$ARGUMENTS"
```

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

Read only referenced files required to verify the workflow.
Do not crawl the project.

Use preflight as the first stale-copy scan pass.
Then judge old names, duplicate templates, and stale
paste/write instructions that need human interpretation.

## Checks

Read `~/.claude/commands/support/ai-review-skill-rubric.md`
and run S1–S12 from it.
Skip checks that pass cleanly.

Record:

- S1–S11: `check | finding | severity | location | suggested fix`
- S12: `step | effort | frequency | impact | verdict`

## Output

Print, in order: S1–S11 table; one decision line; S12 table
only if flagged; metrics block.

Use these schemas:

| Check | Finding | Severity | Location | Suggested fix |
|---|---|---|---|---|

| Step | Effort | Frequency | Impact | Verdict |
|---|---|---|---|---|

**Metrics**
Context load: `<Light | Moderate | Heavy>` — <N files loaded, chain depth N>
Instruction clarity: `<Clear | Mixed | Unclear>` — <1-line reason>

## Final Validation

Before emitting, verify: table schema, exact decision label,
conditional S12, rubric metrics, and preflight coverage.

If validation fails, fix the output before responding.

Hard rules:

- No prose between output sections or after the metrics.
- Do not edit files.
- Do not queue tasks.
- Flag stale duplicate support files that only restate the anchor.
