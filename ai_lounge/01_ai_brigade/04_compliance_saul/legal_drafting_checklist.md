---
owner: saul
---

**Version:** v0.1 — 2026-04-28
**Status:** Draft
**Reviewer:** unassigned

# Legal-Doc Drafting & Review Checklist

Procedural checklist. Loads only when drafting or reviewing a
legal document — not on every Saul session. Definitions of
*lawyer-ready* live in core Saul; this file is the
verify-this-mechanically pass.

---

## Pre-draft

- [ ] Bundle-map row read for this doc (layer, owned topics,
      cross-ref rules).
- [ ] This doc's prompt file read end-to-end.
- [ ] Every "Source files to read before drafting" listed in
      the prompt has been read.
- [ ] No file from the prompt's "Do not read" list is open.
- [ ] If patching: existing DE+EN outputs exist and have
      been read. Lawyer flags from the previous draft are
      noted so they survive the patch.

## During draft

- [ ] Every material obligation cites its article in
      `(DSG Art. X Abs. Y)` form (German citation; English
      docs append `— German original`).
- [ ] Every uncertainty is a *specific, answerable*
      `<!-- confirm with lawyer: ... -->` flag — never a
      vague hedge.
- [ ] Every `human_<key>` token used appears in the prompt's
      placeholder table. No rogue placeholders invented.
- [ ] Facts the bundle map marks `R` for this doc are
      referenced, not restated. Facts marked `C` are owned
      here and stated once.
- [ ] If signed-core / external: no vendor names, no country
      names. Identity and location belong only in Anhang A.

## Pre-output (review)

- [ ] The doc-specific pre-output checklist in the prompt
      passes item-by-item.
- [ ] If external layer: zero references — by filename,
      path, or content — to internal docs (011, 021, 051).
- [ ] Layer self-containment intact: external docs are
      self-contained as a *set* (signed core + annexes).
- [ ] Cross-references resolve (target file exists, target
      section exists).
- [ ] All four lawyer-ready criteria from core Saul satisfied
      (citations, `human_` clarity, lawyer flags,
      cross-refs, lawyer-readability).
- [ ] No `human_` value resolved in the markdown. Resolution
      happens at render time only.
- [ ] No translation cites the English regulation text. EN
      files preserve German citations and append
      `— German original` where applicable.
