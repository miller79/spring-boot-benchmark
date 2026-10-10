#!/usr/bin/env bash
# Decides what the benchmark workflow runs. Inputs come from the environment
# (set by the workflow, never interpolated into this script). On push, LAST_OK_SHA (head of the last
# successful push run; empty when unknown) is the diff base so no module is lost to cancelled or
# failed runs; when it is unknown or not an ancestor of HEAD every module runs. Writes to $GITHUB_OUTPUT:
#   modules (JSON array), mode (full|smoke|spike), profiles, cpu_profiles, iterations, repeats
set -euo pipefail

ALL_MODULES=(original tomcat data-jpa data-rest activemq all)
FULL_PROFILES="plain,aot,cds,aot-cds,aot-caching,aot-aot-caching,alpaquita,native"
OUT="${GITHUB_OUTPUT:-/dev/stdout}"

ALL_CPU_PROFILES="p06,p10,p20"

# Every comma-separated item of $1 must be one of the comma-separated names in $2.
in_set() {
  local item
  local -a items
  IFS=, read -ra items <<< "$1"
  for item in "${items[@]}"; do
    [[ ",$2," == *",$item,"* ]] || { echo "unknown value: $item" >&2; return 1; }
  done
}

# Echo the comma list $1 without duplicates, order preserved.
dedupe_list() {
  local -a items
  IFS=, read -ra items <<< "$1"
  printf '%s\n' "${items[@]}" | awk '!seen[$0]++' | paste -sd, -
}

valid_list() { [[ "$1" =~ ^[a-z0-9]+(-[a-z0-9]+)*(,[a-z0-9]+(-[a-z0-9]+)*)*$ ]]; }

# Echo the module names touched by the changed files read from stdin; "all" means every module.
select_modules() {
  local f m
  declare -A hit=()
  while IFS= read -r f; do
    case "$f" in
      spring-boot-benchmark-parent/*|ci/*|.github/workflows/benchmark.yml)
        printf '%s\n' "${ALL_MODULES[@]}"; return ;;
      spring-boot-benchmark-*/src/*|spring-boot-benchmark-*/pom.xml|spring-boot-benchmark-*/.mvn/*)
        m="${f#spring-boot-benchmark-}"; m="${m%%/*}"
        hit[$m]=1 ;;
    esac
  done
  for m in "${ALL_MODULES[@]}"; do
    [[ -n "${hit[$m]:-}" ]] && echo "$m"
    unset "hit[$m]"
  done
  # Anything left is a module directory that is not benchmarked; the check below fails on it.
  for m in "${!hit[@]}"; do echo "$m"; done
  return 0
}

mode=full profiles="$FULL_PROFILES" cpu_profiles="$ALL_CPU_PROFILES" iterations=30 repeats=1
modules=()

case "${EVENT_NAME:?}" in
  workflow_dispatch)
    valid_list "${INPUT_MODULES:-}" || { echo "invalid modules input" >&2; exit 1; }
    valid_list "${INPUT_PROFILES:-}" || { echo "invalid profiles input" >&2; exit 1; }
    valid_list "${INPUT_CPU_PROFILES:-}" || { echo "invalid cpu_profiles input" >&2; exit 1; }
    [[ "${INPUT_ITERATIONS:-}" =~ ^[1-9][0-9]{0,2}$ ]] || { echo "invalid iterations input (1-999)" >&2; exit 1; }
    in_set "$INPUT_PROFILES" "$FULL_PROFILES" || { echo "invalid profiles input" >&2; exit 1; }
    in_set "$INPUT_CPU_PROFILES" "$ALL_CPU_PROFILES" || { echo "invalid cpu_profiles input" >&2; exit 1; }
    if [[ "${INPUT_MODULES}" == "all-modules" ]]; then
      modules=("${ALL_MODULES[@]}")
    else
      mapfile -t modules < <(dedupe_list "$INPUT_MODULES" | tr ',' '\n')
    fi
    profiles="$(dedupe_list "$INPUT_PROFILES")"; cpu_profiles="$(dedupe_list "$INPUT_CPU_PROFILES")"; iterations="$INPUT_ITERATIONS"
    if [[ "${INPUT_SPIKE:-false}" == "true" ]]; then
      mode=spike; modules=(original); profiles="plain,aot-cds,native"; cpu_profiles="p06"; iterations=15; repeats=3
    fi ;;
  pull_request)
    mode=smoke; profiles="plain,aot-cds"; cpu_profiles="p06"; iterations=10
    base="${BASE_SHA:?}"
    mapfile -t changed < <(git diff --name-only "$base" HEAD 2>/dev/null || echo "spring-boot-benchmark-parent/pom.xml")
    mapfile -t modules < <(printf '%s\n' "${changed[@]}" | select_modules) ;;
  push)
    last="${LAST_OK_SHA:-}"
    if [[ ! "$last" =~ ^[0-9a-f]{40}$ ]] || ! git cat-file -e "$last^{commit}" 2>/dev/null \
       || ! git merge-base --is-ancestor "$last" HEAD 2>/dev/null; then
      echo "no usable last successful run (${last:-none}); running every module"
      modules=("${ALL_MODULES[@]}")
    else
      mapfile -t changed < <(git diff --name-only "$last" HEAD)
      mapfile -t modules < <(printf '%s\n' "${changed[@]}" | select_modules)
    fi ;;
  *) echo "unsupported event" >&2; exit 1 ;;
esac

for m in "${modules[@]}"; do
  [[ " ${ALL_MODULES[*]} " == *" $m "* ]] || { echo "unknown module: $m (add it to ALL_MODULES in ci/plan.sh, MODULES in ci/bench.py and the allowlist in ci/report.py)" >&2; exit 1; }
done

json="["
for m in "${modules[@]}"; do json+="\"$m\","; done
json="${json%,}]"
{
  echo "modules=$json"
  echo "mode=$mode"
  echo "profiles=$profiles"
  echo "cpu_profiles=$cpu_profiles"
  echo "iterations=$iterations"
  echo "repeats=$repeats"
} >> "$OUT"
echo "mode=$mode modules=$json profiles=$profiles cpu_profiles=$cpu_profiles iterations=$iterations repeats=$repeats"
