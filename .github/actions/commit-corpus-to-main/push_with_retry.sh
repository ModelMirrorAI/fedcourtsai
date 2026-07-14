#!/usr/bin/env bash
# Push the local HEAD to the default branch, rebasing onto any advance and
# retrying a *transient* remote failure with exponential backoff.
#
# The deterministic writers (pull / live / historical) commit the corpus pointer
# and any newly-detected outcomes straight to the default branch. A push can fail
# for two very different reasons, and the earlier inline loops conflated them —
# every failure was logged as "default branch advanced," which misdirected triage
# when the real cause was a GitHub-side blip:
#
#   - the branch legitimately advanced between the rebase and the push (a merged
#     data/ PR) — a non-fast-forward the next rebase absorbs, so it self-corrects;
#   - a transient GitHub server error (e.g. `remote: fatal error in commit_refs`)
#     that has nothing to do with the branch and just needs to be outlasted.
#
# So: rebase-then-push in a loop with exponential backoff (which outlasts a brief
# server blip rather than a fixed ~10s window), and classify the failure from the
# push output so the log names the real cause. A rebase CONFLICT — the corpus
# pointer diverged despite the shared corpus-write lock — is a serialization bug,
# never transient, so it fails loudly and immediately.
#
# Assumes: a fresh local commit is already at HEAD; `origin` carries a credential
# that can push; `GITHUB_REF_NAME` names the target branch. Exits 0 on a pushed
# commit, non-zero (loud) on a genuine conflict or exhausted retries.
#
# Usage: push_with_retry.sh "<short label for the logs>"
set -euo pipefail

label="${1:-corpus pointer + outcomes}"
ref="${GITHUB_REF_NAME:?GITHUB_REF_NAME must be set}"
max_attempts="${PUSH_MAX_ATTEMPTS:-5}"
backoff="${PUSH_BACKOFF_START:-5}"

for attempt in $(seq 1 "$max_attempts"); do
  # Rebase onto the current tip first so a genuine advance pushes as a
  # fast-forward. A conflict leaves a rebase in progress; a transient fetch blip
  # does not — tell them apart, but fail closed either way (a diverged pointer is
  # never something to retry past).
  if ! git pull --rebase origin "$ref"; then
    if [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]; then
      git rebase --abort || true
      echo "::error::rebase conflict on the corpus pointer against the advanced tip — a concurrent corpus writer was not serialized (see docs/data-pipeline.md corpus-writer coordination)"
    else
      echo "::error::could not fetch/rebase onto the advanced tip (transient upstream failure)"
    fi
    exit 1
  fi

  # Capture the push output so a transient server error is told apart from a
  # legitimate branch advance — the log then names the real cause.
  push_log="$(mktemp)"
  if git push origin "HEAD:${ref}" >"$push_log" 2>&1; then
    cat "$push_log"
    rm -f "$push_log"
    exit 0
  fi
  cat "$push_log"  # surface the push output in the Actions log
  if grep -qiE 'non-fast-forward|fetch first|\! \[rejected\]' "$push_log"; then
    reason="the default branch advanced between rebase and push"
  else
    reason="a transient remote error (e.g. a GitHub commit_refs blip)"
  fi
  rm -f "$push_log"

  if [ "$attempt" -lt "$max_attempts" ]; then
    echo "::warning::push of ${label} failed — ${reason}; retry ${attempt}/${max_attempts} after ${backoff}s"
    sleep "$backoff"
    backoff=$((backoff * 2))
  fi
done

echo "::error::could not push ${label} after ${max_attempts} attempts (see the per-attempt warnings for the cause)"
exit 1
