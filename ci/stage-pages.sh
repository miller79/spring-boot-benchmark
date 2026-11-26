#!/usr/bin/env bash
# Stage only index.html and data.js from bench-data, then replace the chart template with a static
# latest-results table. Preserve raw history unchanged; never follow symlinks or execute data.js.
set -euo pipefail
src="${1:-site}"
dst="${2:-_site}"
mkdir "$dst"
for f in index.html data.js; do
  if [[ -L "$src/$f" || ! -f "$src/$f" || ! -s "$src/$f" ]]; then
    echo "::error::bench-data has no regular, non-empty $f at its root; run the benchmark workflow on main first"
    exit 1
  fi
  cp -- "$src/$f" "$dst/$f"
done
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 -I "$HERE/results_page.py" "$dst/data.js" "$dst/index.html"
