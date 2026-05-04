---
description: Run a legal doc-drafting prompt — makes patch/regenerate decision, loads all sources, drafts, and gates on the prompt's pre-output checklist before emitting.
argument-hint: <path/to/drafting_prompt.md>
---

You are running a **prompt-run** execution.

Anchor: `$ARGUMENTS` — a doc-drafting prompt `.md` file.

Read the anchor prompt in full before doing anything else.

**Output: the drafted document (or targeted patch).
No prose commentary outside the document itself.**

---

## Phase 1 — Patch or regenerate decision

Locate the output file declared in the anchor prompt
(the first `Output file:` line).

**If no output file exists:** proceed to Phase 2 as
a full generation run.

**If output file exists — read it, then decide:**

| Signal | Decision |
| --- | --- |
| ≥ 1 required section (from the prompt's "Required sections") is entirely absent | Regenerate |
| Version delta > 2 minor versions OR structural drift across multiple sections | Regenerate |
| All required sections present AND gaps are in ≤ 4 rows / cells | Patch |
| Existing output has `<!-- confirm with lawyer` flags | Patch — preserve flags verbatim |
| All required sections present AND zero gaps AND prompt version unchanged | No change |

Print a single decision line before proceeding:

```
Decision: [Patch | Regenerate | No change] — <one sentence reason>
```

**If decision is No change:** stop here. Do not proceed to
Phase 2–5. Write no files.

---

## Phase 2 — Load all sources declared in the prompt

Execute the "Before drafting, load" block from the
anchor prompt. Read every file listed there.

If a file is missing and is **not** marked as a
forward-reference, stop and report:

```
Blocked: <path> not found — resolve before running.
```

Do not attempt to draft with missing source files.

---

## Phase 3 — Draft or patch

**Full generation:** produce the document following
every requirement in the anchor prompt.

**Patch:** apply only the targeted changes identified
in Phase 1. Do not rewrite sections that are correct.
Preserve all existing `<!-- confirm with lawyer -->` flags
exactly as written — never remove or reword them.

In both cases:

- Cite verbatim from the picked-articles folder.
  Never cite from memory or training knowledge.
- Every `human_<key>` token used must appear in the
  prompt's consolidated placeholder table. Do not
  invent placeholders.
- Apply scope-pointer notes exactly — do not draft
  topics declared out of scope in the prompt.

---

## Phase 4 — Pre-output gate

Run the prompt's own pre-output checklist
item-by-item. For every unchecked item:

```
Gate failure: item N — <description>
```

Fix all failures before emitting. Do not emit a
document that fails its own checklist.

---

## Phase 5 — Emit

Write the document (or patch) to the declared output path.

Add a run-summary comment below the document header:

```
<!-- prompt-run: [Patch | Regenerate] | prompt v<X.Y> |
     output v<X.Y> | pre-output checklist: pass | <date> -->
```

---

## Hard rules

- Never resolve a `human_` placeholder to a real value.
- Never remove a `<!-- confirm with lawyer -->` flag.
- Do NOT run post-output review — that is a separate step.
- Do NOT edit the anchor prompt file during this run.
