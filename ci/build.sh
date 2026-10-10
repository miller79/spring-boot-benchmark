#!/usr/bin/env bash
# Builds one image per profile for a module (sequentially) and records disk use.
# Usage: build.sh <module> <source-root> <side: head|base> <profiles,comma,separated> <results-dir>
# Image names must match image_name() in bench.py.
set -euo pipefail

MODULE="${1:?module}"
ROOT="${2:?source root}"
SIDE="${3:?side}"
PROFILES="${4:?profiles}"
OUT="${5:?results dir}"

[[ "$SIDE" == "head" ]] && SUFFIX="" || SUFFIX="-$SIDE"
mkdir -p "$OUT"
IFS=, read -ra LIST <<< "$PROFILES"

for profile in "${LIST[@]}"; do
  name="spring-boot-benchmark-$MODULE-$profile$SUFFIX"
  echo "::group::build $SIDE $MODULE $profile"
  start=$(date +%s)
  "$ROOT/spring-boot-benchmark-$MODULE/mvnw" -B -ntp -DskipTests \
    -f "$ROOT/spring-boot-benchmark-$MODULE/pom.xml" "-P$profile" \
    clean spring-boot:build-image "-DimageName=$name"
  echo "built $name in $(( $(date +%s) - start ))s"
  echo "::endgroup::"
  # Buildpack cache volumes and dangling layers are not needed after the image exists.
  docker volume prune -f > /dev/null
  docker image prune -f > /dev/null
  { echo "== after $SIDE $MODULE $profile ($(date -u +%H:%M:%S)), build $(( $(date +%s) - start ))s"; df -h / | tail -1; docker system df; } | tee -a "$OUT/disk.log"
done
