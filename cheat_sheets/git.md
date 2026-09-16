---
owner: bob
description: Common Git commands for daily work.
---

# Git Cheat Sheet

## Setup

```bash
git config --global user.name "Your Name" // Set your Git author name.
git config --global user.email "you@example.com" // Set your Git author email.
```

## Create or clone

```bash
git init // Start a new Git repository here.
git clone <url> // Copy an existing repository.
```

## Daily workflow

```bash
git status // Show changed files and branch state.
git add <file> // Stage one file for commit.
git add . // Stage all current changes.
git commit -m "message" // Save staged changes with a message.
git pull --rebase // Update your branch by replaying your commits.
git push // Upload local commits to the remote.
```

## Inspect changes

```bash
git diff // Show unstaged changes.
git diff --staged // Show staged changes.
git log --oneline --graph --all // Show compact history with branches.
git show <commit> // Show one commit's details.
```

## Branches

```bash
git branch // List local branches.
git switch -c <branch> // Create and move to a new branch.
git switch <branch> // Move to an existing branch.
git merge <branch> // Bring another branch into this one.
git branch -d <branch> // Delete a merged local branch.
```

## Undo

```bash
git restore <file> // Discard unstaged changes.
git restore --staged <file> // Unstage a file.
git commit --amend // Edit the latest commit.
git revert <commit> // Create a reversing commit.
git reset --soft HEAD~1 // Undo the latest commit but keep changes staged.
```

## Rebase onto main

```bash
git fetch origin // Download remote updates.
git switch <feature-branch> // Move to your feature branch.
git rebase origin/main // Replay your work on latest main.
```

If conflicts occur:

```bash
# Edit conflicted files first.
git add <resolved-file> // Stage the conflict resolution.
git rebase --continue // Continue after resolving conflicts.
```

Other options:

```bash
git rebase --abort // Cancel the rebase.
git rebase --skip // Skip the current commit.
```

After rebasing an already-pushed branch:

```bash
git push --force-with-lease // Safely update rewritten remote history.
```

Use `--force-with-lease`, not `--force`; it avoids overwriting unexpected
remote work.

## Fix divergent branches on pull

For a rebase workflow:

```bash
git pull --rebase // Pull updates without a merge commit.
```

Set rebase as the default for this repository:

```bash
git config pull.rebase true // Use rebase pulls in this repository.
```

Or set it for every repository:

```bash
git config --global pull.rebase true // Use rebase pulls everywhere.
```

If conflicts occur, resolve them, stage the files, and continue:

```bash
git add <resolved-file> // Stage the resolved file.
git rebase --continue // Resume the rebase.
```

## Interactive rebase

```bash
git rebase -i HEAD~3 // Edit the last three commits.
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
git push --force-with-lease // Safely update rewritten remote history.
```

## Stash

```bash
git stash // Temporarily save uncommitted changes.
git stash push <file> // Stash changes from one file.
git stash push <folder>/ // Stash changes inside one folder.
git stash push -m "message" <path> // Stash one path with a label.
git stash pop // Reapply the latest stash and remove it.
git stash list // Show saved stashes.
git stash apply stash@{1} // Reapply the previous stash without deleting it.
```

## Remotes

```bash
git remote -v // Show configured remotes.
git fetch origin // Download remote updates.
git push -u origin <branch> // Push and track a branch.
```
