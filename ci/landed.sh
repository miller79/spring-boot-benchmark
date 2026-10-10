#!/usr/bin/env bash
# Publish-error gate: succeeds only when the bench-data head moved since BEFORE_SHA and its data file
# holds this commit's entry for BENCH_NAME. The benchmark action cannot tell a regression alert from a
# push error (no outputs, both fail the step), so the data decides. Inputs come from the environment:
# GH_TOKEN, GITHUB_REPOSITORY, GITHUB_SHA, BENCH_NAME, BEFORE_SHA, DATA_FILE, MODULE, BENCH_OUTCOME,
# GITHUB_STEP_SUMMARY (optional); LANDED_SLEEP seconds between the 3 attempts (default 5).
set -uo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
for attempt in 1 2 3; do
  head=$(gh api "repos/$GITHUB_REPOSITORY/git/ref/heads/bench-data" -q .object.sha || true)
  if [[ -n "$head" && "$head" != "$BEFORE_SHA" ]] \
    && gh api -H 'Accept: application/vnd.github.raw+json' \
      "repos/$GITHUB_REPOSITORY/contents/$DATA_FILE?ref=$head" \
    | python3 "$here/verify_published.py" --name "$BENCH_NAME" --sha "$GITHUB_SHA"; then
    echo "history landed on bench-data@$head (publish step outcome: $BENCH_OUTCOME)"
    exit 0
  fi
  if [[ $attempt -lt 3 ]]; then sleep "${LANDED_SLEEP:-5}"; fi
done
echo "::error::$MODULE was not published: bench-data has no entry for this commit (publish step outcome: $BENCH_OUTCOME)"
echo "### Not published: $MODULE (the history push did not land; publish step outcome: $BENCH_OUTCOME)" >> "${GITHUB_STEP_SUMMARY:-/dev/null}"
exit 1
