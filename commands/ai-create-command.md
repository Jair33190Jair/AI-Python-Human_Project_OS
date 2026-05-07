---
description: Create or recreate a Claude-style slash command. Not for Codex skills, agent profiles, or ordinary prompts.
argument-hint: <command intent | ai-review-command output | path/to/draft-command.md>
status: draft  # human flips to `stable` when satisfied
owner: kai
---

You are running a **command-create** workflow.

Anchor: `$ARGUMENTS` — command intent, review output, or an
existing draft command path.

Create Claude-style slash commands only.
Do not create Codex skills or agent profiles.

---

## Resolve

Run preflight first:

```bash
python3 ~/.claude/commands/ai-create-command/preflight.py "$ARGUMENTS"
```

Use its `anchor_type`, `placement_hint`, missing refs, and
stale-scan output.

If preflight reports `Blocked`, stop and print the blocked line.

Preflight classifies the anchor:

- **Intent:** user describes a command that does not exist yet.
- **Review:** user provides `/ai-review-command` findings with
  `Decision: Recreate`.
- **Draft:** anchor resolves to an existing command `.md` file.

If the anchor is empty, ask for the command's purpose and stop.

If the anchor is a draft path, read it before deciding whether to
patch or replace it.

If the anchor is review output, extract every finding that changes
the new command contract before asking questions.

## Change Strategy

Use exactly one creation decision:

| Decision | Use when |
|---|---|
| New | No command exists yet. |
| Patch | Existing draft has sound trigger, scope, and output contracts. |
| Recreate | Existing draft lacks core contracts or preserves stale structure. |
| No change | Existing command already passes the quality gate. |

If `No change`, stop after reporting the command path.

## Intake Loop

Create a short **known / missing / assumed** map before drafting.

Known fields:

- command name and invocation;
- global vs project placement;
- expected `$ARGUMENTS`;
- files or URLs the command may read;
- files the command may write;
- stop conditions and blocked states;
- final output rules;
- validation gate.

Question loop:

1. Ask only for fields that change the command contract.
2. Ask at most five questions per round.
3. Prefer concrete choices over open-ended questions.
4. After each answer, update the map and check again.
5. Repeat until all required fields are known or safely assumed.

Use these defaults when they are safe:

- command name: derive from the requested invocation;
- placement: global for reusable workflows, project for local ones;
- `$ARGUMENTS`: one anchor unless the user needs more;
- output: concise terminal report unless files are required;
- validation: run `/ai-review-command` on the created command.

Stop and ask instead of assuming when the answer changes:

- what files may be written;
- whether destructive edits are allowed;
- whether project-specific paths are contractual;
- what downstream command or human consumes the output;
- what counts as blocked or complete.

Before drafting, print one sentence with the chosen contract.

## Placement

Use global placement when the workflow is reusable across projects:

```text
~/.claude/commands/<command>.md
```

Use project placement when the command depends on project agents,
task queues, domain paths, document families, or local conventions:

```text
<project>/.claude/commands/<command>.md
```

If placement is ambiguous, prefer project placement for
project-specific names or paths; otherwise prefer global.

## Source Rules

Read every file whose facts, paths, fields, or workflow rules are
encoded in the new command.

If a required source cannot be read, stop:

```text
Blocked: <path> not found — resolve before creating command.
```

Do not invent project paths, downstream contracts, or validation
commands. Mark uncertain human-owned values with `human_`.

## Draft

Write the command as a portable instruction asset.

Required structure:

- frontmatter with `description`, `argument-hint`, `status`,
  and `owner`;
- short purpose line;
- argument contract;
- resolve or preflight step;
- execution phases;
- validation or review gate;
- output rules;
- hard rules.

Keep the command short enough to review easily. Put long examples,
optional variants, or deterministic checks in support files only
when they change execution.

Prefer one command file. Add support scripts only when the step is
deterministic, repeated, and safer as code than prose.

Do not include generic AI advice. Do not restate global
conventions except where the command extends them.

Target a clean `/ai-review-command` result:

- S1: trigger says when to use the command;
- S2: scope, input, output, stop state, and validation are explicit;
- S3: all referenced files and commands exist or are blocked;
- S4: prose is lean and executable;
- S5: each rule has one home;
- S6: runtime assumptions are checked, not implied;
- S7: facts come from read sources, not memory;
- S8: optional context is not always loaded;
- S9: downstream formats are named and validated;
- S10: reruns have patch / recreate / no-op behavior;
- S11: placement matches portability.

## Quality Gate

Run the finished command through `/ai-review-command`.

If the result is `Decision: No change`, report the new command path.

If the result is `Decision: Patch`, apply one focused patch, then
run `/ai-review-command` again.

If the result is `Decision: Recreate`, stop and ask the focused AI
questions needed to rebuild the command contract. Do not polish a
bad structure.

## Output

After the quality gate passes, print:

```text
Created: <path>
Review: <No change | Patch passed>
Notes: <one sentence, only if useful>
```

Hard rules:

- Create slash commands only.
- Do not create Codex skills.
- Do not edit unrelated commands.
- Do not mark `status: stable`; humans do that.
