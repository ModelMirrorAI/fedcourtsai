#!/usr/bin/env bash
#
# The single definition of the staging→main promotion gate. The `promote`
# dispatch workflow and ci.yml's `promotion-gate` job both invoke this script,
# so the pre-flight a maintainer runs and the required check on the promotion
# PR cannot drift apart.
#
# Stages:
#
#   scripts/promotion-gate.sh quiesce
#       No predict/evaluate matrix may be in flight: an open trigger issue
#       carrying either run label, or a queued/in-progress/waiting run of
#       either fan-out workflow, fails the gate. A workflow-file change that
#       reaches main mid-matrix changes what the run's later jobs execute
#       against (see "Recovering a run whose `collect` failed" in
#       docs/pipeline.md), so promotions wait for quiet. Label fan-out means
#       every `issues: labeled` event briefly spawns to-be-skipped runs of the
#       fan-outs; a false positive from that window clears in seconds — re-run.
#
#   scripts/promotion-gate.sh freshness <sha>
#       Every required integration scenario must have a green run at exactly
#       <sha> — the gate tests what is being promoted, not what staging used
#       to be. Matching is on the integration-test workflow's `run-name`; the
#       format here and there are coupled, and a workflow-shape test pins both
#       ends (tests/test_workflow_promote.py).
#
#   scripts/promotion-gate.sh all <sha>
#       Both stages, in order.
#
# Needs `gh` with a token holding Actions read + issues read (GH_TOKEN in CI).
# PROMOTION_SCENARIOS overrides the required scenario set (space-separated;
# an entry is `<scenario>` or `engine-smoke/<engine>`) — for narrowing a local
# re-check, never for weakening the gate in a workflow.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"

# Keep in step with the dispatch-command list the promote workflow prints on a
# freshness failure.
REQUIRED_SCENARIOS="${PROMOTION_SCENARIOS:-ranged-reads corpus-service stub-cascade mcp-sidecar engine-smoke/claude-code engine-smoke/codex engine-smoke/gemini}"

fail=0

quiesce() {
  local label wf status n
  for label in "run:predict" "run:evaluate"; do
    n=$(gh api "repos/${REPO}/issues?labels=${label}&state=open&per_page=100" \
      --jq '[.[] | select(.pull_request | not)] | length')
    if [ "$n" -gt 0 ]; then
      echo "::error::quiescence: ${n} open '${label}' trigger issue(s) — a matrix is in flight (or stalled: resolve it before promoting)"
      fail=1
    fi
  done
  for wf in run-predict.yml run-evaluate.yml; do
    for status in queued in_progress waiting; do
      n=$(gh api "repos/${REPO}/actions/workflows/${wf}/runs?status=${status}&per_page=1" \
        --jq .total_count)
      if [ "$n" -gt 0 ]; then
        echo "::error::quiescence: ${wf} has ${n} ${status} run(s)"
        fail=1
      fi
    done
  done
}

freshness() {
  local sha="$1" titles req scenario engine pattern
  titles=$(gh api "repos/${REPO}/actions/workflows/integration-test.yml/runs?head_sha=${sha}&per_page=100" \
    --jq '.workflow_runs[] | select(.conclusion == "success") | .display_title')
  for req in $REQUIRED_SCENARIOS; do
    scenario="${req%%/*}"
    engine=""
    case "$req" in */*) engine="${req#*/}" ;; esac
    if [ -n "$engine" ]; then
      pattern="integration-test: ${scenario} / ${engine} @"
    else
      pattern="integration-test: ${scenario} /"
    fi
    if ! grep -qF "$pattern" <<<"$titles"; then
      echo "::error::freshness: no green '${req}' integration-test run at ${sha}"
      fail=1
    fi
  done
}

case "${1:-}" in
  quiesce)
    quiesce
    ;;
  freshness)
    freshness "${2:?usage: promotion-gate.sh freshness <sha>}"
    ;;
  all)
    quiesce
    freshness "${2:?usage: promotion-gate.sh all <sha>}"
    ;;
  *)
    echo "usage: scripts/promotion-gate.sh {quiesce|freshness <sha>|all <sha>}" >&2
    exit 2
    ;;
esac

if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "promotion gate: ${1} clean"
