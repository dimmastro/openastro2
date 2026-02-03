#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOCALE_DIR="$ROOT_DIR/openastro2/locale"
POT="$LOCALE_DIR/templates/openastro.pot"

if ! command -v msgfmt >/dev/null 2>&1; then
  echo "msgfmt is required but not found. Install gettext." >&2
  exit 1
fi

if ! command -v msginit >/dev/null 2>&1; then
  echo "msginit is required but not found. Install gettext." >&2
  exit 1
fi

for loc_dir in "$LOCALE_DIR"/*; do
  loc="$(basename "$loc_dir")"
  if [[ ! -d "$loc_dir" || "$loc" == "templates" ]]; then
    continue
  fi
  po="$loc_dir/LC_MESSAGES/openastro.po"
  mo="$loc_dir/LC_MESSAGES/openastro.mo"
  mkdir -p "$(dirname "$po")"
  if [[ ! -f "$po" ]]; then
    msginit --input "$POT" --locale "$loc" --no-translator --output-file "$po" >/dev/null 2>&1
  fi
  msgfmt "$po" -o "$mo"
  echo "Compiled $loc"
 done

