#!/usr/bin/env bash
# Source this file, then call: maven_setup <module-dir>   (returns non-zero with a message on bad input)
# It fills the array MVN with the command to run Maven for that module. Use: "${MVN[@]}" -B ... goals
#
# Environment:
#   BENCH_MAVEN_MODE      wrapper (default) | system
#                         wrapper: run the module's mvnw (it downloads Maven itself)
#                         system:  run the `mvn` already on PATH, for environments where the wrapper
#                                  cannot download Maven (for example behind a corporate mirror)
#   BENCH_MAVEN_SETTINGS  optional path to a Maven settings file, passed as `-s` in either mode

maven_setup() {
  local module_dir="${1:?module dir}"
  local mode="${BENCH_MAVEN_MODE:-wrapper}"
  local settings="${BENCH_MAVEN_SETTINGS:-}"

  MVN=()
  case "$mode" in
    wrapper)
      # Run through bash: the wrappers are committed as mode 100644, so executing them directly fails (rc=126).
      [[ -f "$module_dir/mvnw" ]] || { echo "ERROR: $module_dir/mvnw not found" >&2; return 1; }
      MVN=(bash "$module_dir/mvnw") ;;
    system)
      command -v mvn > /dev/null 2>&1 \
        || { echo "ERROR: BENCH_MAVEN_MODE=system needs 'mvn' on PATH, but it was not found" >&2; return 1; }
      MVN=(mvn) ;;
    *)
      echo "ERROR: invalid BENCH_MAVEN_MODE (allowed: wrapper, system)" >&2; return 1 ;;
  esac

  if [[ -n "$settings" ]]; then
    [[ -f "$settings" && -r "$settings" ]] \
      || { echo "ERROR: BENCH_MAVEN_SETTINGS is not a readable file: $settings" >&2; return 1; }
    MVN+=(-s "$settings")
  fi
  return 0
}
