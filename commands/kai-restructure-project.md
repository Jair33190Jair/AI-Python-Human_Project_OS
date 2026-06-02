---
description: Plan or apply a project restructure to the current project/product convention, repairing references after each move batch.
argument-hint: "<project-root> [plan|apply]"
status: draft
owner: kai
---

# /kai-restructure-project

Plan or apply a repo restructure to the current two-layer
`project/` + `product/` convention.

## Arguments

| Arg | Required | Description |
|---|---|---|
| `project-root` | yes | Path to the project repo root. |
| `mode` | no | `plan` or `apply`. Defaults to `plan`. |

## Resolve

1. Resolve `project-root` to an existing directory.
2. Set `mode` to `plan` when omitted.
3. Stop if `mode` is not `plan` or `apply`.
4. Stop if `README_AI.md` is missing at `project-root`.
5. Read the current project tree with:

```bash
find <project-root> -maxdepth 4 -not -path '*/.git/*'
```

6. Load:
   - `~/.claude/product/020_conventions/11_project_structure.md`
   - `~/.claude/product/020_conventions/00_md_editing_context.md`
   - root `README_AI.md`
   - root `README.md` if it exists
   - root `dev_tasks_open.md` if it exists
   - `dev_tasks_open.md` inside the project directory if it exists

## Plan Mode

Create or update `restructure_plan.md` inside the project's
`project/` directory.

If the file already exists, patch it when the target convention is
still compatible. Replace it only when the existing plan preserves
an obsolete structure. If the existing plan is actively being used
and conflicts with this command, stop and report the conflict.

The plan must contain:

- target folder tree;
- source-to-target move map;
- batch order;
- files that need manual review;
- commands to run after each batch;
- blocked items.

After writing or accepting the plan, read the concrete file and
verify every required section is present. Stop if validation fails.

Use this target convention unless the project already has a
clearer compatible variant:

```text
project/
  010_strategy/
  020_business/
  030_architecture/
  040_compliance/
  050_builder/
  060_operations/
  070_insurance/
  080_reviews/

product/
  010_core/
  020_experience/
  030_content/
  040_customer_runs/
  050_engine/
  060_app/
  070_site/
```

Only include folders that have real files to hold. Use subfolders
inside `project/020_business/` for `brand/` and `funding/` when
they have multiple artifacts.

## Apply Mode

Before moving anything, read `restructure_plan.md` inside the
project's `project/` directory.

Stop if the plan is missing.
Stop if the plan does not contain a source-to-target move map and
batch order.

Execute the plan one batch at a time:

1. Move only files and directories listed in the move map.
2. Do not delete content. If a target already exists, merge only
   when the ownership is obvious; otherwise stop and report the
   conflict.
3. After each batch, run:

```text
/bob-fix-references <project-root>
```

4. Re-scan for stale old paths named in that batch.
5. Patch root `README_AI.md`, domain `README_AI.md` files,
   `README.md`, `.claude/commands/`, and task references.
6. Continue with the next batch only after the previous batch has
   no obvious stale references.

After all batches, run:

```text
/kai-review-project <project-root>
```

Fix remaining structure and reference issues when they are direct
results of the restructure. Leave unrelated findings alone.

## Output

In `plan` mode, print:

```text
Plan: project/restructure_plan.md
Next: run /kai-restructure-project <project-root> apply
Blocked: <none|short list>
```

In `apply` mode, print:

```text
Moved: <batch count>
References: <fixed|remaining issues>
Review: <pass|remaining issues>
Blocked: <none|short list>
```

## Hard Rules

- Never operate outside `project-root`.
- Never delete files during restructure.
- Never move active source code into `product/060_app/` unless the
  plan explicitly maps it there.
- Run `/bob-fix-references` after each move batch, not only at the
  end.
- Keep slash commands thin; move reusable deterministic checks into
  support scripts only after this command proves repetitive.
