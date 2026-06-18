---
description: Produce a professional, fillable, visually verified legal PDF from approved Markdown using a project-local print profile. Not for drafting or changing legal meaning.
argument-hint: <source.md> [--profile path/to/legal_print_profile.toml] [--output path/to/output.pdf]
status: draft
owner: bob
model: sonnet
---

You are running a **legal-document production** workflow.

Anchor: `$ARGUMENTS` — one approved Markdown source plus optional
`--profile` and `--output` paths.

This command owns layout, fillable fields, rendering, structural
verification, and visual QA. It never drafts, summarizes, or changes
legal meaning. Route legal-content decisions to the project's legal
owner or human lawyer.

## Resolve

Run:

```bash
python3 ~/.claude/commands/bob-produce-legal-doc/preflight.py $ARGUMENTS
```

Use its JSON output as the execution contract. Stop on `blocked`, except
when the only blocker is a missing profile and the user confirms the
scaffold directory as described below.

Read the resolved source, profile, project context files, brand
references, visual references, and renderer files named by the
profile. Do not search beyond these unless a referenced file is
missing or contradictory.

If no profile exists, ask for the exact legal-doc directory. After
confirmation, scaffold there:

```bash
python3 ~/.claude/commands/bob-produce-legal-doc/scaffold.py <legal-doc-dir>
```

Then fill the generated profile from project sources before rendering.

## Intake

Derive requirements from the source and profile first. Ask only for
missing decisions that change production:

- audience and contracting parties;
- prefilled versus user-fillable values;
- single, couple, or repeatable parties;
- typed text, drawn signature, or cryptographic signature;
- logo/attribution policy;
- output path and project-specific render parameters.

Before edits, state the resolved contract in one sentence.

Use preflight's `output_state`: verify and visually review
`blank_fresh`; regenerate `missing` or `blank_stale`; stop on
`completed`.

## Produce

1. Preserve all clauses, citations, flags, and legal ordering.
2. Use the project's renderer when compatible. Patch or scaffold only
   the smallest project-local tooling needed for the profile contract.
   Resolve profile command placeholders from preflight, the matched
   document entry, and intake answers. Execute the command as an argv
   list from `render_working_directory`; never interpolate a shell
   command string.
3. Generate genuine named AcroForm controls for user input. Never use
   underscore lines or decorative empty boxes as substitutes.
4. Use stable ASCII field names. Keep repeated parties and signatures
   independently named. Mark multiline, optional, checkbox, date, and
   signature behavior in the profile or renderer schema.
5. Keep headings with following content, table rows intact, and signing
   blocks together when space allows. Do not force every chapter onto a
   new page. Add a page break only when the remaining space cannot hold
   the protected block.
6. Keep tables and form sections aligned to the document's text margin.
7. Do not imply that a software provider is a contracting party. Apply
   the profile's logo policy exactly.

If the output PDF already contains non-empty form values, stop. Require
a different `--output` path; never overwrite completed intake data.

## Verify

Run after every render:

```bash
python3 ~/.claude/commands/bob-produce-legal-doc/verify_pdf.py \
  <output.pdf> --profile <legal_print_profile.toml> --source <source.md>
```

Fix every failed deterministic check before visual review.

Inspect every PNG listed in `preview_files`. Check:

- clipping, overlap, broken glyphs, and unreadable text;
- orphan headings and clauses/signature blocks split across pages;
- table alignment, margins, whitespace, and field usability;
- restrained brand hierarchy and contracting-party clarity;
- every intended input is visibly clickable and large enough to use.

Iterate render, verify, and full-page inspection until clean. If a
visual requirement conflicts with legal content or profile policy,
stop and report the conflict instead of guessing.

## Output

Print only:

```text
Produced: <pdf path>
Profile: <profile path>
Checks: pass (<page count> pages, <field count> fields)
Visual review: pass — every page inspected
Notes: <one sentence, only if useful>
```

Hard rules:

- Never change legal meaning.
- Never overwrite a PDF with completed form values.
- Never claim visual completion without inspecting every page.
- Never treat typed text fields as cryptographic signatures.
- Keep project branding and paths in the project profile, not here.
