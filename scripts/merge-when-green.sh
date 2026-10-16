#!/usr/bin/env bash
# Merge one unattended data-lane PR into `main` once its checks pass, pinned to
# the commit the job that built it pushed.
#
#   merge-when-green.sh <pr-number> <head-sha>
#
# Environment: `GH_TOKEN` (the dev App token, minted fresh by the calling step),
# `CHECKS_TOKEN` (a token with checks read for the check-run listing — the job's
# ambient `GITHUB_TOKEN`, so the dev App needs no checks permission), `REPO`
# (owner/name). Optional: `MERGE_REQUIRED_CHECKS` (space-separated check names
# that must have reported before a refusal counts as settled; default
# `gate paths`), `MERGE_METHOD` (default `squash`), `MERGE_WAIT_SECONDS`
# (default 1200), `MERGE_POLL_SECONDS` (default 30).
#
# Why this exists rather than `gh pr merge --auto`. `main: require approval`
# lists the dev App as a pull-request-only bypass actor, and that bypass is what
# lets the two unattended lanes — the predict/evaluate `collect` PRs and the
# big-case board — land without a human. Auto-merge never exercises a bypass:
# it waits until the PR satisfies every rule, approval included, so an armed
# bot PR sits blocked with every check green. A merge call made by the dev App
# itself is expected to exercise it — unverified until the first production
# run, whose merge step either reports the merge or quotes the platform's
# refusal, leaving the PR as it would have been. The call sites still arm auto-merge first, so a PR
# this script gives up on merges the moment the maintainer approves it.
#
# What still binds. The bypass is on the approval ruleset alone; `main: require
# PR`, which carries the required `gate` and `paths` checks, does not list the
# dev App, so the platform refuses this merge until those checks pass. The
# script never decides that a PR is green — it asks to merge and the ruleset
# answers. Its own refusals are all conservative:
#
# - **Pinned head.** The merge passes `sha`, so it lands only the commit the
#   calling job pushed and jailed. A push onto the branch afterwards — by any
#   identity — makes the platform refuse it, and the PR is left for the
#   maintainer's review, where `dismiss stale reviews` and the extra-approval
#   rule for unattributed changes apply.
# - **Its own lane only.** A PR whose base is not `main`, or whose head lives in
#   another repository, is never merged, whatever number it was handed.
# - **Every check is heard first, and any failure stops it,** required or not:
#   the merge is asked for only once nothing is still running, so a red CodeQL
#   run on a data PR gets a human look before it lands. Only each check's newest run
#   counts, and a cancelled one is waited on rather than failed: `ci.yml`
#   cancels a superseded run of the same ref, and the call sites' own force-push
#   and body edit fire two runs on one head.
#
# Call sites run this file as their own job's commit holds it — copied out with
# `git show "${GITHUB_SHA}:scripts/merge-when-green.sh"` to the runner's temp
# directory — never from the working tree: by the time a collect job merges,
# its tree has held cell artifacts, and a script read from there would be
# whatever those left behind, run against a token that can merge to `main`.
#
# Every give-up path exits 0 with a warning and a line in the step summary: the
# artifact is already pushed and its PR open, which is the state a refused merge
# leaves, and the run's own work did not fail. A refusal that persists once the
# required checks have reported and nothing is still running is reported with
# the platform's own message, because that is what a missing bypass looks like.

set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: merge-when-green.sh <pr-number> <head-sha>" >&2
  exit 2
fi
pr=$1
sha=$2
: "${GH_TOKEN:?GH_TOKEN must hold the dev App token}"
: "${CHECKS_TOKEN:?CHECKS_TOKEN must hold a token with checks read}"
: "${REPO:?REPO must name owner/repo}"
case "$pr" in
  '' | *[!0-9]*)
    echo "pr must be a number, got '${pr}'" >&2
    exit 2
    ;;
esac
case "$sha" in
  '' | *[!0-9a-f]*)
    echo "head sha must be a lowercase hex commit id, got '${sha}'" >&2
    exit 2
    ;;
esac
[ "${#sha}" -eq 40 ] || {
  echo "head sha must be 40 hex characters, got '${sha}'" >&2
  exit 2
}

method=${MERGE_METHOD:-squash}
wait_s=${MERGE_WAIT_SECONDS:-1200}
poll_s=${MERGE_POLL_SECONDS:-30}
read -r -a required <<<"${MERGE_REQUIRED_CHECKS:-gate paths}"
deadline=$(($(date +%s) + wait_s))
pr_url="${GITHUB_SERVER_URL:-https://github.com}/${REPO}/pull/${pr}"
fallback="it lands on the maintainer's approval if auto-merge is armed, and needs a manual merge otherwise"

report() {
  # $1 = annotation level, $2 = message. The annotation expires with the run,
  # so the summary carries it too.
  echo "::$1::$2" >&2
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    printf '%s\n' "$2" >>"$GITHUB_STEP_SUMMARY"
  fi
}

