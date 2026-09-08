---
owner: bob
description: Common Git commands for daily work.
---

# Git Cheat Sheet

## Setup

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Create or clone

```bash
git init
git clone <url>
```

## Daily workflow

```bash
git status
git add <file>
git add .
git commit -m "message"
git pull --rebase
git push
```

## Inspect changes

```bash
git diff
git diff --staged
git log --oneline --graph --all
git show <commit>
```

## Branches

```bash
git branch
git switch -c <branch>
git switch <branch>
git merge <branch>
git branch -d <branch>
```

## Undo

| Command | Use |
|---|---|
| `git restore <file>` | Discard unstaged changes. |
| `git restore --staged <file>` | Unstage a file. |
| `git commit --amend` | Edit the latest commit. |
| `git revert <commit>` | Create a commit that reverses another commit. |
| `git reset --soft HEAD~1` | Undo the latest commit but keep changes staged. |

## Rebase onto main

```bash
git fetch origin
git switch <feature-branch>
git rebase origin/main
```

If conflicts occur:

```bash
# Edit conflicted files first.
git add <resolved-file>
git rebase --continue
```

Other options:

```bash
git rebase --abort
git rebase --skip
```

After rebasing an already-pushed branch:

```bash
git push --force-with-lease
```

Use `--force-with-lease`, not `--force`; it avoids overwriting unexpected
remote work.

## Fix divergent branches on pull

For a rebase workflow:

```bash
git pull --rebase
```

Set rebase as the default for this repository:

```bash
git config pull.rebase true
```

Or set it for every repository:

```bash
git config --global pull.rebase true
```

If conflicts occur, resolve them, stage the files, and continue:

```bash
git add <resolved-file>
git rebase --continue
```

## Interactive rebase

```bash
git rebase -i HEAD~3
```

| Action | Meaning |
|---|---|
| `pick` | Keep commit. |
| `reword` | Change commit message. |
| `edit` | Modify commit. |
| `squash` | Combine with previous commit. |
| `drop` | Remove commit. |

Then push if the old history was already remote:

```bash
git push --force-with-lease
```

## Stash

```bash
git stash
git stash pop
git stash list
```

## Remotes

```bash
git remote -v
git fetch origin
git push -u origin <branch>
```
