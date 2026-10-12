---
owner: kai
description: Shared working modes and human hand-off rules for all agents.
---

# Working Modes

Default to **Review**. State mode changes.

- **Teach** — new or risky work. Explain purpose, impact, expected result;
  the user executes.
- **Review** — prepare changes and checks; the user reviews the diff or plan
  and runs credentials, DNS, migrations, and production changes.
- **Delegate** — complete routine, reversible work; report the outcome.

Multi-step work: phases with purpose, actions, pass condition, stop condition.
Batch safe checks. Pause for secrets, production changes, irreversible actions,
or surprises. Review the change, expected result, and rollback — not every
keystroke.

## Hand to the human

Run anything checkable against a spec yourself. Hand off only:

- a credential or identity meant to stay uniquely theirs;
- subjective quality of generated output where human review is the safeguard;
- authorizing a consequential, hard-to-reverse action — execute once told.

Never bundle a mechanical check with one of these; split them. Never merge or
run an irreversible step without the human's go. For roadmap, positioning, or
architecture calls: ask detailed questions, recommend one path.
