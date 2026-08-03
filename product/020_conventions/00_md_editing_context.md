---
owner: kai
description: Load before drafting or editing any markdown file.
---

# Markdown Editing Context

## Headers

Every authored markdown file opens with frontmatter:

```
---
owner: <agent-name>
description: <one-line purpose>
---
```

`owner` is required. Omit `description` when the title says enough.

Deliverables (design docs, decision records, specs, legal docs,
runbooks) add to the same frontmatter:

```
version: v<MAJOR>.<MINOR>
status: <draft | approved | deprecated>
reviewer: <human name(s) or unassigned>
```

- MINOR bumps within a draft cycle; MAJOR after approval.
- `status` vocabulary is fixed — don't invent values.
- `reviewer` is always human. Agents are authors, never reviewers.
- Always use English keys.

**Don't own the file?** Don't edit it — raise a task in
`dev_tasks_open.md` targeting the owner.
**Kai override:** may modify any file for structural or
cross-agent changes — log as a resolution note.

Deliverable metadata does NOT apply to: `README.md`,
`ai_context.md`, `friction.md`, conventions, code files,
or internal scratchpads.

## Paths

All paths must be **root-relative** from the project root.
Never use `../` or `./`.

**Exception:** paths inside `~/.claude/` may use `~/`.

## Markup

### `human_` prefix

Use for any value a human must supply before the artifact is usable:

```
human_company_name
"endpoint": "human_api_endpoint"
```

Only where the value genuinely varies. Never resolve in copies.

### AI / human boundary

```
<!-- AI-generated — human should review -->
<!-- Human fills in from here -->
```

## No Duplication

Every fact has one home. Other places link to it.

- Already exists? Link — don't restate.
- Duplicated? Pick one home; replace others with links.
- Conflict between sources? Flag — never silently pick a winner.

Mark deliberate duplicates: `<!-- canonical: path/to/source.md -->`

Acceptable: short context-setting sentences; safety or compliance
constraints repeated at point of use.

## Chain Depth

1 hop ≈ 95% · 2 hops ≈ 85% · 3+ hops: unreliable.

**Max safe depth: 2 hops.** Flatten: load dependencies in
parallel, not sequentially chained.

## Numbering

Numbers are stable sparse identifiers — for identity and reading
order, not contiguity. Intentional gaps are allowed.

Change numbering only to fix: duplicate IDs, wrong order, broken
links, or a prefix pointing to the wrong family.

Don't renumber folders to close gaps — renames break paths,
agent invocations, and task references.

## Flags

```
<!-- clarify: [specific, answerable question] -->
```

- The question must be answerable — not "is this OK?"
  but "does X apply under Y condition?"
- Never leave the question blank.

## Trimming Gate

Run after every markdown write or edit.

1. Does each sentence change a trigger, input, action, decision, output,
   validation, or safety boundary?
2. Can a rule or section be shorter without becoming ambiguous?
3. Is it already stated or linked elsewhere?
4. Can headings, bullets, steps, or examples be merged or removed?
5. Did the edit add an unnecessary abstraction or layer?

The target is the shortest unambiguous contract. Trim unless removing a
safety/legal/security constraint, a source or ownership marker, or a decision
needed downstream.
