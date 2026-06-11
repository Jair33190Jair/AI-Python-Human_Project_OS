#!/usr/bin/env bash
# Idempotent setup for the web-render helper.
# Creates .venv, installs requirements, ensures Chromium is present.
# Safe to run on every invocation: fast no-op when already set up.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"
REQ="$HERE/requirements.txt"
STAMP="$VENV/.bootstrap-ok"

# Re-bootstrap if requirements.txt changed since last successful run.
if [[ -f "$STAMP" && "$REQ" -ot "$STAMP" ]]; then
  exit 0
fi

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

pip install --quiet --upgrade pip
pip install --quiet -r "$REQ"
playwright install chromium --quiet

touch "$STAMP"
