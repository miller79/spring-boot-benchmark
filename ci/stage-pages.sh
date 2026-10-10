#!/usr/bin/env bash
# Stage the Pages artifact: copy exactly index.html and data.js from the bench-data checkout (default
# `site`) into a fresh `_site`. Each must be a regular, non-empty, non-symlink file, so a link on
# bench-data can never pull a runner file into the artifact; anything else on bench-data is ignored.
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
