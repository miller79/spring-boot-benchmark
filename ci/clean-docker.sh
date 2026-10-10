#!/usr/bin/env bash
# Frees Docker disk between image builds: buildpack cache volumes and dangling layers.
# `docker volume prune -f` removes only anonymous volumes (Docker CLI docs), but spring-boot:build-image
# keeps its caches in NAMED volumes, pack-cache-<12 hex>.build and .launch (VolumeName.basedOn in
# Spring Boot's buildpack Lifecycle, checked at v4.1.1); its other volumes (pack-layers-*, pack-app-*)
# it deletes itself. So remove exactly the pack-cache volumes by name. `volume prune -a` is not used:
# it would also remove every other unused named volume on the runner.
# Fail-closed: if the prune or the volume listing fails, the script (and the build) fails. Only a single
# volume that cannot be removed (for example one still in use) is tolerated, with a warning.
set -euo pipefail

docker volume prune -f > /dev/null
docker volume ls -q --filter name=pack-cache- | { grep -E '^pack-cache-[0-9a-f]+\.(build|launch)$' || true; } |
  while read -r vol; do
    docker volume rm "$vol" > /dev/null || echo "::warning::could not remove cache volume $vol"
  done
docker image prune -f > /dev/null
