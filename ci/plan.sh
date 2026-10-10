#!/usr/bin/env bash
# Decides what the benchmark workflow runs. Inputs come from the environment
# (set by the workflow, never interpolated into this script). Writes to $GITHUB_OUTPUT:
#   modules (JSON array), mode (full|smoke|spike), profiles, cpu_profiles, iterations, repeats
set -euo pipefail

ALL_MODULES=(original tomcat data-jpa data-rest activemq all)
FULL_PROFILES="plain,aot,cds,aot-cds,aot-caching,aot-aot-caching,alpaquita,native"
OUT="${GITHUB_OUTPUT:-/dev/stdout}"

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
  for m in "${ALL_MODULES[@]}"; do [[ -n "${hit[$m]:-}" ]] && echo "$m"; done
  return 0
}

mode=full profiles="$FULL_PROFILES" cpu_profiles="p06,p10,p20" iterations=30 repeats=1
modules=()

case "${EVENT_NAME:?}" in
  workflow_dispatch)
    valid_list "${INPUT_MODULES:-}" || { echo "invalid modules input" >&2; exit 1; }
    valid_list "${INPUT_PROFILES:-}" || { echo "invalid profiles input" >&2; exit 1; }
    valid_list "${INPUT_CPU_PROFILES:-}" || { echo "invalid cpu_profiles input" >&2; exit 1; }
    [[ "${INPUT_ITERATIONS:-}" =~ ^[0-9]{1,3}$ ]] || { echo "invalid iterations input" >&2; exit 1; }
    if [[ "${INPUT_MODULES}" == "all-modules" ]]; then
      modules=("${ALL_MODULES[@]}")
    else
      IFS=, read -ra modules <<< "$INPUT_MODULES"
    fi
    profiles="$INPUT_PROFILES"; cpu_profiles="$INPUT_CPU_PROFILES"; iterations="$INPUT_ITERATIONS"
    if [[ "${INPUT_SPIKE:-false}" == "true" ]]; then
      mode=spike; modules=(original); profiles="plain,aot-cds,native"; cpu_profiles="p06"; iterations=15; repeats=3
    fi ;;
  pull_request)
    mode=smoke; profiles="plain,aot-cds"; cpu_profiles="p06"; iterations=10
    base="${BASE_SHA:?}"
    mapfile -t changed < <(git diff --name-only "$base" HEAD 2>/dev/null || echo "spring-boot-benchmark-parent/pom.xml")
    mapfile -t modules < <(printf '%s\n' "${changed[@]}" | select_modules) ;;
  push)
    before="${BEFORE_SHA:?}"
    if [[ "$before" =~ ^0+$ ]] || ! git cat-file -e "$before^{commit}" 2>/dev/null; then
      modules=("${ALL_MODULES[@]}")
    else
      mapfile -t changed < <(git diff --name-only "$before" HEAD)
      mapfile -t modules < <(printf '%s\n' "${changed[@]}" | select_modules)
    fi ;;
  *) echo "unsupported event" >&2; exit 1 ;;
esac

for m in "${modules[@]}"; do
  [[ " ${ALL_MODULES[*]} " == *" $m "* ]] || { echo "unknown module: $m" >&2; exit 1; }
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
