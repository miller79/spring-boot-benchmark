#!/usr/bin/env bash
# Prepares a GitHub-hosted runner for benchmarking and records the facts the
# results depend on (cgroup mode, cpuset support, disk headroom).
# Usage: prepare-host.sh <cpuset> <results-dir>
set -euo pipefail

CPUSET="${1:?cpuset, e.g. 2,3}"
OUT="${2:?results dir}"
# Pinned by digest; used only to prove the cpuset and quota flags work on this host.
PROBE_IMAGE="docker.io/library/busybox@sha256:bdf57e528e45e4433820e045b29b4597825a1c9e38353532d90a01445013f82e"

mkdir -p "$OUT"
disk() { echo "== $1 ($(date -u +%H:%M:%S))"; df -h / /mnt 2>/dev/null; }

{
  disk "before cleanup"
  # Preinstalled toolchains this job never uses; removing them is the usual way to get headroom for native builds.
  sudo rm -rf /usr/share/dotnet /usr/local/lib/android /opt/ghc /opt/hostedtoolcache/CodeQL /usr/local/share/boost
  disk "after cleanup"
} | tee "$OUT/disk.log"

if [[ "$(stat -fc %T /sys/fs/cgroup)" != "cgroup2fs" ]]; then
  echo "::error::cgroup v2 expected; cpu.stat/memory.peak polling would not work" >&2
  exit 1
fi
if (( $(nproc) < 4 )); then
  echo "::error::need >= 4 vCPUs to keep the harness off cpuset $CPUSET" >&2
  exit 1
fi

python3 "$(dirname "$0")/bench.py" env --out "$OUT/env.json" > /dev/null

# Docker only warns and drops --cpuset-cpus when the cpuset controller is missing, so check what the container really got.
probe=$(docker run --rm --cpus=0.6 --cpuset-cpus="$CPUSET" --memory=1g "$PROBE_IMAGE" \
  sh -c 'echo cpuset.cpus.effective=$(cat /sys/fs/cgroup/cpuset.cpus.effective 2>/dev/null); echo cpu.max=$(cat /sys/fs/cgroup/cpu.max); echo memory.max=$(cat /sys/fs/cgroup/memory.max)' 2>&1)
{ echo "== cpuset/quota probe (--cpus=0.6 --cpuset-cpus=$CPUSET --memory=1g)"; echo "$probe"; } | tee "$OUT/cgroup-probe.log"
effective=$(sed -n 's/^cpuset.cpus.effective=//p' <<< "$probe")
if ! python3 - "$CPUSET" "$effective" <<'PY'
import sys

def expand(spec):
    out = set()
    for part in spec.split(","):
        if part:
            a, _, b = part.partition("-")
            out.update(range(int(a), int(b or a) + 1))
    return out

sys.exit(0 if expand(sys.argv[1]) == expand(sys.argv[2]) else 1)
PY
then
  echo "::error::cpuset $CPUSET was not applied (effective: '$effective')" >&2
  exit 1
fi
grep -q '^cpu.max=60000 100000$' <<< "$probe" || { echo "::error::0.6 CPU quota was not applied" >&2; exit 1; }
