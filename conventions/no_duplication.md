---
name: no_duplication
description: Refer, don't duplicate. Validate before writing new content.
---

# No Duplication

## Principle

Every fact has one home. Other places reference it.
Copies drift, references don't.

## Before writing new content

1. Ask: does this information already live somewhere?
   (Conventions, another doc, code, decisions log,
   agent context file.)
2. If yes — link to it, don't restate.
3. If the information is currently duplicated across
   places, pick one canonical home and replace the
   others with links.

## Validation gate

Run this before finalizing any document:

- Scan for paragraphs that restate info available
  elsewhere. Replace with links.
- If you find a conflict between two sources, do NOT
  silently resolve it. Flag it to the user and ask
  which wins.
- If you cannot locate an authoritative home for a
  fact you need, that's a signal — create one
  (a decision record, a convention entry, a glossary
  line) and reference it.

## When duplication is acceptable

- Short context-setting sentences so the reader
  doesn't need to click through for basic orientation.
- Security- or compliance-critical constraints
  repeated at the point of use (explicit is safer
  than linked).

Mark deliberate duplications with a comment noting
the canonical source, e.g. `<!-- canonical: path/to/source.md -->`.
