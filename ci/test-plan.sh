#!/usr/bin/env bash
# Scenario tests for plan.sh in a throwaway git repo. Usage: ci/test-plan.sh
set -uo pipefail

PLAN="$(cd "$(dirname "$0")" && pwd)/plan.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"
git init -q . && git config user.email t@t && git config user.name t
commit() { mkdir -p "$(dirname "$1")"; echo "$RANDOM" >> "$1"; git add -A; git commit -qm "$1"; git rev-parse HEAD; }

c0=$(commit README.md)
c1=$(commit spring-boot-benchmark-tomcat/src/A.java)
c2=$(commit spring-boot-benchmark-activemq/pom.xml)
c3=$(commit spring-boot-benchmark-tomcat/src/B.java)

fails=0
# run <name> <expected exit 0|1> <expected output regex> VAR=value...
run() {
  local name="$1" want_rc="$2" want="$3" out rc
  shift 3
  out=$(env -i PATH="$PATH" HOME="$HOME" GITHUB_OUTPUT=/dev/stdout "$@" bash "$PLAN" 2>&1); rc=$?
  if [[ $rc -eq $want_rc && "$out" =~ $want ]]; then echo "ok   $name"
  else echo "FAIL $name (rc=$rc, wanted rc=$want_rc /$want/)"; echo "$out" | sed 's/^/     /'; fails=$((fails + 1)); fi
}
D="EVENT_NAME=workflow_dispatch INPUT_MODULES=tomcat INPUT_PROFILES=plain INPUT_CPU_PROFILES=p06 INPUT_ITERATIONS=5"
d() { run "$1" "$2" "$3" $D "${@:4}"; }

# dispatch validation (later assignments win in env)
d "dispatch ok"                 0 'modules=\["tomcat"\]'
d "iterations=0 rejected"       1 'invalid iterations' INPUT_ITERATIONS=0
d "iterations=000 rejected"     1 'invalid iterations' INPUT_ITERATIONS=000
d "iterations=1000 rejected"    1 'invalid iterations' INPUT_ITERATIONS=1000
d "iterations=1 accepted"       0 'iterations=1 repeats' INPUT_ITERATIONS=1
d "unknown profile rejected"    1 'unknown value: bogus' INPUT_PROFILES=plain,bogus
d "unknown cpu profile rejected" 1 'unknown value: p99' INPUT_CPU_PROFILES=p06,p99
d "unknown module rejected"     1 'unknown module: nope' INPUT_MODULES=tomcat,nope
d "duplicate modules deduped"   0 'modules=\["tomcat","original"\]' INPUT_MODULES=tomcat,original,tomcat
d "duplicate profiles deduped"  0 'profiles=plain,aot cpu_profiles' INPUT_PROFILES=plain,aot,plain
d "all-modules"                 0 'modules=\["original","tomcat","data-jpa","data-rest","activemq","all"\]' INPUT_MODULES=all-modules
d "spike overrides"             0 'mode=spike modules=\["original"\]' INPUT_SPIKE=true

# push: diff base is the last successful run, not github.event.before
run "push since last ok"        0 'modules=\["tomcat","activemq"\]' EVENT_NAME=push LAST_OK_SHA="$c0"
run "push covers cancelled run" 0 'modules=\["activemq","tomcat"\]|modules=\["tomcat","activemq"\]' EVENT_NAME=push LAST_OK_SHA="$c1"
run "push only recent change"   0 'modules=\["tomcat"\]' EVENT_NAME=push LAST_OK_SHA="$c2"
run "push no last ok -> all"    0 'running every module.*modules=\["original"' EVENT_NAME=push LAST_OK_SHA=
run "push unknown sha -> all"   0 'running every module' EVENT_NAME=push LAST_OK_SHA=0123456789012345678901234567890123456789
run "push junk sha -> all"      0 'running every module' EVENT_NAME=push 'LAST_OK_SHA=--help;x'
run "push unset sha -> all"     0 'running every module' EVENT_NAME=push

# pull_request
run "pr smoke"                  0 'mode=smoke modules=\["tomcat","activemq"\]' EVENT_NAME=pull_request BASE_SHA="$c0"
run "unsupported event"         1 'unsupported event' EVENT_NAME=schedule

# a changed module directory that plan.sh does not know must fail, not be dropped (HEAD moves here)
c4=$(commit spring-boot-benchmark-foo/src/A.java)
run "push unknown module dir"   1 'unknown module: foo' EVENT_NAME=push LAST_OK_SHA="$c3"
run "pr unknown module dir"     1 'unknown module: foo' EVENT_NAME=pull_request BASE_SHA="$c3"

echo
if [[ $fails -eq 0 ]]; then echo "all plan scenarios passed"; else echo "$fails scenario(s) failed"; exit 1; fi
