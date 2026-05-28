#!/usr/bin/env bash
# Rename a file/dir and repair all text references in a git repo.
# Usage: fix.sh <repo_root> [<old_path> <new_path>]
set -euo pipefail

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
    { git diff --name-status HEAD 2>/dev/null
      git diff --name-status --cached 2>/dev/null; } \
    | awk -F'\t' '$1 ~ /^R/ { print $2"\t"$3 }' \
    | sort -u
  )

  # Also catch manual moves: deleted tracked file + untracked file with same basename
  declare -A _seen
  for p in "${OLD_PATHS[@]+"${OLD_PATHS[@]}"}"; do _seen["$p"]=1; done
  while IFS= read -r deleted; do
    [[ -n "${_seen[$deleted]:-}" ]] && continue
    base="$(basename "$deleted")"
    match="$(git ls-files --others --exclude-standard \
      | awk -v b="$base" -F'/' 'NF && $NF == b { print; exit }')"
    if [[ -n "$match" ]]; then
      OLD_PATHS+=("$deleted")
      NEW_PATHS+=("$match")
    fi
  done < <(git ls-files --deleted)
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
  OLD_BASE="$(basename "$OLD")"
  NEW_BASE="$(basename "$NEW")"

  printf '\n[rename] %s  →  %s\n' "$OLD" "$NEW"

  if [[ -e "$OLD" ]]; then
    mkdir -p "$(dirname "$NEW")"
    git mv -- "$OLD" "$NEW" 2>/dev/null || mv -- "$OLD" "$NEW"
    (( FILES_RENAMED++ )) || true
  fi

  while IFS= read -r f; do
    [[ -f "$f" && -r "$f" ]] || continue
    grep -qI '' "$f" 2>/dev/null || continue  # skip binary

    BEFORE="$(md5sum "$f")"
    [[ "$OLD" != "$OLD_BASE" ]] && sed -i "s|${OLD}|${NEW}|g" "$f"
    sed -i "s|${OLD_BASE}|${NEW_BASE}|g" "$f"
    AFTER="$(md5sum "$f")"

    [[ "$BEFORE" != "$AFTER" ]] && {
      printf '  refs: %s\n' "$f"
      (( FILES_UPDATED++ )) || true
    }
  done < <(git ls-files)
done
fi

printf '\nDone: %d file(s) renamed, %d file(s) updated.\n' "$FILES_RENAMED" "$FILES_UPDATED"

# Dead-ref audit — report ~/.claude/ paths that exist in tracked files but not on disk
echo ""
dead=()
while IFS= read -r p; do
  [[ -e "${p/\~/$HOME}" ]] || dead+=("$p")
done < <(git ls-files | grep -v 'ai_tasks_closed' | xargs grep -hEo '~/.claude/[^`" )]+' 2>/dev/null | grep -vE '<|>|\[|\.\.\.' | sort -u)

if [[ ${#dead[@]} -gt 0 ]]; then
  echo "Dead references (need manual fix):"
  for p in "${dead[@]}"; do
    echo "  $p"
  done
else
  echo "No dead references found."
fi
