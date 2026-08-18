#!/usr/bin/env bash
# Shared reference audit for Git hooks and /bob-fix-references.
set -euo pipefail

mode="${1:---cached}"
repo="${2:-$(git rev-parse --show-toplevel)}"

case "$mode" in
  --cached|--worktree) ;;
  *)
    echo "Usage: check-references.sh [--cached|--worktree] [repo]" >&2
    exit 2
    ;;
esac

cd "$repo"

if [[ "$mode" == "--cached" ]]; then
  rename_cmd=(git diff --cached --diff-filter=R --name-status)
  grep_cmd=(git grep --cached -F -l)
else
  rename_cmd=(git diff --diff-filter=R --name-status)
  grep_cmd=(git grep -F -l)
fi

renames=$("${rename_cmd[@]}" | awk '{print $2 "\t" $3}' | sort -u)

found_any=0

if [[ -n "$renames" ]]; then
  while IFS=$'\t' read -r old_path new_path; do
    still_exists=$(git ls-files -- "$old_path" "$old_path/*")
    [[ -n "$still_exists" ]] && continue

    hits=$("${grep_cmd[@]}" -- "$old_path" 2>/dev/null || true)
    if [[ -n "$hits" ]]; then
      if [[ $found_any -eq 0 ]]; then
        echo ""
        echo "  COMMIT BLOCKED — unresolved references after rename"
        echo ""
      fi
      found_any=1
      echo "  Renamed path: $old_path  →  $new_path"
      echo "  Stale references in:"
      while IFS= read -r hit; do
        echo "    $hit"
      done <<< "$hits"
      echo ""
    fi
  done <<< "$renames"
fi

if [[ $found_any -eq 1 ]]; then
  echo "  Fix with: /bob-fix-references"
  echo ""
  exit 1
fi

dead_refs=$(git ls-files \
  | grep -v 'dev_tasks_closed' \
  | xargs grep -hEo '~/.claude/[^`" ;,)]+' 2>/dev/null \
  | grep -vE '<|>|\[|\.\.\.' \
  | sort -u \
  | while read -r p; do
      [[ -e "${p/\~/$HOME}" ]] || echo "  $p"
    done || true)

if [[ -n "$dead_refs" ]]; then
  echo ""
  echo "  COMMIT BLOCKED — dead ~/.claude/ references found"
  echo ""
  echo "$dead_refs"
  echo ""
  echo "  Fix with: /bob-fix-references"
  echo ""
  exit 1
fi

echo "No dead references found."
