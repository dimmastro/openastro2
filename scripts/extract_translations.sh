#!/usr/bin/env bash
# Extract translation strings into openastro.pot from:
# - Python sources (using _ and _t)
# - Selected settings JSON files (settings2.json, settings2-tno.json)
# The settings strings are staged into .tmp/ so xgettext can parse them,
# then source paths are rewritten back to the original JSON locations.
set -euo pipefail

# Project paths
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$ROOT_DIR/openastro2"
LOCALE_DIR="$ROOT_DIR/openastro2/locale"
SETTINGS_DIR="$ROOT_DIR/openastro2/openastro2/settings"
POT="$LOCALE_DIR/templates/openastro.pot"
TMP_DIR="$ROOT_DIR/.tmp"
TMP_SETTINGS_DIR="$TMP_DIR/openastro2"

# Ensure gettext tooling is available.
if ! command -v xgettext >/dev/null 2>&1; then
  echo "xgettext is required but not found. Install gettext." >&2
  exit 1
fi

# Prepare output and temp directories.
mkdir -p "$(dirname "$POT")"
mkdir -p "$TMP_DIR"
mkdir -p "$TMP_SETTINGS_DIR"

# 1) Extract strings from Python sources (_ and _t).
(cd "$ROOT_DIR" && find "openastro2" -name "*.py" -print0 | \
  xargs -0 xgettext \
    --from-code=UTF-8 \
    --language=Python \
    --keyword=_ \
    --keyword=_t \
    --add-comments \
    --output="$POT")

# 2) Extract strings from selected JSON settings files.
#    We generate temporary Python files containing _t("...") calls so xgettext can parse them.
SETTINGS_FILES="$SETTINGS_DIR/settings2.json:$SETTINGS_DIR/settings2-tno.json" \
ROOT_DIR="$ROOT_DIR" \
TMP_SETTINGS_DIR="$TMP_SETTINGS_DIR" \
python3 - <<'PY'
import json
import os
import re
from pathlib import Path

root_dir = Path(os.environ.get("ROOT_DIR", ""))
files_env = os.environ.get("SETTINGS_FILES", "")
settings_files = [Path(p) for p in files_env.split(":") if p]
tmp_settings_dir = Path(os.environ.get("TMP_SETTINGS_DIR", ""))
allowed_keys = {"label", "name", "type", "label_short"}

def walk(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in allowed_keys and isinstance(v, str) and v.strip():
                out.add(v)
            walk(v, out)
    elif isinstance(obj, list):
        for item in obj:
            walk(item, out)

def regex_extract(text, out):
    # JSON5 fallback: capture "key": "value" or 'key': 'value' or key: "value"
    pattern = re.compile(
        r"""(?P<key>label|name|type|label_short)\s*:\s*(?P<val>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')""",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        raw = match.group("val")
        if raw.startswith('"'):
            val = raw[1:-1].encode("utf-8").decode("unicode_escape")
        else:
            val = raw[1:-1].encode("utf-8").decode("unicode_escape")
        if val.strip():
            out.add(val)

def load_json5(path):
    try:
        import json5  # type: ignore
    except Exception:
        return None
    try:
        return json5.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def py_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

target_names = {"settings2.json", "settings2-tno.json"}
for path in settings_files:
    if not path.is_file():
        continue
    if path.suffix not in {".json", ".json5"}:
        continue
    strings = set()
    data = None
    if path.suffix == ".json5":
        data = load_json5(path)
    else:
        data = load_json(path)
    if data is not None:
        walk(data, strings)
    else:
        # Fallback: regex for JSON5 or invalid JSON
        try:
            regex_extract(path.read_text(encoding="utf-8"), strings)
        except Exception:
            strings = set()
    if not strings:
        continue
    # Mirror the original path under .tmp/ so xgettext records useful locations.
    rel_path = path.relative_to(root_dir)
    out_path = tmp_settings_dir / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for value in sorted(strings):
            fh.write(f'_t("{py_escape(value)}")\n')
PY

# 3) Join settings-derived strings into the existing POT.
(
  cd "$ROOT_DIR"
  find ".tmp/openastro2" -type f -print0 | \
    xargs -0 -r xgettext \
      --from-code=UTF-8 \
      --language=Python \
      --keyword=_t \
      --add-comments \
      --join-existing \
      --output="$POT"
)

# 4) Rewrite source locations: replace ".tmp/" prefix with original paths.
POT="$POT" python3 - <<'PY'
import os
from pathlib import Path

pot = Path(os.environ["POT"])
tmp_prefix = "#: .tmp/"
lines = pot.read_text(encoding="utf-8").splitlines()
out = []
for line in lines:
    if line.startswith(tmp_prefix):
        out.append(line.replace(tmp_prefix, "#: "))
    else:
        out.append(line)
pot.write_text("\n".join(out) + "\n", encoding="utf-8")
PY

# 5) Cleanup temporary staged files.
rm -rf "$TMP_SETTINGS_DIR"

echo "Updated template: $POT"
