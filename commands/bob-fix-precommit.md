---
description: Run pre-commit on a git repo and resolve everything it fires, where safe to auto-fix. Never auto-allowlists secrets.
argument-hint: "[repo_root]"
status: draft
owner: bob
---

Run pre-commit on a git repo, auto-fix what's safe, and surface
everything else for a human call — never guessed.

## Arguments

| Arg | Required | Description |
|---|---|---|
| `repo_root` | no | Repo root path. Defaults to `.`. |

## Execute

```bash
bash ~/.claude/commands/bob-fix-precommit/fix.sh "$REPO_ROOT"
```

With no args — run across all workspace repos:

```bash
bash ~/.claude/commands/bob-fix-precommit/fix.sh --all $WORKSPACE_DIRS
```

The script:

- Runs `pre-commit run --all-files` up to 4 times, so auto-fixing
  hooks (trailing-whitespace, end-of-file-fixer, `ruff --fix`, ...)
  converge across passes.
- Fills genuinely empty (0-byte) files that `check-json` flags with
  `{}` — valid JSON, still empty, no content invented.
- Leaves every `detect-secrets` finding untouched and prints a note
  after the run.

## Detect-secrets findings

Never add `pragma: allowlist secret` on the script's say-so. For
each finding printed:

1. Read the flagged line in context.
2. Judge whether it's a real credential or a placeholder/schema
   example value.
3. If it's a placeholder, tell the user what you found and why you
   believe it's a false positive, then ask for confirmation before
   adding the inline `pragma: allowlist secret` comment. The pragma
   must be the first thing after the comment marker — start a fresh
   `// pragma: allowlist secret` (or `# pragma: allowlist secret`)
   rather than appending it after existing comment text, or
   detect-secrets won't recognize it.
4. If it looks like a real credential, stop and flag it — do not
   edit, do not commit.

## Output

Print the script's stdout verbatim, then report any detect-secrets
findings and other unresolved hook failures with your assessment.

## Hard Rules

- Never operate outside the resolved repo root(s).
- Never add a `pragma: allowlist secret` comment without explicit
  user confirmation for that specific finding.
- Never invent content for non-empty malformed files — report them,
  don't guess.
