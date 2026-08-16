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
#       No predict/evaluate/backtest fan-out may be in flight: an open trigger
#       issue carrying one of the run labels, or an unfinished run of any of
#       the three fan-out workflows, fails the gate. A workflow-file change
#       that reaches main mid-run changes what the run's later jobs execute
#       against (see "Recovering a run whose `collect` failed" in
#       docs/pipeline.md), so promotions wait for quiet — and backtests end in
#       a branch push + PR against main, so they count as matrices here.
#       Anything but a literal 0 from a count read — including a malformed
#       API response — fails the gate. Label fan-out means every
#       `issues: labeled` event briefly spawns to-be-skipped runs of the
#       fan-outs; a false positive from that window clears in seconds — re-run.
#
#   scripts/promotion-gate.sh freshness <sha>
#       Every required integration scenario must have a green run at exactly
#       <sha> — the gate tests what is being promoted, not what staging used
#       to be. A single green `scenario=all` run (the whole suite as one
#       run) satisfies every scenario at once; otherwise each is
#       matched per-run. Matching is on the integration-test workflow's
#       `run-name`; the format here and there are coupled, and a
#       workflow-shape test pins both ends (tests/test_workflow_promote.py).
#       Under PROMOTION_SKIP_SMOKE (below) the engine-smoke entries leave the
#       required set and a green `scenario=all-offline` run — the same suite
#       without them — also counts as whole-suite evidence.
#
#   scripts/promotion-gate.sh contexts [candidate...]
#       Every context `main`'s ruleset requires must have a job on `main` that
#       can report it: a required context nothing produces leaves every PR into
#       `main` pending forever, and the auto-merging collect PRs hang first.
#       The pre-flight before adding one, and the check that a promotion has
#       not renamed or deleted a job already required. Candidates are reported
#       as ready or not-yet, never fatally. Needs a token with repository
#       administration read, which `GITHUB_TOKEN` cannot hold at all — hence
#       not part of `all`, and the maintainer's to run.
#
#   scripts/promotion-gate.sh all <sha>
#       The quiesce and freshness stages, in order.
#
# quiesce and freshness need `gh` with Actions read + issues read (GH_TOKEN in
# CI); contexts additionally needs repository administration read (see above).
#
# Two environment variables move the required set, and they are not peers:
#
# PROMOTION_SCENARIOS overrides it outright (space-separated; an entry is
# `<scenario>` or `engine-smoke/<engine>`) — for narrowing a local re-check,
# never for weakening the gate in a workflow. An override also
# disables the whole-suite `scenario=all` acceptance in freshness: the `all`
# matrix is keyed to the default set, so an overridden set is checked against
# per-scenario runs only.
#
# PROMOTION_SKIP_SMOKE=1 drops the `engine-smoke/*` entries and lets a green
# `scenario=all-offline` run stand in for `scenario=all`. It is the one
# relaxation a workflow may set, and `promote.yml`'s `skip_engine_smoke`
# dispatch input is the only workflow that sets it (a shape test pins that no
# other does) — so a workflow-side skip is always an explicit act on one
# dispatch, never a standing configuration. Only the exact value `1` enables
# it; anything else, a typo included, leaves the gate strict. What it trades
# away is the only evidence that real engine cells still run in the production
# posture at the sha being promoted, so reserve it for batches that cannot
# affect a cell — docs, analytics, non-cell code — and when in doubt run the
# full suite. It narrows a pre-flight, not a merge: ci.yml's `promotion-gate`
# job — the required check on the promotion PR — sets neither variable, so the
# full set is what a batch actually merges on.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"

# Keep in step with the dispatch-command list the promote workflow prints on a
# freshness failure, and with the `all` scenario's matrix in
# integration-test.yml — a `scenario=all` dispatch must fan out exactly this
# set (a workflow-shape test pins both couplings).
REQUIRED_SCENARIOS="${PROMOTION_SCENARIOS:-ranged-reads corpus-service stub-cascade mcp-sidecar collect qp-topic engine-smoke/claude-code engine-smoke/codex engine-smoke/gemini}"

