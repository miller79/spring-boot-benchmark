#!/usr/bin/env bash
# Scenario tests for clean-docker.sh with a stub `docker`. Usage: ci/test-clean-docker.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/bin"
# The stub logs every call; `volume ls` lists $STUB_VOLUMES (one per line); `volume rm` fails for $STUB_RM_FAIL.
cat > "$WORK/bin/docker" <<'STUB'
#!/usr/bin/env bash
echo "$*" >> "$STUB_LOG"
case "$1 $2" in
  "volume ls") printf '%s\n' "${STUB_VOLUMES:-}" | sed '/^$/d' ;;
  "volume rm") [[ "$3" != "${STUB_RM_FAIL:-}" ]] ;;
esac
STUB
chmod +x "$WORK/bin/docker"

fails=0
LOG="$WORK/log"
# run <name> <expected rc> <exact expected docker calls, newline separated> [VAR=value...]
run() {
  local name="$1" want_rc="$2" want="$3" out rc
  shift 3
  : > "$LOG"
  out=$(env PATH="$WORK/bin:$PATH" STUB_LOG="$LOG" "$@" bash "$HERE/clean-docker.sh" 2>&1); rc=$?
  if [[ $rc -eq $want_rc && "$(cat "$LOG")" == "$want" ]]; then echo "ok   $name"
  else echo "FAIL $name (rc=$rc, wanted rc=$want_rc)"; sed 's/^/     /' "$LOG"; echo "$out" | sed 's/^/     /'; fails=$((fails + 1)); fi
}
LS='volume ls -q --filter name=pack-cache-'

run "removes build and launch cache volumes, prunes the rest" 0 \
  "volume prune -f
$LS
volume rm pack-cache-1a2b3c4d5e6f.build
volume rm pack-cache-1a2b3c4d5e6f.launch
image prune -f" \
  "STUB_VOLUMES=$(printf 'pack-cache-1a2b3c4d5e6f.build\npack-cache-1a2b3c4d5e6f.launch')"
run "no cache volumes: nothing removed, never prune -a" 0 \
  "volume prune -f
$LS
image prune -f"
run "leaves other volumes alone" 0 \
  "volume prune -f
$LS
image prune -f" \
  "STUB_VOLUMES=$(printf 'postgres-data\nmy-pack-cache-1a2b3c4d5e6f.build\npack-cache-evil;id.build\npack-layers-abc')"
run "a volume that cannot be removed only warns" 0 \
  "volume prune -f
$LS
volume rm pack-cache-aaaaaaaaaaaa.build
volume rm pack-cache-bbbbbbbbbbbb.build
image prune -f" \
  "STUB_VOLUMES=$(printf 'pack-cache-aaaaaaaaaaaa.build\npack-cache-bbbbbbbbbbbb.build')" STUB_RM_FAIL=pack-cache-aaaaaaaaaaaa.build

echo
if [[ $fails -eq 0 ]]; then echo "all clean-docker scenarios passed"; else echo "$fails scenario(s) failed"; exit 1; fi
