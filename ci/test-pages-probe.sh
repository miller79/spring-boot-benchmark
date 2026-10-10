#!/usr/bin/env bash
# Scenario tests for pages-probe.sh with a stub `gh`. Usage: ci/test-pages-probe.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/bin"
# The stub exits $STUB_RC and prints $STUB_ERR on stderr, like `gh api` does for an HTTP error.
cat > "$WORK/bin/gh" <<'STUB'
#!/usr/bin/env bash
[[ -n "${STUB_ERR:-}" ]] && echo "$STUB_ERR" >&2
exit "${STUB_RC:-0}"
STUB
chmod +x "$WORK/bin/gh"

fails=0
# run <name> <expected rc> <expect present=true in output: yes|no> <STUB_RC> <STUB_ERR>
run() {
  local name="$1" want_rc="$2" want_present="$3" rc_stub="$4" err="$5" out rc got=no
  : > "$WORK/output"
  out=$(env PATH="$WORK/bin:$PATH" GITHUB_REPOSITORY=o/r GITHUB_OUTPUT="$WORK/output" STUB_RC="$rc_stub" STUB_ERR="$err" \
    bash "$HERE/pages-probe.sh" 2>&1); rc=$?
  grep -qx 'present=true' "$WORK/output" && got=yes
  if [[ $rc -eq $want_rc && "$got" == "$want_present" ]]; then echo "ok   $name"
  else echo "FAIL $name (rc=$rc, present=$got)"; echo "$out" | sed 's/^/     /'; fails=$((fails + 1)); fi
}

run "branch exists: deploy" 0 yes 0 ""
run "HTTP 404: skip, not an error" 0 no 1 "gh: Not Found (HTTP 404)"
run "HTTP 403 (token or rate limit) fails" 1 no 1 "gh: Resource not accessible by integration (HTTP 403)"
run "HTTP 500 fails" 1 no 1 "gh: Server Error (HTTP 500)"
run "network error fails" 1 no 1 "error connecting to api.github.com"

echo
if [[ $fails -eq 0 ]]; then echo "all pages-probe scenarios passed"; else echo "$fails scenario(s) failed"; exit 1; fi
