# Commands Preamble

Run this before executing any slash command.

## Agent Delegation

Check whether this command belongs to another agent's domain.
If it does, load that agent before proceeding — don't do the
work yourself. Use `~/.claude/product/README.md`
to resolve the responsible agent.

## Instruction Minimalism

The instruction asset includes its anchor and referenced rubrics, templates,
prompts, and helper scripts.

When creating or reviewing an instruction asset, load
`~/.claude/product/020_conventions/00_md_editing_context.md` and apply its
Trimming Gate to the whole asset, not only changed lines.
