#!/usr/bin/env bash
# Scenario tests for landed.sh (the publish-error gate) with a stub `gh`. Usage: ci/test-landed.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/bin"
# `git/ref` answers the next line of $STUB_HEADS (the last one repeats; "FAIL" makes gh fail);
# `contents` prints $STUB_DATA, and fails when it is empty.
cat > "$WORK/bin/gh" <<'STUB'
#!/usr/bin/env bash
n=$(cat "$STUB_STATE" 2>/dev/null || echo 0)
case "$*" in
  *git/ref/heads/bench-data*)
    n=$((n + 1)); echo "$n" > "$STUB_STATE"
    head=$(sed -n "${n}p" "$STUB_HEADS"); [[ -z "$head" ]] && head=$(tail -n 1 "$STUB_HEADS")
    [[ "$head" == FAIL ]] && exit 1
    echo "$head" ;;
  *contents/*) [[ -n "${STUB_DATA:-}" ]] || exit 1; printf '%s' "$STUB_DATA" ;;
  *) exit 2 ;;
esac
STUB
chmod +x "$WORK/bin/gh"

SHA=aaaa1111
entry() { printf 'window.BENCHMARK_DATA = {"entries":{"spring-boot-benchmark-tomcat":[{"commit":{"id":"%s"}}]}}' "$1"; }
fails=0
# run <name> <expected rc> <heads, space separated> <data.js text> [expected output substring]
run() {
  local name="$1" want_rc="$2" heads="$3" data="$4" want_out="${5:-}" out rc
  tr ' ' '\n' <<< "$heads" > "$WORK/heads"; : > "$WORK/state"
  out=$(env PATH="$WORK/bin:$PATH" STUB_HEADS="$WORK/heads" STUB_STATE="$WORK/state" STUB_DATA="$data" \
    GITHUB_REPOSITORY=o/r GITHUB_SHA=$SHA BENCH_NAME=spring-boot-benchmark-tomcat BEFORE_SHA=old1 \
    DATA_FILE=dev/bench/data.js MODULE=tomcat BENCH_OUTCOME=failure LANDED_SLEEP=0 \
    GITHUB_STEP_SUMMARY="$WORK/summary" bash "$HERE/landed.sh" 2>&1); rc=$?
  if [[ $rc -eq $want_rc && "$out" == *"$want_out"* ]]; then echo "ok   $name"
  else echo "FAIL $name (rc=$rc, wanted rc=$want_rc)"; echo "$out" | sed 's/^/     /'; fails=$((fails + 1)); fi
}

run "head moved and entry present (alert path) is green" 0 "new1" "$(entry $SHA)" "history landed on bench-data@new1"
run "head unchanged (push error) is red" 1 "old1" "$(entry $SHA)" "was not published"
run "head moved but no entry for this commit is red" 1 "new1" "$(entry other)" "was not published"
run "re-run with a stale entry and an unchanged head is red" 1 "old1" "$(entry $SHA)" "was not published"
run "ref lookup fails every time is red" 1 "FAIL" "$(entry $SHA)" "was not published"
run "contents lookup fails is red" 1 "new1" "" "was not published"
run "push lands on the second attempt is green" 0 "old1 new1" "$(entry $SHA)" "history landed"
run "ref lookup fails once, then lands, is green" 0 "FAIL new1" "$(entry $SHA)" "history landed"

echo
if [[ $fails -eq 0 ]]; then echo "all landed scenarios passed"; else echo "$fails scenario(s) failed"; exit 1; fi
