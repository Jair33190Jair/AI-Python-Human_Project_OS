---
name: no_duplication
description: Refer, don't duplicate. Validate before writing new content.
---

# No Duplication

Every fact has one home. Other places link to it. Copies
drift, references don't.

## Before writing new content

1. Does this info already live somewhere? (Conventions,
   another doc, code, decisions log, agent context.)
2. If yes — link to it, don't restate.
3. If currently duplicated across places — pick one
   canonical home and replace the others with links.

## Validation gate (before finalizing)

- Scan for paragraphs restating info elsewhere → replace
  with links.
- Conflict between two sources? Flag to the user. Do not
  silently pick a winner.
- No authoritative home exists for a fact you need?
  That's a signal — create one (decision record,
  convention entry, glossary line) and reference it.

## When duplication is acceptable

- Short context-setting sentences so the reader doesn't
  need to click through for basic orientation.
- Security- or compliance-critical constraints repeated
  at the point of use (explicit beats linked).

Mark deliberate duplicates with the source:

```
<!-- canonical: path/to/source.md -->
```
