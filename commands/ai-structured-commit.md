---
description: Split a messy worktree into reviewed, isolated commits — one system behavior per commit, gate-checked, verified by actually running each chunk, with explicit go/no-go before every commit.
argument-hint: "[repo-path]"
status: draft
owner: bob
---

# /ai-structured-commit

Turn a worktree with more pending changes than one clean commit into a
sequence of small, tested, explainable commits — done together with the
user, one chunk at a time, never batched.

## Arguments

`$ARGUMENTS` — path to the repo/worktree. Defaults to the current
working directory if omitted.

## Blocked conditions

Stop and print `Blocked: <reason>` if:
- The resolved path is not inside a git repository.
- There are zero pending changes (`git status --porcelain -uall` is
  empty) — nothing to split.

## Resolve

Run:

```bash
python3 ~/.claude/commands/ai-structured-commit/preflight.py $ARGUMENTS
```

Use its JSON output for the repo root, the diff snapshot
(`diff`/`diff_entry_count`), whether the task queue already exists,
and whether a pre-commit hook is present. Stop on `status: blocked`
and print its `blocked` reasons.

This diff snapshot is the plan's baseline — if it changes later (see
"Handling a moving target"), rerun preflight rather than trusting a
stale list.

If `task_queue_exists` is false, run
`python3 ~/.claude/commands/ai-structured-commit/preflight.py $ARGUMENTS --init-task-queue`
before the first chunk that needs to file something into it — it
writes the standard schema block, not a freehand header.

## Plan the split

Group the full diff into chunks where each chunk changes **one
system behavior** and can be tested with **one focused command or
manual check**. A commit whose summary needs "and" more than twice is
too big — split it further.

Order chunks by dependency, not by file type alone — a chunk that
calls code another chunk introduces must land after it. When there's
no clear dependency from the diff itself, default to Steve's build
order (`~/.claude/product/010_agents/010_strategy_steve/steve.md`): product
decision → data model → backend contract → backend implementation →
backend tests → minimal UI → end-to-end check → infra/deploy →
compliance documents → public copy.

Track the chunk breakdown with `TodoWrite` — one todo per chunk,
marked `in_progress`/`completed` as the loop advances. This is
session-scoped tracking, not a repo artifact: nothing to create,
maintain, or clean up afterward. Show the full breakdown to the user
before starting the per-chunk loop. Get agreement on the shape of the
split before diving into individual gates — replanning after gate 3
of chunk 1 wastes both your time.

If a file's diff contains two hunks that logically belong to
different chunks (e.g. one hunk fixes a typo, another documents a new
command from a different chunk), split by hunk rather than forcing
the whole file into one chunk or the other.

## The nine gates

Apply all nine to every chunk before it is staged. If a gate fails,
propose the specific fix to the user and get explicit approval before
applying it — never apply a gate fix autonomously, and never carry a
failure forward as "fix later."

1. **File-purpose comment** — every new or modified file in the
   chunk carries a short one-line purpose comment/docstring at its
   top.
2. **References correct — hard block.** Use preflight's
   `pre_commit_hook` result: if set, that hook may already catch stale
   references after a rename and dead absolute links automatically —
   don't assume what it covers or duplicate it. It will **not** catch
   project-internal doc cross-links (README → schema doc, task-queue
   links, config values another file expects to match). Check those
   manually for every doc/config the chunk touches. Any broken
   reference — hook-caught or manual — must be fixed before the
   commit, never left as a follow-up task.
3. **Structure sanity** — is each file in the chunk in the right
   place per existing conventions? No stray duplicates, no file that
   should have been a rename instead of a new file.
4. **No redundancy or contradiction** — no duplicate logic doing the
   same job two ways, no doc that now says something different from
   another doc about the same fact.
5. **Documentation maintained** — data model changed → the project's
   schema doc; sensitive/security flow changed → its doc; remaining
   work → the task queue.
6. **Understandable to a newcomer** — the commit message **body**
   (not just its one-line summary) states what's actually in the
   chunk and why it was necessary. This is the durable change record
   — no separate report file. `git log` / `git show <sha>` is the
   audit trail; keep it complete enough to read on its own.
7. **You always know what's going on** — nothing is staged or
   committed until the user has seen the include list, the
   explanation, and the check output.
8. **No secrets** — before staging, confirm the diff contains no
   credentials, API keys, tokens, or other secrets.
9. **Is this really necessary** — delete anything not adding enough
   value to be read in the future, anything unused, anything that
   only adds decoration or confusion. Strict, tight pass. Keep the
   files and the system lean, simple, and effective.

## Per-chunk loop

Repeat for every chunk, in dependency order:

1. Show the chunk's include list and its "what's actually in this
   chunk" / "why separate" explanation.
