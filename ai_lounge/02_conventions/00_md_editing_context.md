---
owner: kai
description: Shared convention bundle — load before drafting or editing any markdown file.
---

# Markdown Editing Context

Load before drafting or editing any `.md` file.

## Headers

Every authored markdown file opens with frontmatter:

```
---
owner: <agent-name>
description: <one-line purpose>
---
```

`owner` is required. Multiple owners: `owner: kai, saul`
Omit `description` when the title already says enough.

Deliverables (design docs, decision records, specs, legal
docs, runbooks) add `version`, `status`, and `reviewer`
to the same frontmatter:

```
version: v<MAJOR>.<MINOR>
status: <draft | approved | deprecated>
reviewer: <human name(s) or unassigned>
```

- MINOR bumps on edits within a draft cycle; MAJOR after
  approval.
- `status` vocabulary is fixed; don't invent values.
- `reviewer` is always human. Agents are authors, never
  reviewers.
- Always use English attributes; never translate keys.

**When reading:** identify the owner(s). No action required.
**When modifying a file you don't own:** don't edit it.
Raise a task in `ai_tasks_open.md` targeting an owner.
**When you own the file:** modify directly. Note cross-agent
impacts in the task queue.
**Kai override:** Kai may modify any file for structural or
cross-agent changes — log as a resolution note.

Scope: all `ai_lounge` and project workspace markdown files.
Not applicable to vendored dependencies, virtualenvs, or
third-party license files.

Deliverable metadata does NOT apply to: `README.md`,
`ai_context.md`, `friction.md`, conventions, code files,
or internal scratchpads.

## Paths

All file paths in agent profiles, project agents, and
document prompts must be **root-relative** from the
project root (e.g. `03_compliance/legal_docs/…`).

Never use relative paths (`../`, `./`).

**Exception:** paths inside `~/.claude/` may use the
`~/` prefix.

## Markup

### `human_` prefix

Use `human_` for any value a human must supply before the
artifact is usable:

```
# documents
human_company_name

# JSON / config
"endpoint": "human_api_endpoint"

# code
API_KEY = "human_api_key"
```

- Only where the value genuinely varies per context.
  Don't over-annotate stable values.
- Never resolve `human_` fields in copies or translations.

### AI / human boundary

Where it isn't obvious which parts are AI-generated vs.
human-edited, mark it:

```
<!-- AI-generated — human should review -->
<!-- Human fills in from here -->
```

## No Duplication

Every fact has one home. Other places link to it.

Before writing new content:

1. Already lives somewhere? Link — don't restate.
2. Currently duplicated? Pick one canonical home; replace
   the others with links.
3. No authoritative home exists? Create one (decision
   record, convention entry) and reference it.

Conflict between two sources: flag to the user — never
silently pick a winner.

Mark deliberate duplicates with their source:

```
<!-- canonical: path/to/source.md -->
```

Acceptable duplication: short context-setting sentences so
the reader doesn't need to click through; safety, security,
or compliance constraints repeated at the point of use.

### Layered rule hierarchy

Rules compose across layers:
`CLAUDE.md` → conventions → core agent → project agent →
document prompt.

- Lower layers may only **extend** (add specificity, narrow
  scope, add domain rules). Never contradict or silently
  override a higher-layer rule.
- Cite the higher-layer rule when extending:
  `<!-- extends: CLAUDE.md § Working Defaults -->`
- Two layers appear to conflict? The higher layer wins.
  Flag explicitly — never silently resolve.

## Layering

Before writing a rule into any file, ask:

> *Would I repeat this rule for a second project,
> document, or human?*

| Scope | Where it belongs |
| ----- | ---------------- |
| Universal across projects | Core agent (brigade) |
| Universal within this project | Project agent |
| Only for one deliverable | Document prompt |
| Consumed by humans too | A convention (this folder) |

If a rule fits two layers, it belongs in the higher one.
The lower layer references it — never restates it.

| Layer | Owns |
| ----- | ---- |
| Global config | Shared behavior and convention loading |
| Core agent | Role and role-specific behavior |
| Project agent | Project scope, key paths, task queue, owned docs |
| Document prompt | What is unique to one specific deliverable |

**Loading chain:** each layer loads the one above it.
Invoking the lowest layer must bring everything above it —
no hidden prerequisites.

**Validation:**

- Grep a rule across the tree — it should appear once.
- Every path referenced in a layer must resolve.
- A fresh session invoking the lowest layer must work
  end-to-end.

## Chain Depth

Reliability drops with each reference hop:
1 hop ≈ 95% · 2 hops ≈ 85% · 3+ hops: don't rely on it.

**Max safe depth: 2 hops.**
Flatten instead: have one file load all dependencies
in parallel, not sequentially chained.

## Numbering

Numbers are stable sparse identifiers — for identity and
reading order, not to prove contiguity. Intentional gaps
are allowed.

**Change numbering only to fix:**

- Duplicate IDs in the same family.
- Wrong order that misleads the reader.
- A prefix pointing to the wrong family or layer.
- A broken link or reference to a renamed path.

**Stable families** (treat as append-only unless the owner
decides otherwise): task IDs (`TASK-NNNN`), legal document
IDs (`011`, `031`…), numbered convention files, numbered
folders encoding layer or reading order.

**What to number:** durable navigation points, not every
leaf file. Use sparse three-digit prefixes for folders,
document families, or workflow files when order or identity
must stay stable. Don't number support files where the name
already communicates the role.

Folder renames are high-blast-radius — they break paths,
agent invocations, task references, and scripts. Do not
renumber folders to close gaps.

## Flags

Use when something needs clarification before the artifact
is usable or final.

```
<!-- clarify: [specific, answerable question] -->
```
e.g.:
```
<!-- clarify: lawyer — AI Act [Art. X] — applies if classified as high-risk system -->
```

Rules:
- The question must be specific and answerable — not
  "is this OK?" but "does X apply under Y condition?"
- Never leave the question blank. A blank flag is noise;
  a sharp question is actionable.
- Do not resolve flags in translations or copies.


## Trimming Gate

Run after every markdown write or edit, before final answer.

1. Does each sentence add unique information?
2. Is this rule/fact already stated or linked elsewhere?
3. Can two headings, bullets, or steps become one?
4. Can an example be removed without losing clarity?
5. Did the edit add a new abstraction, layer, or process?

Trim unless it would remove:

- a safety, legal, or security constraint;
- a source, citation, path, or ownership marker;
- a decision needed by a future agent or human.

The final file should be shorter or clearer than the draft.
If it grows, the added text must earn its place.
