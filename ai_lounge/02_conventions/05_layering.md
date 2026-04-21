---
name: layering
description: Where each rule belongs when an agent has core / project / document layers
---

# Layering

Agents compose across layers: a brigade role, a project
overlay, sometimes a per-document prompt. Without a rule
for what lives where, content drifts and duplicates.

## Decision test

Before writing a rule into any file, ask:

> *Would I repeat this rule if I wrote a second project,
> a second document, or for a second human?*

- **Universal across projects & jurisdictions**
  → the core agent file (brigade).
- **Universal within this project**
  → the project agent file.
- **Only when producing this one deliverable**
  → the document prompt.
- **Also consumed by humans, not just the agent**
  → a convention (this folder).

If a rule fits two layers, it belongs in the higher one.
The lower layer references it — never restates it.

## Loading chain

Each layer loads the one above it. Core agent files
self-load the conventions they apply (via the folder
README as the index). Project files only add what is
project-specific. Document prompts only add what is
document-specific.

Invoking the lowest layer should bring everything above
it. No hidden prerequisites, no "assumes loaded."

## Validation

- Grep a rule across the tree — it should appear once.
- Every path referenced in a layer must resolve.
- A fresh session invoking the lowest layer should work
  end-to-end without manual pre-loading.
