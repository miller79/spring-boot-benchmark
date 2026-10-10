#!/usr/bin/env bash
# Decide whether the Pages deploy has a bench-data branch to publish. Only an explicit HTTP 404 on the
# branch ref means "no history yet" (skip, exit 0 without present=true); any other API error (403, 5xx,
# network) is a real failure and fails the job, so a broken token or outage is never reported as a skip.
# Needs GH_TOKEN, GITHUB_REPOSITORY and GITHUB_OUTPUT.
set -uo pipefail
out=$(gh api "repos/$GITHUB_REPOSITORY/git/ref/heads/bench-data" --silent 2>&1)
rc=$?
if [[ $rc -eq 0 ]]; then
  echo "present=true" >> "$GITHUB_OUTPUT"
elif [[ "$out" == *"(HTTP 404)"* ]]; then
  echo "::notice::bench-data does not exist yet (HTTP 404); nothing to deploy"
else
  echo "::error::could not look up bench-data: $out"
  exit 1
fi