2. Run gates 1, 3, 4, 5, 8, 9 by reading the actual files. For any
   finding, propose the fix to the user and get explicit go-ahead
   before applying it — do not fix autonomously. Only move to checks
   once every finding in this chunk is either approved-and-applied or
   explicitly waved off by the user.
3. Run the chunk's real check command — actually execute it. If a
   tool seems unavailable (interpreter not on `PATH`, package missing,
   credential helper broken), look for a scoped workaround (source a
   version manager, install the missing package into the project's
   existing environment, use a temporary isolated config) before
   reporting the check as unverifiable. Never work around something
   that would touch real or production state to make a check pass.
4. Check whether the chunk's check command has a narrower scope than
   what CI or other tooling will actually run for real (e.g. a linter
   run from a subdirectory versus from the repo root, a test command
   that excludes a folder CI includes). If so, run the broader scope
   too — the gap is exactly where regressions hide.
5. Prefer running the change end-to-end (real migration, CLI call, or
   build) over unit tests alone for migrations, CLI wiring, and
   path-dependent code — synthetic fixtures can pass while the real
   path is broken.
6. If this surfaces test/code drift (the code changed and its tests
   didn't, or vice versa), do not silently pick a side. Determine
   which one is stale, confirm the intended behavior with the user,
   then fix the other to match — and add a test for the specific gap
   if none covers it.
7. If this surfaces duplicated logic across independent,
   deliberately-standalone components, do not force a shared
   abstraction preemptively. File it as a task in the project's task
   queue with the real scope (exact file list, occurrence count), and
   only extract once a concrete threshold is crossed and the user
   agrees — ask rather than deciding unilaterally.
8. If the chunk touches real business/customer data (renamed IDs,
   changed labels, corrected values), treat it as the user's judgment
   call, not something to commit silently. Grep for other references
   to the old value before assuming a rename is safe, and surface any
   break found before asking.
9. File any deferred work this chunk surfaced but doesn't need to
   block on (missing test coverage, cleanup, real-world/paperwork
   follow-ups such as signatures or confirmations someone needs to
   obtain) into the project's task queue — addressed to whichever
   person or agent actually needs to act, not only to a dev agent.
   Never do the deferred work now, and never leave it undiscoverable.
10. Present the final include list, explanation, and check output.
    Ask for explicit go/no-go before staging anything.
11. On go, stage **exactly** this chunk's file list — never `git add
    -A`, never a broad glob. Run
    `python3 ~/.claude/commands/ai-structured-commit/preflight.py $ARGUMENTS --verify-staged <file1> <file2> ...`
    with the intended list; it exits non-zero on any mismatch. If it
    reports a mismatch, diagnose why (a stale index, leftover staged
    content from before this session) before proceeding — never
    commit an unexplained diff.
12. Commit with a full message: a short subject plus a body stating
    what changed and why, per gate 6.
13. Move to the next chunk.

## Handling a moving target

The file scope is frozen to the initial preflight diff snapshot — work
in parallel with the user and other sessions rather than trying to
absorb everything moving in the worktree.

- **Files not in the original snapshot** (new files, or files nothing
  in the snapshot referenced) that appear mid-session belong to
  whoever is producing them. Leave them unstaged and out of every
  chunk; don't pull them in, don't ask about deleting them — just
  acknowledge them to the user and note them under "Remaining
  unstaged" in the final output.
- **Files already in the snapshot** that change further mid-session
  (parallel edits by the user, another process, or a prior automated
  run) do need reconciling: stop, re-diff just those specific files
  against the current worktree, and adjust the affected chunk(s)
  accordingly. Don't expand into files outside the original snapshot
  to do this.
- If a commit already landed outside this session covering part of
  the plan, acknowledge it explicitly and adjust the remaining chunk
  plan instead of ignoring it or re-doing it.

Update the `TodoWrite` chunk list to match reality before resuming the
loop.

## Output

After each chunk commits:

```text
Chunk <n>/<total>: <name>
Files: <count>
Checks: <pass/fail summary — what was actually run>
Committed: <sha> <subject>
```

After the last chunk:

```text
Structured commit complete: <n> chunks, <n> commits
Deferred: <n> tasks filed in <task queue path>
Remaining unstaged: <what's left and why, or "none">
```

## Hard rules

- Never `git add -A` or stage by broad glob — always an explicit,
  verified file list.
- Never commit before the user has seen that chunk's include list,
  explanation, and check output.
- Never silently work around a check-tool gap in a way that touches
  real or production state.
- Never force a shared abstraction across independent components
  without the user's agreement — file it as a task instead.
- Never rename or change real business/customer data without asking.
- Never push, force-push, or amend a prior commit unless the user
  explicitly asks.
