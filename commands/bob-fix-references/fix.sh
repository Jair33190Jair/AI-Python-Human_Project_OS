#!/usr/bin/env bash
# Rename a file/dir and repair all text references in a git repo.
# Usage: fix.sh <repo_root> [<old_path> <new_path>]
#        fix.sh --all <search_root>...
set -euo pipefail

if [[ "${1:-}" == "--all" ]]; then
  shift
  search_roots=("${@:-.}")
  repos=()
  while IFS= read -r d; do
    repos+=("${d%/.git}")
  done < <(find "${search_roots[@]}" -maxdepth 6 -name .git -type d 2>/dev/null | grep -v '/.git/' | sort)
  if [[ ${#repos[@]} -eq 0 ]]; then
    echo "No git repos found under: ${search_roots[*]}"
    exit 0
  fi
  for repo in "${repos[@]}"; do
    echo ""
    echo "━━━ $repo ━━━"
    bash "$0" "$repo" || true
  done
  exit 0
fi

REPO="${1:-.}"
shift || true
cd "$REPO"

OLD_PATHS=()
NEW_PATHS=()

if [[ $# -ge 2 ]]; then
  OLD_PATHS+=("$1")
  NEW_PATHS+=("$2")
else
  while IFS=$'\t' read -r old new; do
    OLD_PATHS+=("$old")
    NEW_PATHS+=("$new")
  done < <(
    { git -c core.quotePath=false diff --name-status HEAD 2>/dev/null
      git -c core.quotePath=false diff --name-status --cached 2>/dev/null; } \
    | awk -F'\t' '$1 ~ /^R/ { print $2"\t"$3 }' \
    | sort -u
  )

fi

if [[ ${#OLD_PATHS[@]} -eq 0 ]]; then
  echo "No renames to process."
fi

FILES_RENAMED=0
FILES_UPDATED=0

if [[ ${#OLD_PATHS[@]} -gt 0 ]]; then
for i in "${!OLD_PATHS[@]}"; do
  OLD="${OLD_PATHS[$i]}"
  NEW="${NEW_PATHS[$i]}"

  printf '\n[rename] %s  →  %s\n' "$OLD" "$NEW"

  if [[ -e "$OLD" ]]; then
    mkdir -p "$(dirname "$NEW")"
    git mv -- "$OLD" "$NEW" 2>/dev/null || mv -- "$OLD" "$NEW"
    (( FILES_RENAMED++ )) || true
  fi

  # Full path replacement
  while IFS= read -r f; do
    [[ -f "$f" && -r "$f" ]] || continue
    grep -qI '' "$f" 2>/dev/null || continue  # skip binary

    BEFORE="$(md5sum "$f")"
    OLD="$OLD" NEW="$NEW" perl -pi -e '
      BEGIN { $o = quotemeta($ENV{OLD}); $n = $ENV{NEW}; }
      s/$o/$n/g;
    ' -- "$f"
    AFTER="$(md5sum "$f")"

    [[ "$BEFORE" != "$AFTER" ]] && {
      printf '  refs: %s\n' "$f"
      (( FILES_UPDATED++ )) || true
    }
  done < <(git ls-files)
done
fi

printf '\nDone: %d file(s) renamed, %d file(s) updated.\n' "$FILES_RENAMED" "$FILES_UPDATED"

hook=""
[[ -x git-hooks/pre-commit ]] && hook="git-hooks/pre-commit"
[[ -z "$hook" && -x .git/hooks/pre-commit ]] && hook=".git/hooks/pre-commit"
if [[ -z "$hook" ]]; then
  global_hooks=$(git config --get core.hooksPath 2>/dev/null || true)
  [[ -n "$global_hooks" && -x "$global_hooks/pre-commit" ]] && hook="$global_hooks/pre-commit"
fi
if [[ -n "$hook" ]]; then
  echo ""
  echo "Running pre-commit hook..."
  bash "$hook"
fi

echo ""
bash ~/.claude/git-hooks/check-references.sh --worktree "$PWD"