# The engine-smoke skip (see the header): a filter over whatever set is in
# force, so it composes with a local PROMOTION_SCENARIOS narrowing instead of
# racing it. Fails closed — only the literal `1` drops anything.
if [ "${PROMOTION_SKIP_SMOKE:-}" = 1 ]; then
  kept=""
  for entry in $REQUIRED_SCENARIOS; do
    case "$entry" in
      engine-smoke/*) continue ;;
    esac
    kept="${kept:+${kept} }${entry}"
  done
  REQUIRED_SCENARIOS="$kept"
fi

fail=0

quiesce() {
  local label wf status n
  for label in "run:predict" "run:evaluate" "run:backtest"; do
    n=$(gh api "repos/${REPO}/issues?labels=${label}&state=open&per_page=100" \
      --jq '[.[] | select(.pull_request | not)] | length')
    # Fail on anything that is not a literal 0, so a malformed count fails
    # closed instead of reading as "quiet".
    if [ "$n" != "0" ]; then
      echo "::error::quiescence: open '${label}' trigger issue count is ${n} — a run is in flight (or stalled: resolve it before promoting)"
      fail=1
    fi
  done
  for wf in run-predict.yml run-evaluate.yml run-backtest.yml; do
    for status in queued in_progress waiting pending requested; do
      n=$(gh api "repos/${REPO}/actions/workflows/${wf}/runs?status=${status}&per_page=1" \
        --jq .total_count)
      if [ "$n" != "0" ]; then
        echo "::error::quiescence: ${wf} ${status} run count is ${n}"
        fail=1
      fi
    done
  done
}

freshness() {
  local sha="$1" titles req scenario engine prefix
  # The one stage that reads the required set, so the one that must refuse an
  # empty one: the loop below would run zero times and report a clean gate
  # that checked no evidence at all. Reachable only from a
  # PROMOTION_SCENARIOS narrowing the engine-smoke skip then filters away to
  # nothing.
  if [ -z "$REQUIRED_SCENARIOS" ]; then
    echo "::error::freshness: the required scenario set is empty — the gate would check nothing"
    exit 2
  fi
  # Why the titles this matches cannot be forged: every dispatcher-controlled
  # component of the integration-test run-name — scenario, engine, and
  # deploy-environment — is a server-validated `choice` input (workflow-shape
  # tests pin this), so a display title is always drawn from a fixed
  # vocabulary and never carries free text. Everything below is defense in
  # depth on top of that: head_branch pins the evidence to runs dispatched
  # from the staging branch itself, before a title is even read; the
  # newline exclusion means a title that somehow preserved one could never
  # split into a fabricated extra line; and the matches are anchored.
  titles=$(gh api "repos/${REPO}/actions/workflows/integration-test.yml/runs?head_sha=${sha}&per_page=100" \
    --jq '.workflow_runs[]
          | select(.conclusion == "success" and .head_branch == "staging"
                   and ((.display_title | test("\n")) | not))
          | .display_title')
  # A `scenario=all` dispatch fans the whole required suite out as one
  # workflow run, so one green `all` title at the sha satisfies every
  # required scenario at once. The equivalence holds link by link: this exact
  # title shape is produced only by an `all` dispatch (a per-scenario run
  # always carries `<scenario> / <engine>`); an `all` run covers the whole
  # required set — the matrix legs with fail-fast off plus the collect job,
  # separate jobs in the same run — so the run concludes success only when
  # every job succeeded; and `@ staging` names the environment every matrix
  # leg bound, which only the staging branch may deploy to (the collect job
  # binds none by design — its evidence rests on the head_branch pin above,
  # which every title here already passed). Matched whole-line
  # (-Fx): the title is one fully-fixed string. Only titles selected as
  # success above are searched, so a match is a green run, never a red one.
  # Skipped entirely under a PROMOTION_SCENARIOS override: the `all` matrix
  # covers the default set, so an overridden set — which may name something
  # beyond it — must be satisfied by per-scenario runs.
  if [ -z "${PROMOTION_SCENARIOS:-}" ]; then
    if grep -Fqx "integration-test: all @ staging" <<<"$titles"; then
      return
    fi
    # Under the engine-smoke skip the requirement is the smaller suite, which
    # an `all-offline` run covers leg for leg — same jobs, same environment
    # binding, same success-only-when-every-job-succeeded arithmetic, minus
    # the three token-spending legs the skip already removed. The `all`
    # acceptance above stays first and unconditional: a full run is always
    # sufficient evidence for a subset of what it ran.
    if [ "${PROMOTION_SKIP_SMOKE:-}" = 1 ] \
      && grep -Fqx "integration-test: all-offline @ staging" <<<"$titles"; then
      return
    fi
  fi
  for req in $REQUIRED_SCENARIOS; do
    scenario="${req%%/*}"
    engine=""
    case "$req" in */*) engine="${req#*/}" ;; esac
    # Two anchored matches per title: the start-anchored prefix pins the
    # scenario (and engine, for the smokes; both come from the fixed
    # REQUIRED_SCENARIOS vocabulary, which contains no regex metacharacters),
    # the end-anchored suffix pins the staging deployment environment — which
    # is restricted to the staging branch, so only runs that ran from staging
    # satisfy the gate, independent of the prod environment's main-only
    # deployment policy. (The environment-free collect scenario's title
    # carries `@ staging` from the branch resolution without binding it; its
    # staging provenance is the head_branch pin above, which every title
    # here already passed.) The second grep runs without -q so the first
    # never dies on a closed pipe.
    if [ -n "$engine" ]; then
      prefix="^integration-test: ${scenario} / ${engine} @"
    else
      prefix="^integration-test: ${scenario} /"
    fi
    if ! grep "$prefix" <<<"$titles" | grep "@ staging$" >/dev/null; then
      echo "::error::freshness: no green '${req}' integration-test run at ${sha}"
      fail=1
    fi
  done
}

