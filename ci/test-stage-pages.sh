#!/usr/bin/env bash
# Scenario tests for stage-pages.sh. Usage: ci/test-stage-pages.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fails=0
# check <name> <expected rc> <expected _site listing, space separated> ; the caller prepares $WORK/site
check() {
  local name="$1" want_rc="$2" want_ls="$3" out rc ls_out
  rm -rf "$WORK/_site"
  out=$(bash "$HERE/stage-pages.sh" "$WORK/site" "$WORK/_site" 2>&1); rc=$?
  ls_out=$(ls "$WORK/_site" 2>/dev/null | paste -sd' ' -)
  if [[ $rc -eq $want_rc && "$ls_out" == "$want_ls" ]]; then echo "ok   $name"
  else echo "FAIL $name (rc=$rc, _site='$ls_out')"; echo "$out"; fails=$((fails + 1)); fi
}
fresh() { rm -rf "$WORK/site"; mkdir "$WORK/site"; echo '<html>' > "$WORK/site/index.html"; echo 'window.BENCHMARK_DATA = {}' > "$WORK/site/data.js"; }

fresh; check "both files are staged" 0 "data.js index.html"
fresh; echo secret > "$WORK/site/README.md"; mkdir "$WORK/site/dir"; echo x > "$WORK/site/dir/f"; check "extra files and dirs are not staged" 0 "data.js index.html"
fresh; rm "$WORK/site/data.js"; check "missing data.js fails" 1 "index.html"
fresh; : > "$WORK/site/index.html"; check "empty index.html fails" 1 ""
fresh; rm "$WORK/site/data.js"; echo secret > "$WORK/target"; ln -s "$WORK/target" "$WORK/site/data.js"; check "symlinked data.js is rejected" 1 "index.html"
fresh; rm "$WORK/site/index.html"; mkdir "$WORK/site/index.html"; check "directory named index.html is rejected" 1 ""

echo
if [[ $fails -eq 0 ]]; then echo "all stage-pages scenarios passed"; else echo "$fails scenario(s) failed"; exit 1; fi
