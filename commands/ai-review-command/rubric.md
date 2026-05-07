---
owner: kai
---

# Skill Review Rubric

Use this rubric with `/ai-review-command`.

Record only failing checks.

## Checks

**S1 — Trigger clarity**  
Must say when to use it, not only what it does.  
Fail: vague trigger or missing frontmatter/opening purpose.  
Severity: Med.

**S2 — Scope boundary**  
Must define task boundary, inputs, output, stop condition, and
an input validation gate that halts on bad or missing input.  
Fail: can expand scope, invent inputs, or proceed silently.  
Severity: High.

**S3 — Completeness**  
Must include every required source, validation step, and output
rule needed to execute.

Input validation must inspect the actual input artifact before it
is used. Output validation must run on the written output, or on
the existing output accepted as no-change. Pre-validation of a
planned output may supplement this, but must not replace validating
the concrete file.

Source warnings may be carried forward as structured output
metadata, for example a `warnings:` frontmatter field, when the
output schema defines it.

Fail: missing source, hidden prerequisite, no input validation
gate, no validation of actual written/accepted output, or
discarded source warnings that the schema can preserve.  
Severity: High.

**S4 — Minimalism / prose clarity / simplicity**  
Flag generic advice, repeated principles, long examples,
overbuilt workflows, needless abstraction, or support files that
do not change execution.

Ask whether the same skill could run with fewer steps, fewer
loaded files, fewer concepts, or a smaller output contract without
losing required behavior.

Paragraphs must be short, direct, and necessary. Sentences must be
clear, complete, and specific enough to execute.

Fail: bloated paragraph, vague wording, filler, sentence fragment,
unnecessary explanation, or wording that hides the action the AI
must take.  
Severity: Low; Med if unclear prose changes execution.

**S5 — No redundancy / contradiction**  
Check inside the anchor, across bundled support files, and against
loaded conventions and referenced files.

Fail: duplicated rule, duplicated workflow step, stale copy,
contradiction, inconsistent terminology, or multiple canonical
homes for the same workflow rule.  
Severity: Med for contradiction or multiple homes; Low for
duplication.

**S6 — Portability**  
Flag project-specific paths, names, tools, or runtime assumptions
unless marked as examples or resolved from the active project.  
Severity: Med.

**S7 — Hallucination resistance**  
Must require reading sources before factual claims and define how
to handle missing or uncertain facts.  
Fail: invites guessing, invented paths/APIs, unverified project
facts, or requires source evidence without schema support.  
Severity: High.

**S8 — Context size**  
Anchor body should stay lean; optional or variant material belongs
in directly referenced files loaded only when needed.  
Fail: bloated body, deep chain, or always-loaded optional content.  
Severity: Med.

**S9 — Compatibility**  
If output is consumed downstream, verify the contract.  
Fail: mismatched lookup, missing required fields, incompatible
format, or downstream command cannot find the output.  
Severity: High.

**S10 — Change strategy**  
Must say how to handle existing outputs or instruction files when
rerun or reviewed.  
Fail: always overwrites/regenerates, or lacks no-op / patch /
regenerate decision gate.  
Severity: Med.

**S11 — Level placement**  
Decide whether the anchor belongs in a global or project command
home.

Global: `~/.claude/commands/`, generic, only `~/.claude/...`
paths, useful across projects.

Project: `<project>/.claude/commands/`, project-specific paths,
names, conventions, task queues, or workflows.

Fail: global asset with project-specific content, or project asset
that is fully generic and broadly reusable.  
Severity: Med.

**S12 — Scriptability**  
Flag deterministic, structural, or pattern-matchable workflow
steps where a linter/script would produce the same result at zero
token cost.

`~/.claude/commands/ai-review-command/preflight.py`
already covers anchor file/folder resolution, support path
existence, anchor line count, context-load labeling, and the
first stale-copy scan pass.

Score each flagged step:

- **Effort**: Low / Med / High to automate.
- **Frequency**: per session / per PR / ad hoc.
- **Impact**: Low / Med / High payoff.
- **Verdict**: Script it / Not worth it / Hybrid.

Impact means:

- **Low**: saves little context or catches minor issues.
- **Med**: saves recurring review time or catches common mistakes.
- **High**: prevents frequent drift, broken workflows, or large
  token waste.

Fail: the step is deterministic and frequent enough that token
cost accumulates.  
Severity: Med for one step; High if most of the skill could be
scripted.

## Metrics

Labels are grounded in observed facts; do not estimate.

**Context load**

- **Light**: <=2 files loaded, chain depth <=1, anchor body
  <=100 lines.
- **Moderate**: 3–5 files, chain depth 2, or body 100–200 lines.
- **Heavy**: >5 files, chain depth 3+, body >200 lines, or
  always-loaded optional content.

**Instruction clarity**

Based on S1/S2/S3/S7 findings only:

- **Clear**: all four pass, zero High findings total.
- **Mixed**: 1–2 High or Med findings across S1/S2/S3/S7.
- **Unclear**: 3+ High/Med findings in S1/S2/S3/S7, or S2 fails.
