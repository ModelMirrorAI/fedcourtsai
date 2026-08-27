# shellcheck shell=bash
# A bounded retry around a single GitHub API call, for the steps whose GitHub
# bookkeeping should not decide whether a run is red: the ops dashboard and the
# collection calls that feed it, the weekly digest, the data-validation
# escalation, the per-day pull-log / live-log alarms, the pipeline-runs
# dashboard, and the seed guard.
#
# The contract. Every one of those calls is bookkeeping *about* a run rather
# than the work itself, so a transient 5xx costs something the run never earned
# — and what it costs differs by site, which is why they all get the same
# wrapper. On the run-ops steps and the seed guard's clear-the-incident path, a
# blip fails the step and so reddens a run that did its work, or leaves a stale
# incident open over a healthy one. On the pipeline-runs dashboard
# (`continue-on-error` at both callers) and the pull-log / live-log alarms
# (which fire only on an already-failed window), nothing turns red: the loss is
# the record itself — a missing dashboard row, or no incident issue for a day
# that broke. Three attempts absorb the blip; a sustained outage still exhausts
# and returns non-zero, which is the right residue when the API itself is down.
#
# Shape matters as much as the retry at the find-or-create lookups, where an
# empty result is silently meaningful: an empty `num` reads as "no issue yet"
# and opens a duplicate, or restarts a dashboard's rolling table from scratch.
# The rule there is that a retried call is never a non-final element of a
# pipeline — either filter with `gh`'s own `--jq` inside the same command, or
# assign the output and filter the variable — so `set -e` stops the step on the
# assignment itself. (Note what that does and does not buy: it narrows the
# dependence from errexit *and* pipefail to errexit alone. With `set -e` off,
# an empty `listing` filters to an empty `num` and the duplicate opens anyway.)
# A call whose output is only accumulated — run-ops' per-label listing loop
# into `jq -s` — has no such branch to fall into and stays a pipeline.
#
# What the retry cannot make safe. `gh issue create` and `gh issue comment` are
# not idempotent, so a write that lands server-side and is then cut off at
# `timeout 30` is re-sent on the next attempt: a second dashboard issue, or a
# second alarm thread for the same day. That is the same split state this
# wrapper exists to prevent, reached from the other side, and it is accepted —
# a >30s write that still succeeds is far rarer than the transient failure
# being absorbed, and the find-or-create at every such site converges on one
# issue at the next window.
#
# Why each attempt is bounded (`timeout 30`). `gh` sets no client-side request
# timeout, so a stalled connect against a degraded API hangs until the job's own
# kill — leaving nothing written, the one outcome these steps exist to prevent.
#
# Why no transient/genuine split (unlike commit-corpus-to-main's
# push_with_retry.sh, which classifies its failures). Retrying a deterministic
# 4xx costs only the 15s of sleeps; buying a classifier out of `gh`'s exit codes
# would cost more in reviewable surface than that is worth.
#
# Why the annotations go to stderr. `gh_retry`'s stdout is the wrapped command's
# stdout, and most callers read it through `$(…)`; an annotation on stdout would
# be captured into the variable instead of reaching the log. A caller that
# deliberately tolerates exhaustion (`gh_retry gh label create … || …`) still
# gets the `::error::` annotation, which is deliberate — three failed attempts
# mean something is persistently wrong, worth surfacing even where that one
# call is optional. The annotation names the call and the fact only, leaving
# the consequence to the caller: exhaustion is fatal at most sites and
# tolerated at a few, and only the caller knows which. Only the command's first
# three words are named, so an issue body passed as an argument never lands in
# an annotation.
#
# Two consumption modes:
#   * `source scripts/gh_retry.sh` — wherever the step runs after a checkout
#     (the run-ops jobs; the run-log-dashboard composite, whose own presence on
#     disk already proves the checkout succeeded).
#   * an inline copy of the function below — for the steps that must fire even
#     when the checkout or the App-token mint failed (run-pull's two failure
#     alarms, run-seed's guard job, which has no checkout at all). Those copies
#     are pinned byte-identical to this one by
#     `tests/test_workflow_cell_invariants.py`, so drift fails a test rather
#     than quietly splitting the behavior in two.
gh_retry() {
  local attempt out what
  what="${1:-} ${2:-} ${3:-}"
  for attempt in 1 2 3; do
    if out=$(timeout 30 "$@"); then
      printf '%s\n' "$out"
      return 0
    fi
    if [ "$attempt" -lt 3 ]; then
      echo "::warning::${what} failed (attempt ${attempt}/3) — retrying" >&2
      sleep $((attempt * 5))
    fi
  done
  echo "::error::${what} failed after 3 attempts" >&2
  return 1
}
