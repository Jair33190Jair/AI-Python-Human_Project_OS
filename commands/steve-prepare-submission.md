---
description: Fill a submission form for a grant, accelerator, or pitch application using project context documents and a crawled submission site.
argument-hint: <submission-form.md> <crawl-index.md> <project-doc-1.md> <project-doc-2.md> [additional-docs...]
status: draft
owner: steve
---

You are running a **submission preparation** workflow.

Anchor: `$ARGUMENTS` — paths to the submission form, the crawled
submission site index, and at least two project context documents.

Write the filled submission to a new file next to the form.

---

## Resolve

Extract from `$ARGUMENTS` in this order:

1. **Submission form** — blank template to fill (`.md`)
2. **Crawl index** — `00_crawl_index.md` or equivalent from the
   crawled submission organisation site
3. **Project doc 1** — most relevant current project document
   (e.g. brand questionnaire, product spec)
4. **Project doc 2** — second most relevant document
   (e.g. landing page copy, decision log)
5. **Additional docs** — any further paths provided

If any of the four required inputs are missing, ask for them and
stop:

```
To prepare the submission, I need:
1. Submission form path: <path>
2. Crawl index path (submission organisation site): <path>
3. Project doc 1 (most up-to-date context): <path>
4. Project doc 2 (second context source): <path>
```

Do not proceed until all four are provided.

If a named file cannot be read, stop:

```
Blocked: <path> not found — resolve before continuing.
```

## Load

Read all provided files in parallel before doing any analysis.

From the **crawl index**, identify and read only the pages marked
as relevant for the submission. Skip noise pages. If the index has
no relevance annotations, read the full index and decide yourself
which pages to load (max 6).

From the **project docs**, extract:
- the product's core job and target user
- the problem being solved and primary evidence
- current build status and any measurable results
- team credentials and founder motivation
- business model and pricing
- what the founders need most right now

From the **submission form**, extract:
- the required sections and their questions
- word or time limits
- any eligibility criteria that must be addressed explicitly

## Submission Brief

Before filling any section, derive:

- what the submission organisation cares about (values, language,
  precedent projects from the crawl)
- which eligibility criteria need an explicit sentence
- which project facts map cleanest to which sections
- what is missing from the project docs and must be flagged

Do not fill sections until this brief is complete.

## Fill

Fill each section of the form in order.

For each section:

- Use only facts from the loaded sources. Do not invent numbers,
  quotes, or claims.
- Mirror the submission organisation's language where it adds
  credibility without sounding forced.
- Keep copy concise — slides and short-form submissions are read,
  not scanned.
- Mark any value a human must supply as `human_<field>` and add
  it to the open-items table at the end.
- Add image suggestions as HTML comments immediately after the
  section heading they apply to:
  `<!-- IMAGE: <specific description of what visual would help and why> -->`

Ask for human input mid-fill only when the answer would
materially change the substance of a section (not the phrasing).
Phrase the question inline as:

```
<!-- QUESTION (human): <specific, answerable question> -->
```

Do not ask about polish, tone, or word choice.

## Output

Derive the output path from the form path:

- If the form ends in `.md`, write to the same directory with
  `_filled` appended before the extension.
  Example: `foo/form.md` → `foo/form_filled.md`
- If a `_filled` file already exists in that directory, confirm
  before overwriting.

The output file must include:

1. Frontmatter with `owner: steve`, `status: draft`,
   `reviewer: human_reviewer`
2. All filled sections, in the same order as the form
3. `<!-- IMAGE: -->` suggestions where visuals add impact
4. An **Open Items** table at the end:

```markdown
## Open Items

| Field | Slide / Section | Priority |
|-------|-----------------|----------|
| human_xyz | Slide N | high / medium |
```

List every `human_` field and every `<!-- QUESTION -->` here.
Mark eligibility-blocking items as `high`.

## Validate Output

After writing the output file:

1. Confirm the file exists at the derived path.
2. Confirm every section from the original form is present in the
   output, even if filled only with `human_` placeholders.
3. Confirm every `human_` field and `<!-- QUESTION -->` in the
   written file appears in the Open Items table. Add any that
   are missing before reporting done.

If the file cannot be written or a section is absent, stop and
report which step failed.

## Hard Rules

- Never overwrite the blank submission form.
- Never invent facts, statistics, or quotes not in the source docs.
- Never claim compliance, hosting, or legal status not confirmed
  in the source docs.
- Ask inline only when substance changes — not for phrasing.
- Eligibility criteria must be addressed explicitly, not implied.
