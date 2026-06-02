---
description: Rename a file/dir and repair all text references in a git repo. Infers renames from git when no args given.
argument-hint: "[repo_root] [old_path new_path]"
status: draft
owner: bob
---

Rename a file or directory in a git repo and fix every reference to the old
name across all tracked text files.

## Arguments

| Arg | Required | Description |
|---|---|---|
| `repo_root` | no | Repo root path. Defaults to all workspace repos. |
| `old_path` | no* | Old file or directory path (relative to repo root). |
| `new_path` | no* | New file or directory path (relative to repo root). |

*Omit both to infer rename pairs from `git diff HEAD` + staged changes.

## Parse

```
REPO_ROOT="${ARGUMENTS[0]:-}"
OLD_PATH="${ARGUMENTS[1]:-}"
NEW_PATH="${ARGUMENTS[2]:-}"
WORKSPACE_DIRS=<all open workspace root directories from the current session>
```

## Execute

With explicit repo + rename args:

```bash
bash ~/.claude/commands/bob-fix-references/fix.sh "$REPO_ROOT" "$OLD_PATH" "$NEW_PATH"
```

With explicit repo, no rename args (infer from git):

```bash
bash ~/.claude/commands/bob-fix-references/fix.sh "$REPO_ROOT"
```

With no args — run across all workspace repos:

```bash
bash ~/.claude/commands/bob-fix-references/fix.sh --all $WORKSPACE_DIRS
```

## Output

Print the script's stdout verbatim. No additional commentary.

## Hard Rules

- Never operate outside the resolved repo root(s).
- If no renames detected anywhere, say so.
