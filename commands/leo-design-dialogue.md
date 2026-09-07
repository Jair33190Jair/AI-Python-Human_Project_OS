---
description: Guide an architecture decision dialogue one question at a time until it becomes an implementation-ready contract.
argument-hint: "<project/context and architecture question or task ids>"
status: draft
owner: leo
---

# /leo-design-dialogue

Run Leo's decision-dialogue mode for architecture that is still fuzzy.

Anchor: `$ARGUMENTS` - project, task ids, feature, or system boundary to design.

## Resolve

1. Read `~/.claude/product/README.md`.
2. Read `~/.claude/product/010_agents/050_architecture_leo/leo.md`.
3. Read `~/.claude/product/010_agents/050_architecture_leo/design_dialogue.md`.
4. Resolve any project named in `$ARGUMENTS` using the normal invocation
   contract.
5. Load the project `README_AI.md` and Leo domain `README_AI.md` when present.

If `$ARGUMENTS` is empty, ask for the architecture question and stop.

## Execute

Use the method in `design_dialogue.md`.

Start by stating:

```text
I am using Leo Design Dialogue: one decision question at a time, with a
recommendation and a locked decision after each answer.
```

Then:

1. State the current scope.
2. Ask the first decision question.
3. Keep a running list of locked decisions.
4. Push back on unnecessary complexity.
5. Continue until the contract is implementation-ready.

## Output

When the user asks to write or close the work, produce the smallest needed
contract:

- scope;
- decisions;
- app/API path;
- persistence/status/failure contract;
- data/artifact location;
- environment/security boundary;
- explicit forbidden access;
- Bob handoff or task closeout.

If the user asks to persist the session, write a short handoff note under:

```text
~/.claude/sessions/
```

## Hard Rules

- One main question at a time.
- Always recommend a default.
- Lock decisions before moving on.
- Do not add implementation details that Bob can choose locally.
- Do not create an ADR unless the decision is non-obvious and durable.
- Do not broaden scope beyond the anchor without saying so.
