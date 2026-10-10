#!/usr/bin/env bash
# Scenario tests for maven.sh mode selection and validation. Usage: ci/test-maven.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/mod" "$WORK/bin" "$WORK/empty"
: > "$WORK/mod/mvnw"
: > "$WORK/bin/mvn"; chmod +x "$WORK/bin/mvn"
: > "$WORK/settings.xml"
BASH_BIN="$(command -v bash)"

fails=0
# run <name> <expected rc> <expected output regex> <PATH value> [VAR=value...]
run() {
  local name="$1" want_rc="$2" want="$3" path="$4" out rc
  shift 4
  out=$(env -i PATH="$path" "$@" "$BASH_BIN" -c \
    "source '$HERE/maven.sh' && maven_setup '$WORK/mod' && printf '%s\n' \"\${MVN[*]}\"" 2>&1); rc=$?
  if [[ $rc -eq $want_rc && "$out" =~ $want ]]; then echo "ok   $name"
  else echo "FAIL $name (rc=$rc, wanted rc=$want_rc /$want/)"; echo "$out" | sed 's/^/     /'; fails=$((fails + 1)); fi
}
WITH="$WORK/bin:$PATH"

run "default is wrapper"            0 "^bash $WORK/mod/mvnw\$" "$PATH"
run "empty mode is wrapper"         0 "^bash $WORK/mod/mvnw\$" "$PATH" BENCH_MAVEN_MODE=
run "explicit wrapper"              0 "^bash $WORK/mod/mvnw\$" "$PATH" BENCH_MAVEN_MODE=wrapper
run "wrapper with settings"         0 "^bash $WORK/mod/mvnw -s $WORK/settings.xml\$" "$PATH" BENCH_MAVEN_SETTINGS="$WORK/settings.xml"
run "system uses mvn"               0 '^mvn$' "$WITH" BENCH_MAVEN_MODE=system
run "system with settings"          0 "^mvn -s $WORK/settings.xml\$" "$WITH" BENCH_MAVEN_MODE=system BENCH_MAVEN_SETTINGS="$WORK/settings.xml"
run "system without mvn on PATH"    1 "needs 'mvn' on PATH" "$WORK/empty" BENCH_MAVEN_MODE=system
run "missing settings file"         1 'not a readable file' "$PATH" BENCH_MAVEN_SETTINGS="$WORK/nope.xml"
run "settings is a directory"       1 'not a readable file' "$PATH" BENCH_MAVEN_SETTINGS="$WORK"
run "invalid mode rejected"         1 'invalid BENCH_MAVEN_MODE' "$WITH" BENCH_MAVEN_MODE=docker
run "mode is case sensitive"        1 'invalid BENCH_MAVEN_MODE' "$WITH" BENCH_MAVEN_MODE=System
run "mode injection rejected"       1 'invalid BENCH_MAVEN_MODE' "$WITH" 'BENCH_MAVEN_MODE=system;id'
run "settings path with spaces"     0 'settings with space.xml$' "$WITH" BENCH_MAVEN_MODE=system "BENCH_MAVEN_SETTINGS=$(: > "$WORK/settings with space.xml"; echo "$WORK/settings with space.xml")"

echo
if [[ $fails -eq 0 ]]; then echo "all maven mode scenarios passed"; else echo "$fails scenario(s) failed"; exit 1; fi