# Every context `main`'s ruleset requires must have a job on `main` that can
# report it. A required context nothing produces leaves every PR into `main`
# pending forever — the auto-merging collect PRs first — so this is the
# pre-flight before adding one, and the check that a promotion has not renamed
# or deleted a job that is already required. Extra arguments are candidate
# contexts: reported as ready or not-yet, never fatal.
#
# Deliberately NOT part of `all`: reading a ruleset needs admin-level access,
# and ci.yml's promotion-gate job holds only contents/actions/issues read. A
# required check that 403s would block promotions to report an advisory fact,
# so this stage is the maintainer's to run with their own token.
contexts() {
  local workdir main_workflows ruleset_id contexts_raw ctx candidate
  local required=() candidates=()

  workdir="$(mktemp -d)"
  # shellcheck disable=SC2064  # expand workdir now, not at trap time
  trap "rm -rf '${workdir}'" RETURN
  main_workflows="${workdir}/workflows"
  git fetch --quiet origin main
  git archive origin/main .github/workflows | tar -x -C "${workdir}" --strip-components=1

  # `|| true` so the -z branch can report the likely cause; under `set -e` a
  # 403 would otherwise kill the script before this message.
  ruleset_id="$(gh api "repos/${REPO}/rulesets" \
    --jq '.[] | select(.name=="main: require PR") | .id' 2>/dev/null | head -1 || true)"
  if [ -z "$ruleset_id" ]; then
    echo "::error::contexts: could not read the 'main: require PR' ruleset — a token with repository administration read is required"
    fail=1
    return
  fi

  # Read into a variable first: a failed call inside a process substitution
  # escapes both `set -e` and `pipefail`, and an empty required set would then
  # read as a clean run that checked nothing.
  if ! contexts_raw="$(gh api "repos/${REPO}/rulesets/${ruleset_id}" \
    --jq '.rules[] | select(.type=="required_status_checks")
          | .parameters.required_status_checks[].context')"; then
    echo "::error::contexts: could not read ruleset ${ruleset_id}'s required status checks"
    fail=1
    return
  fi
  while IFS= read -r ctx; do
    [ -n "$ctx" ] && required+=(--context "$ctx")
  done <<<"$contexts_raw"
  if [ ${#required[@]} -eq 0 ]; then
    echo "::error::contexts: ruleset ${ruleset_id} reported no required status checks — the read failed or the rule shape changed"
    fail=1
    return
  fi

  for candidate in "$@"; do
    candidates+=(--candidate "$candidate")
  done

  # The comparison is tested Python (tests/test_required_checks.py); this only
  # fetches what it compares.
  if ! uv run fedcourts assert-required-contexts \
    --workflows "$main_workflows" --base-branch main \
    ${required[@]+"${required[@]}"} ${candidates[@]+"${candidates[@]}"}; then
    fail=1
  fi
}

case "${1:-}" in
  quiesce)
    quiesce
    ;;
  freshness)
    freshness "${2:?usage: promotion-gate.sh freshness <sha>}"
    ;;
  contexts)
    contexts "${@:2}"
    ;;
  all)
    quiesce
    freshness "${2:?usage: promotion-gate.sh all <sha>}"
    ;;
  *)
    echo "usage: scripts/promotion-gate.sh {quiesce|freshness <sha>|contexts [candidate...]|all <sha>}" >&2
    exit 2
    ;;
esac

if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "promotion gate: ${1} clean"