# Sleep to the next poll, or give up at the deadline. Every unanswered state
# ends here, so the wait is bounded whatever the API does.
next_poll() {
  if [ "$(date +%s)" -ge "$deadline" ]; then
    report warning "PR #${pr}: not merged within ${wait_s}s (last refusal: ${last_refusal:-none}); ${fallback} (${pr_url})."
    exit 0
  fi
  sleep "$poll_s"
}

# The answers are joined on `|`, not tabs: tab is IFS whitespace, so `read`
# would collapse an empty field and shift the ones after it.
PULL_JQ='[.state, (.merged | tostring), .head.sha, .base.ref, (.head.repo.full_name // "")] | join("|")'
# Newest run per check name, then: how many are still unsettled (queued,
# running, or cancelled), the failed ones, and the ones that concluded.
# shellcheck disable=SC2016 # `$latest` is a jq variable, not a shell one
CHECKS_JQ='[.check_runs | group_by(.name)[] | max_by(.id)] as $latest
  | [ ($latest | map(select(.status != "completed" or .conclusion == "cancelled")) | length | tostring),
      ($latest | map(select(.status == "completed"
        and (.conclusion | IN("failure", "timed_out", "action_required", "startup_failure", "stale")))
        | .name) | join(",")),
      ($latest | map(select(.status == "completed" and .conclusion != "cancelled") | .name) | join(",")) ]
  | join("|")'

settled_refusals=0
last_refusal=""
while :; do
  # Each read is bounded and a failed one is retried at the next poll rather
  # than ending the step: a blip here would otherwise strand a green PR. The
  # output is assigned before it is parsed, so an empty answer can never read
  # as a closed PR.
  if ! info=$(timeout 30 gh api "repos/${REPO}/pulls/${pr}" --jq "$PULL_JQ"); then
    last_refusal="reading the pull request failed"
    next_poll
    continue
  fi
  IFS='|' read -r state merged head base head_repo <<<"$info"
  if [ -z "$state" ]; then
    last_refusal="the pull request read came back empty"
    next_poll
    continue
  fi
  if [ "$merged" = "true" ]; then
    echo "PR #${pr} is already merged."
    exit 0
  fi
  if [ "$state" != "open" ]; then
    report warning "PR #${pr} was closed unmerged; nothing to merge (${pr_url})."
    exit 0
  fi
  if [ "$base" != "main" ] || [ "$head_repo" != "$REPO" ]; then
    report warning "PR #${pr} is not a ${REPO} branch into main (base ${base}, head ${head_repo:-unknown}); not merged (${pr_url})."
    exit 0
  fi
  if [ "$head" != "$sha" ]; then
    report warning "PR #${pr}'s head moved from ${sha} to ${head} after this job pushed it; left for the maintainer's review (${pr_url})."
    exit 0
  fi

  # One page of 100: a data PR's head carries well under a dozen check runs.
  if ! checks=$(GH_TOKEN="$CHECKS_TOKEN" timeout 30 \
    gh api "repos/${REPO}/commits/${sha}/check-runs?per_page=100" --jq "$CHECKS_JQ"); then
    last_refusal="reading the check runs failed"
    next_poll
    continue
  fi
  IFS='|' read -r pending failed concluded <<<"$checks"
  if [ -n "$failed" ]; then
    report warning "PR #${pr} has failed checks (${failed}); left open for a manual look (${pr_url})."
    exit 0
  fi

  # Ask only once every check has had its say: the required checks have
  # concluded and nothing — required or not — is still queued, running, or
  # waiting on a rerun. Merging the moment the ruleset would accept it would
  # land a PR while a non-required check could still fail.
  reported=true
  for name in "${required[@]}"; do
    case ",${concluded}," in
      *",${name},"*) ;;
      *) reported=false ;;
    esac
  done
  if [ "$reported" != true ] || [ "$pending" != "0" ]; then
    settled_refusals=0
    last_refusal="checks still running"
    next_poll
    continue
  fi

  if out=$(timeout 30 gh api -X PUT "repos/${REPO}/pulls/${pr}/merge" \
    -f merge_method="$method" -f sha="$sha" --jq '.sha' 2>&1); then
    echo "Merged PR #${pr} at ${sha} as ${out}."
    if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
      printf 'Merged %s once its checks passed.\n' "$pr_url" >>"$GITHUB_STEP_SUMMARY"
    fi
    exit 0
  fi
  last_refusal=$(printf '%s' "$out" | tr '\n' ' ' | cut -c1-300)

  # A refusal with every check concluded means the platform wants something no
  # check will supply — an approval the bypass did not cover, a conflict, a
  # moved base. Twice running, so a check that starts between two polls (a
  # rerun, a late suite) resets the count instead of ending the wait.
  settled_refusals=$((settled_refusals + 1))
  if [ "$settled_refusals" -ge 2 ]; then
    report warning "PR #${pr}: merge refused with every check concluded (${last_refusal}); ${fallback} (${pr_url})."
    exit 0
  fi
  next_poll
done
