#!/bin/sh
# Vérifie que chaque dépendance installée a une licence couverte par licenses/allowlist.txt
set -eu

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
ALLOWLIST_FILE="$ROOT/licenses/allowlist.txt"

if [ ! -f "$ALLOWLIST_FILE" ]; then
  echo "Missing allowlist: $ALLOWLIST_FILE" >&2
  exit 1
fi

ALLOWLIST=$(
  grep -v '^#' "$ALLOWLIST_FILE" | grep -v '^[[:space:]]*$' | paste -sd';' -
)

if [ -z "$ALLOWLIST" ]; then
  echo "Allowlist is empty" >&2
  exit 1
fi

pip install -q pip-licenses

echo "Checking licenses against allowlist (partial match):"
echo "$ALLOWLIST" | tr ';' '\n' | sed 's/^/  - /'

pip-licenses --allow-only="$ALLOWLIST" --partial-match
