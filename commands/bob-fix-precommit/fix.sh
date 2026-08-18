#!/usr/bin/env bash
# Run pre-commit on a repo, auto-fix what's safe, report the rest.
# Never resolves detect-secrets findings — those need a human decision.
# Usage: fix.sh <repo_root>
#        fix.sh --all <search_root>...
set -uo pipefail

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
  status=0
  for repo in "${repos[@]}"; do
    echo ""
    echo "━━━ $repo ━━━"
    bash "$0" "$repo" || status=1
  done
  exit "$status"
fi

REPO="${1:-.}"
if [[ ! -d "$REPO" ]]; then
  echo "Not a directory: $REPO"
  exit 1
fi
cd "$REPO" || { echo "Cannot cd into: $REPO"; exit 1; }

if [[ ! -f .pre-commit-config.yaml ]]; then
  echo "No .pre-commit-config.yaml in $PWD — not a pre-commit repo."
  exit 1
fi

PC=""
[[ -x .venv/bin/pre-commit ]] && PC=".venv/bin/pre-commit"
[[ -z "$PC" ]] && command -v pre-commit >/dev/null 2>&1 && PC="pre-commit"
if [[ -z "$PC" ]]; then
  echo "No pre-commit found (checked .venv/bin/pre-commit and PATH) in $PWD."
  exit 1
fi

echo "Repo: $PWD"

MAX_PASSES=4
pass=1
OUT=""
STATUS=1
while (( pass <= MAX_PASSES )); do
  echo ""
  echo "── pass $pass ──"
  OUT="$("$PC" run --all-files 2>&1)"
  STATUS=$?
  echo "$OUT"

  if [[ $STATUS -eq 0 ]]; then
    echo ""
    echo "All hooks passed."
    echo ""
    echo "── reference check ──"
    REF_OUT="$(bash ~/.claude/git-hooks/check-references.sh --worktree "$PWD" 2>&1)"
    REF_STATUS=$?
    echo "$REF_OUT"
    exit "$REF_STATUS"
  fi

  # Safe auto-fix: genuinely empty (0-byte) files that check-json flagged.
  # Filled with {} — valid JSON, still empty, no content invented.
  fixed_any=0
  while IFS= read -r f; do
    [[ -f "$f" && ! -s "$f" ]] || continue
    printf '{}\n' > "$f"
    echo "[auto-fix] empty JSON filled with {}: $f"
    fixed_any=1
  done < <(printf '%s\n' "$OUT" | grep -oP '^\S+\.jsonc?(?=: Failed to json decode)')

  [[ $fixed_any -eq 1 ]] || break
  (( pass++ ))
done

echo ""
echo "── Unresolved after auto-fix ──"
printf '%s\n' "$OUT"

if printf '%s\n' "$OUT" | grep -qi "detect-secrets\|Detect secrets"; then
  echo ""
  echo "NOTE: detect-secrets findings above were left untouched. Each one needs a"
  echo "human judgment call — inspect the flagged line, and only if it's a"
  echo "placeholder/schema value (not a real credential) add an inline"
  echo "'pragma: allowlist secret' comment, after confirming with the user."
fi

exit "$STATUS"
