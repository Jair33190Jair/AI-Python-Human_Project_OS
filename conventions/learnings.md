---
name: learnings
description: When and how to log workflow learnings for Paul to review
---

# Learnings Log

## Where

`~/.claude/learnings.log` — append-only, one line per entry.

## Format

```
YYYY-MM-DD | <agent> | <project> | <observation>
```

Keep each entry under ~200 chars. If it needs more, write
a decision record instead and log a one-liner pointing to it.

## When to append

At session close, add an entry ONLY if something
non-obvious happened:

- The user corrected your approach (what they wanted
  differed from what you did — note the gap, not the fix).
- The user validated a non-obvious choice (a judgment
  call that paid off — worth repeating).
- You noticed waste: re-reading the same file, re-asking
  the same question, a brief that needed clarification.
- A convention was ambiguous, missing, or contradicted
  another.
- A pattern repeated across projects or sessions.

## Do NOT log

- Routine successes ("task completed").
- Tool errors with obvious fixes.
- Anything already captured in `~/.claude/memory/`.

## Who reads this

Paul (workflow QM). When summoned, Paul reads the log,
spots patterns, writes suggestions to
`~/.claude/decisions/paul_<YYYY-MM-DD>.md`, and reports
back. Honest feedback is the job — including
"the user keeps asking the same thing, consider a
slash command" or "stop drafting before reading inputs."
