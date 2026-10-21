#!/usr/bin/env bash
#
# The single definition of the promotion gate into `main`. The `promote`
# dispatch workflow, the promotion train (`promotion-prep`) and ci.yml's
# `promotion-gate` job all invoke this script, so the pre-flight a maintainer
# runs, the train's reads and the required check on the promotion PR cannot
# drift apart.
#
# A promotion's head ref is `staging` (a hand-opened promotion) or a promotion
# train candidate, `promote/<UTC date>[-N]`: a branch cut at a commit on
# staging's first-parent chain and never moved. The stages that read a head
# take the ref beside the SHA (default `staging`) and refuse any other name.
#
# Stages:
#
#   scripts/promotion-gate.sh quiesce
#       No predict/evaluate/backtest fan-out may be in flight: an unfinished
#       run of any of the three fan-out workflows fails the gate. A
#       workflow-file change that reaches main mid-run changes what the run's
#       later jobs execute against (see "Recovering a run whose `collect`
#       failed" in docs/pipeline.md), so promotions wait for quiet — and
#       backtests end in a branch push + PR against main, so they count as
#       matrices here. Anything but a literal 0 from a count read — including a
#       malformed API response — fails the gate. Run state is what the gate
#       reads, and it is exhaustive: every fan-out enters through this
#       workflow's own schedule or dispatch, so a round in flight is always a
#       run in flight. A round parked on the `review` hold counts as in flight
#       (`waiting`), which is the intent — it will spend against whatever is on
#       `main` when it releases.
#
#   scripts/promotion-gate.sh freshness <sha> [<head-ref>]
#       Every required integration scenario must have a green run at exactly
#       <sha>, dispatched from exactly <head-ref> — the gate tests what is
#       being promoted, not what staging used to be. A single green `scenario=gate` run (the whole required suite
#       as one run) satisfies every scenario at once; otherwise each is
#       matched per-run. Matching is on the integration-test workflow's
#       `run-name`; the format here and there are coupled, and a
#       workflow-shape test pins both ends (tests/test_workflow_promote.py).
#       Under PROMOTION_SKIP_SMOKE (below) both engine families' entries leave
#       the required set and a green `scenario=offline-gate` run — the same
#       suite without them — also counts as whole-suite evidence. The
#       workflow's `all` and `all-offline` selections are never evidence:
#       they run every scenario it offers, a set that moves with the workflow
#       rather than with this gate.
#
#   scripts/promotion-gate.sh contexts [candidate...]
#       Every context `main`'s ruleset requires must have a job on `main` that
#       can report it: a required context nothing produces leaves every PR into
#       `main` pending forever, and the auto-merging collect PRs hang first.
#       The pre-flight before adding one, and the check that a promotion has
#       not renamed or deleted a job already required. Candidates are reported
#       as ready or not-yet, never fatally. Needs a token with repository
#       administration read, which `GITHUB_TOKEN` cannot hold at all — hence
#       not part of `promotion-gate.sh all`, and the maintainer's to run.
#
#   scripts/promotion-gate.sh contexts-due <sha>
#       Whether this batch owes the `contexts` stage above: due when it changes
#       anything that stage judges settings against — a workflow, this script,
#       the required-check, ruleset or environment judgments, or the
#       corpus-check approver they check against (`fedcourts contexts-due`,
#       src/fedcourtsai/contexts_due.py). The verdict says when to run it:
#       `contexts` reads main's own workflows, so a workflow change is checked
#       once the promotion merges, and the rest before.
#       It prints the verdict and never fails the gate: `contexts` needs an
#       admin-read token no CI job holds, so the verdict tells the maintainer
#       which promotions to run it for, and a setting changed by hand needs it
#       with no batch at all. Reads git alone; the caller fetches main first.
#
#   scripts/promotion-gate.sh registry <sha>
#       Step 0 of a process move, checked on every batch: the process registry
#       at <sha> must exist, load, and be stampable by the merge that carries
#       it to `main`. A batch carrying anything pending needs `origin/main` to
#       declare merge-stamped instants; no digest it holds pending may already
#       stamp a committed cell on `origin/main`; every enabled actor's digest
#       at <sha> must be registered; each predictor keeps at most one open
#       window (a pending close counts as a close); the batch carries at most
#       one label new to `main`, with no `prereg/` tag yet; no boundary name
#       may repeat; nothing may already sit pending on `origin/main`; and no
#       row `origin/main` has stamped may change, go or move, nor any
#       evaluator digest's blessing labels lose main's prefix, save a pending
#       close on a window no live predictor computes, a blessing that left
#       the fleet, and a revocation of a closed window dated at or after the
#       head.
#       The logic is tested Python (`fedcourts registry-gate`,
#       src/fedcourtsai/registry_gate.py); it reads git alone — <sha>'s tree,
#       `origin/main` and the local tags — so the caller fetches `main` and
#       the tags first (`git fetch origin --tags`; CI's checkout already holds
#       them, with full history).
#
#   scripts/promotion-gate.sh provenance <sha> [<head-ref>]
#       A `promote/` head must be a cut of staging: <sha> on origin/staging's
#       first-parent chain, which is also what `promotion-record` requires of
#       the merge's second parent. A `staging` head is staging itself. Reads
#       git alone; the caller fetches staging first.
#
#   scripts/promotion-gate.sh all <sha> [<head-ref>]
#       The quiesce, provenance, freshness and registry stages, in order, then
#       the contexts-due verdict, which reports and never fails.
#
# quiesce and freshness need `gh` with Actions read (GH_TOKEN in CI); contexts
# additionally needs repository administration read (see above); registry
# and contexts-due need `uv` and the fetched refs, and no token.
#
# Two environment variables move the required set, and they are not peers:
#
# PROMOTION_SCENARIOS overrides it outright (space-separated; an entry is
# `<scenario>` or `engine-smoke/<engine>`) — for narrowing a local re-check,
# never for weakening the gate in a workflow. An override also
# disables the whole-suite `scenario=gate` acceptance in freshness: the `gate`
# matrix is keyed to the default set, so an overridden set is checked against
# per-scenario runs only.
#
# PROMOTION_SKIP_SMOKE=1 drops the `engine-smoke/*` and
# `engine-actions-smoke/*` entries — every entry that spends model tokens —
# and lets a green `scenario=offline-gate` run stand in for `scenario=gate`. It
# is the one relaxation a workflow may set, and exactly three workflows set it
# (a shape test pins that no fourth does):
#
#   * `promote.yml`'s `skip_engine_smoke` dispatch input, which narrows one
#     pre-flight — a cheap answer to "is anything else missing" before paying
#     for the smokes;
#   * `ci.yml`'s `promotion-gate` job, when `main`'s cell-reach classifier
#     (scripts/cell_reach.py) calls the batch cell-inert or the promotion PR
#     carries the `promote:skip-engine-smoke` label — and never while it
#     carries `promote:require-engine-smoke` — which narrows what that batch
#     merges on;
#   * the promotion train's plan job (`promotion-prep.yml`), on the same
#     decision for its candidate, so the train reads freshness exactly as the
#     required check will.
#
# None is standing configuration a batch can switch on for itself: a dispatch
# input covers one run, a label one PR, and the classifier that runs is
# `main`'s copy — an allow-list of paths no cell runs, failing closed on every
# doubt — so a batch never grades itself, and only a promotion changes what
# it waives.
#
# What it trades away is every piece of evidence that real engines still run at
# the sha being promoted: that a cell completes in the production posture
# (engine-smoke), and that each engine's own invocation block is still accepted
# by the surface that receives it (engine-actions-smoke) — the second being the
# class an action version bump breaks, silently, on the very promotion that
# carries it. A batch that cannot affect a cell (docs, data, tests, the gate,
# promotion and reporting machinery) owes neither, and the classifier says so
# without anyone asking; anything else waived is the maintainer's risk call,
# made with the label, and when in doubt run the full suite. What the gate
# owes in return is that a waived batch says so: this script names the dropped
# entries on every run under the skip, and `ci.yml`'s waiver step annotates
# the PR and writes the reason and the trade into the run summary.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"

# Keep in step with the dispatch-command list the promote workflow prints on a
# freshness failure, and with the `gate: true` legs of the suite literal in
# integration-test.yml — a `scenario=gate` dispatch must fan out exactly this
# set (a workflow-shape test pins both couplings).
REQUIRED_SCENARIOS="${PROMOTION_SCENARIOS:-ranged-reads corpus-service stub-cascade mcp-sidecar collect qp-topic engine-smoke/claude-code engine-smoke/codex engine-smoke/gemini engine-actions-smoke/claude-code engine-actions-smoke/codex engine-actions-smoke/gemini}"

# The engine skip (see the header): a filter over whatever set is in
# force, so it composes with a local PROMOTION_SCENARIOS narrowing instead of
# racing it. Fails closed — only the literal `1` drops anything. Both
# token-spending families leave together, and they have to: the whole-suite
# acceptance the skip unlocks returns before this set is ever looped over, so a
# filter that kept one family required would not make the gate stricter — a
# green `offline-gate` title, from a suite that ran neither, would satisfy the
# kept entry without exercising it. Unsound rather than strict, which is worse
# than the relaxation it looks like.
if [ "${PROMOTION_SKIP_SMOKE:-}" = 1 ]; then
  kept=""
  dropped=""
  for entry in $REQUIRED_SCENARIOS; do
    case "$entry" in
      engine-smoke/* | engine-actions-smoke/*)
        dropped="${dropped:+${dropped} }${entry}"
        continue
        ;;
    esac
    kept="${kept:+${kept} }${entry}"
  done
  REQUIRED_SCENARIOS="$kept"
  # Say what left the set, on stdout, on every stage. A gate that quietly
  # checks less than its name implies is the failure mode the skip is one
  # short typo away from; naming the entries makes a waived run readable as
  # waived from its log alone, without reconstructing which surface set the
  # variable.
  echo "promotion gate: engine scenarios waived — not required at this sha: ${dropped:-none}"
fi

fail=0

# The head refs a promotion may come from: staging itself, or a train
# candidate's frozen branch. Anchored and fixed-vocabulary, because the ref is
# interpolated into the freshness stage's jq filter.
HEAD_REF_PATTERN='^(staging|promote/[0-9]{4}-[0-9]{2}-[0-9]{2}(-([2-9]|[1-9][0-9]+))?)$'

head_ref() {
  local ref="${1:-staging}"
  if ! [[ "$ref" =~ $HEAD_REF_PATTERN ]]; then
    echo "::error::head ref '${ref}' is neither staging nor a promote/<date> candidate" >&2
    exit 2
  fi
  printf '%s' "$ref"
}

provenance() {
  local sha="$1" ref="$2"
  if [ "$ref" = staging ]; then
    return
  fi
  if ! git rev-parse --verify -q "origin/staging^{commit}" >/dev/null; then
    echo "::error::provenance: origin/staging is not fetched — fetch staging first"
    fail=1
    return
  fi
  # grep reads the whole list (no -q): an early exit would SIGPIPE rev-list,
  # and pipefail would then read a cut on the chain as one off it.
  if ! git rev-list --first-parent origin/staging | grep -Fx "$sha" >/dev/null; then
    echo "::error::provenance: ${ref} at ${sha} is not on staging's first-parent chain — not a cut of staging"
    fail=1
  fi
}

quiesce() {
  local wf status n
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
  local sha="$1" ref="$2" titles req scenario engine prefix
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
  # from the promotion's own head ref — staging, or the frozen candidate
  # branch, which resolves the staging environment — before a title is even
  # read; the
  # newline exclusion means a title that somehow preserved one could never
  # split into a fabricated extra line; and the matches are anchored.
  titles=$(gh api "repos/${REPO}/actions/workflows/integration-test.yml/runs?head_sha=${sha}&per_page=100" \
    --jq '.workflow_runs[]
          | select(.conclusion == "success" and .head_branch == "'"${ref}"'"
                   and ((.display_title | test("\n")) | not))
          | .display_title')
  # A `scenario=gate` dispatch fans the whole required suite out as one
  # workflow run, so one green `gate` title at the sha satisfies every
  # required scenario at once. The equivalence holds link by link: this exact
  # title shape is produced only by a `gate` dispatch (a per-scenario run
  # always carries `<scenario> / <engine>`); a `gate` run covers the whole
  # required set — the matrix legs with fail-fast off plus the collect job,
  # separate jobs in the same run — so the run concludes success only when
  # every job succeeded; and `@ staging` names the environment every matrix
  # leg bound, which only the staging branch may deploy to (the collect job
  # binds none by design — its evidence rests on the head_branch pin above,
  # which every title here already passed). Matched whole-line
  # (-Fx): the title is one fully-fixed string. Only titles selected as
  # success above are searched, so a match is a green run, never a red one.
  # Skipped entirely under a PROMOTION_SCENARIOS override: the `gate` matrix
  # covers the default set, so an overridden set — which may name something
  # beyond it — must be satisfied by per-scenario runs.
  #
  # Only the two gate titles are read. The workflow's `all` and `all-offline`
  # runs contain these suites today, but their membership is "every scenario
  # the workflow offers", which a workflow edit may move — add a diagnostic
  # that is red by design, drop a broken one — without that edit being a
  # change to this gate. Accepting them would make every such edit a gate
  # change in disguise, so a superset run earns no credit here: the gate's
  # evidence is the run whose name says it is the gate's.
  if [ -z "${PROMOTION_SCENARIOS:-}" ]; then
    if grep -Fqx "integration-test: gate @ staging" <<<"$titles"; then
      return
    fi
    # Under the engine-smoke skip the requirement is the smaller suite, which
    # an `offline-gate` run covers leg for leg — same jobs, same environment
    # binding, same success-only-when-every-job-succeeded arithmetic, minus
    # the six token-spending legs the skip already removed. The `gate`
    # acceptance above stays first and unconditional: a full run is always
    # sufficient evidence for a subset of what it ran.
    if [ "${PROMOTION_SKIP_SMOKE:-}" = 1 ] \
      && grep -Fqx "integration-test: offline-gate @ staging" <<<"$titles"; then
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
# Deliberately NOT part of `promotion-gate.sh all`: reading a ruleset needs admin-level access,
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

  # The review hold is only a gate while the environment carries
  # required reviewers: GitHub auto-creates a referenced environment
  # unprotected, and an unprotected hold releases instantly with no signal
  # that it did not gate. Enforced here — the same admin-read stage that
  # verifies the rulesets — from the moment main's workflows reference the
  # environment; before that the check reports itself skipped.
  # Both YAML spellings of the binding — the inline scalar and the mapping
  # form a later `url:` addition would introduce; a grep that knew only one
  # would skip the check exactly when main really binds the environment.
  if grep -rqE '^[[:space:]]*(environment:[[:space:]]+review|name:[[:space:]]+review)[[:space:]]*$' "$main_workflows"; then
    local protections
    protections="$(gh api "repos/${REPO}/environments/review" \
      --jq '[.protection_rules[]?.type] | join(",")' 2>/dev/null || true)"
    case "$protections" in
      *required_reviewers*)
        echo "contexts: the review environment carries required reviewers"
        ;;
      *)
        echo "::error::contexts: the review environment has no required reviewers — the spend hold is inert; configure the environment before promoting anything that relies on it"
        fail=1
        ;;
    esac
  else
    echo "contexts: the review environment is not yet referenced on main; environment check skipped"
  fi

  # The auto-release environment is the review hold's reviewer-less twin: a
  # predict round whose plan is within `config/review-hold.yaml`'s caps binds
  # `review-auto` instead of `review`. It runs without reviewers (that is its
  # purpose; adding one is auto-release's emergency stop, so reviewers are not
  # checked), so what keeps it a narrow path is everything else: deployments
  # from `main` alone, so only a promoted workflow can add to or bind it, and
  # no secrets or variables, so binding it reaches nothing. GitHub would
  # auto-create it on first reference with no branch policy at all. A tag
  # policy is listed with its type, so one named `main` cannot pass for the
  # branch. Checked
  # from the moment main's workflows reference it, like the review check above.
  if grep -rqE "review-auto" "$main_workflows"; then
    local auto_policy auto_branches auto_secrets auto_vars
    auto_policy="$(gh api "repos/${REPO}/environments/review-auto" \
      --jq '.deployment_branch_policy.custom_branch_policies // false' 2>/dev/null || true)"
    auto_branches="$(gh api "repos/${REPO}/environments/review-auto/deployment-branch-policies" \
      --jq '[.branch_policies[]? | if (.type // "branch") == "branch" then .name else "\(.type):\(.name)" end] | join(",")' 2>/dev/null || true)"
    auto_secrets="$(gh api "repos/${REPO}/environments/review-auto/secrets" \
      --jq '.total_count' 2>/dev/null || true)"
    auto_vars="$(gh api "repos/${REPO}/environments/review-auto/variables" \
      --jq '.total_count' 2>/dev/null || true)"
    if [ "$auto_policy" = "true" ] && [ "$auto_branches" = "main" ] \
      && [ "$auto_secrets" = "0" ] && [ "$auto_vars" = "0" ]; then
      echo "contexts: the review-auto environment is restricted to main and carries no secrets or variables"
    else
      echo "::error::contexts: the review-auto environment must restrict deployments to 'main' alone with a named custom policy and carry no secrets or variables (policy: ${auto_policy:-unread}, branches: ${auto_branches:-unread}, secrets: ${auto_secrets:-unread}, variables: ${auto_vars:-unread}) — fix the environment before promoting anything that binds it"
      fail=1
    fi
  else
    echo "contexts: the review-auto environment is not yet referenced on main; environment check skipped"
  fi

  # The review and tag-record rulesets: the approval `main` requires and who
  # may give it, staging's code-owner review, and the record tags' update,
  # deletion and creation rules, each with the bypass list the docs record.
  # All live in settings, so a promotion would otherwise outlive one being
  # edited away unnoticed. Each ruleset is fetched whole (the list endpoint
  # omits rules) and judged by tested Python (tests/test_ruleset_checks.py).
  # Bypass lists come back only to an admin, so the read must be one; the
  # identities they must name are resolved here rather than pinned in code.
  local ruleset_ids id is_admin team_id data_app_id dev_app_id
  local rulesets_dir="${workdir}/rulesets"
  is_admin="$(gh api "repos/${REPO}" --jq '.permissions.admin' 2>/dev/null || true)"
  team_id="$(gh api "orgs/${REPO%%/*}/teams/maintainers" --jq '.id' 2>/dev/null || true)"
  data_app_id="$(gh api "apps/fedcourtsai-data" --jq '.id' 2>/dev/null || true)"
  dev_app_id="$(gh api "apps/fedcourtsai-dev" --jq '.id' 2>/dev/null || true)"
  if [ "$is_admin" != "true" ]; then
    echo "::error::contexts: the ruleset check needs an admin token — bypass lists are invisible to any other, and a check that cannot see them proves nothing about them"
    fail=1
  elif [ -z "$team_id" ] || [ -z "$data_app_id" ] || [ -z "$dev_app_id" ]; then
    echo "::error::contexts: could not resolve the maintainers team or the data/dev App ids (team: ${team_id:-unread}, data: ${data_app_id:-unread}, dev: ${dev_app_id:-unread})"
    fail=1
  elif ruleset_ids="$(gh api --paginate "repos/${REPO}/rulesets" --jq '.[].id' 2>/dev/null)" \
    && [ -n "$ruleset_ids" ]; then
    mkdir -p "$rulesets_dir"
    for id in $ruleset_ids; do
      if ! gh api "repos/${REPO}/rulesets/${id}" >"${rulesets_dir}/${id}.json" 2>/dev/null; then
        rm -f "${rulesets_dir}/${id}.json"
        echo "::error::contexts: could not read ruleset ${id}"
        fail=1
      fi
    done
    if uv run fedcourts assert-rulesets --rulesets-dir "$rulesets_dir" \
      --reviewer-team-id "$team_id" --data-app-id "$data_app_id" --dev-app-id "$dev_app_id"; then
      echo "contexts: the review and tag-record rulesets hold"
    else
      fail=1
    fi
  else
    echo "::error::contexts: could not list the repository's rulesets"
    fail=1
  fi

  # The staging environment's mirror of the same failure mode: the staging
  # read-write role's trust names `environment: staging` — deliberately, the
  # environment every staging reader binds (docs/security.md) — which makes
  # that environment's deployment-branch policy the one thing keeping the only
  # write-capable role outside `corpus-write` off arbitrary branches. Unconditional,
  # unlike the review-environment check above: the trust exists from the
  # moment the role is provisioned on the AWS side, before any workflow that
  # binds it reaches main, and the policy predates the role (the integration
  # runs need it too) — so there is no state in which checking it early is
  # wrong, and the silent window an arming key would leave is exactly the one
  # between provisioning and promotion.
  #
  # Two names are admitted, and nothing else: `staging`, and `promote/*`, the
  # promotion train's frozen candidate branches, whose integration gate runs
  # bind this environment. Those branches are only ever created by the dev
  # App at a commit already on staging and are never updated — the two
  # `promote:` branch rulesets, checked below with the others, are what make
  # admitting the pattern no wider than admitting staging.
  local branch_policy policy_name policy_ok=true saw_staging=false
  # `deployment_branch_policy.custom_branch_policies` means named branches;
  # the names themselves are a second call. A tag policy is listed with its
  # type, so one named `staging` cannot pass for the branch.
  branch_policy="$(gh api "repos/${REPO}/environments/staging/deployment-branch-policies" \
    --jq '[.branch_policies[]? | if (.type // "branch") == "branch" then .name else "\(.type):\(.name)" end] | join(",")' 2>/dev/null || true)"
  IFS=',' read -r -a policy_names <<<"$branch_policy"
  for policy_name in ${policy_names[@]+"${policy_names[@]}"}; do
    case "$policy_name" in
      staging) saw_staging=true ;;
      'promote/*') ;;
      *) policy_ok=false ;;
    esac
  done
  if [ "$saw_staging" = true ] && [ "$policy_ok" = true ]; then
    echo "contexts: the staging environment is restricted to the staging branch and the promote/* candidates"
  else
    echo "::error::contexts: the staging environment must restrict deployments to 'staging' (and, for the promotion train, 'promote/*') by named custom policies and nothing else (found: ${branch_policy:-unread}) — the staging read-write role its trust names would be reachable from any other ref that can dispatch; fix the environment's branch policy"
    fail=1
  fi

  # The corpus-check environment, on the staging check's reasoning and just as
  # unconditional: the read-only role's trust names `environment:corpus-check`,
  # so an environment that is missing, reviewer-less or open to any branch hands
  # that role to whatever branch workflow binds it — and GitHub auto-creates a
  # referenced environment with neither control. Required: the environment
  # exists, its reviewer rule names the configured approver (resolved to an id
  # here, as the ruleset check resolves the team and App ids), its branch
  # policy admits `main` alone, and it holds no secret and no variable but the
  # read-only role's three. The decision is tested Python
  # (tests/test_environment_checks.py); this only fetches what it judges.
  local cc_dir="${workdir}/corpus-check-environment" cc_base approver approver_id
  cc_base="repos/${REPO}/environments/corpus-check"
  mkdir -p "$cc_dir"
  approver="$(uv run fedcourts corpus-check-approver 2>/dev/null || true)"
  approver_id=""
  if [ -n "$approver" ]; then
    approver_id="$(gh api "users/${approver}" --jq '.id' 2>/dev/null || true)"
  fi
  gh api "$cc_base" >"${cc_dir}/environment.json" 2>/dev/null \
    || rm -f "${cc_dir}/environment.json"
  gh api "${cc_base}/deployment-branch-policies?per_page=100" \
    >"${cc_dir}/branch-policies.json" 2>/dev/null || rm -f "${cc_dir}/branch-policies.json"
  gh api "${cc_base}/secrets?per_page=100" >"${cc_dir}/secrets.json" 2>/dev/null \
    || rm -f "${cc_dir}/secrets.json"
  gh api "${cc_base}/variables?per_page=30" >"${cc_dir}/variables.json" 2>/dev/null \
    || rm -f "${cc_dir}/variables.json"
  local approver_args=()
  if [ -n "$approver_id" ]; then
    approver_args=(--approver-id "$approver_id")
  fi
  if uv run fedcourts assert-corpus-check-environment \
    --environment-file "${cc_dir}/environment.json" \
    --branch-policies-file "${cc_dir}/branch-policies.json" \
    --secrets-file "${cc_dir}/secrets.json" \
    --variables-file "${cc_dir}/variables.json" \
    ${approver_args[@]+"${approver_args[@]}"}; then
    echo "contexts: the corpus-check environment holds its reviewer, its main-only policy and only the read-only role's variables"
  else
    echo "::error::contexts: fix the corpus-check environment before promoting — the read-only role's trust names it (docs/security.md)"
    fail=1
  fi

  # The corpus-check-auto environment, on the same reasoning and just as
  # unconditional: the read-only role's trust names
  # `environment:corpus-check-auto` too, and that environment has no reviewer
  # by design, so its `main`-only branch policy is its one control — a missing
  # environment is one any branch's workflow creates unprotected by binding it.
  # Required: it exists, admits `main` alone, and holds no secret and no
  # variable but the read-only role's three. Reviewers are not checked: one
  # added there is the stop for the unapproved path. The decision is tested
  # Python (tests/test_environment_checks.py).
  local cca_dir="${workdir}/corpus-check-auto-environment" cca_base
  cca_base="repos/${REPO}/environments/corpus-check-auto"
  mkdir -p "$cca_dir"
  gh api "$cca_base" >"${cca_dir}/environment.json" 2>/dev/null \
    || rm -f "${cca_dir}/environment.json"
  gh api "${cca_base}/deployment-branch-policies?per_page=100" \
    >"${cca_dir}/branch-policies.json" 2>/dev/null || rm -f "${cca_dir}/branch-policies.json"
  gh api "${cca_base}/secrets?per_page=100" >"${cca_dir}/secrets.json" 2>/dev/null \
    || rm -f "${cca_dir}/secrets.json"
  gh api "${cca_base}/variables?per_page=30" >"${cca_dir}/variables.json" 2>/dev/null \
    || rm -f "${cca_dir}/variables.json"
  if uv run fedcourts assert-corpus-check-auto-environment \
    --environment-file "${cca_dir}/environment.json" \
    --branch-policies-file "${cca_dir}/branch-policies.json" \
    --secrets-file "${cca_dir}/secrets.json" \
    --variables-file "${cca_dir}/variables.json"; then
    echo "contexts: the corpus-check-auto environment admits main alone and holds only the read-only role's variables"
  else
    echo "::error::contexts: fix the corpus-check-auto environment before promoting — the read-only role's trust names it (docs/security.md)"
    fail=1
  fi

  # The website environment, unconditionally: it holds the Buttondown API key
  # from the moment it is configured, whether or not main's workflows bind it
  # yet, and its `main`-only branch policy is the one thing keeping that key
  # from a workflow run off any other ref — so long as the key lives nowhere
  # else, since a workflow's secret falls back to a repository or organization
  # secret of the same name. Required: the environment exists, admits `main`
  # alone, holds exactly the key and the weekly tag id, and no repository or
  # organization secret shares the key's name. The decision is tested Python
  # (tests/test_environment_checks.py).
  local web_dir="${workdir}/website-environment" web_base
  web_base="repos/${REPO}/environments/website"
  mkdir -p "$web_dir"
  gh api "$web_base" >"${web_dir}/environment.json" 2>/dev/null \
    || rm -f "${web_dir}/environment.json"
  gh api "${web_base}/deployment-branch-policies?per_page=100" \
    >"${web_dir}/branch-policies.json" 2>/dev/null || rm -f "${web_dir}/branch-policies.json"
  gh api "${web_base}/secrets?per_page=100" >"${web_dir}/secrets.json" 2>/dev/null \
    || rm -f "${web_dir}/secrets.json"
  gh api "${web_base}/variables?per_page=30" >"${web_dir}/variables.json" 2>/dev/null \
    || rm -f "${web_dir}/variables.json"
  gh api "repos/${REPO}/actions/secrets?per_page=100" \
    >"${web_dir}/repository-secrets.json" 2>/dev/null || rm -f "${web_dir}/repository-secrets.json"
  gh api "repos/${REPO}/actions/organization-secrets?per_page=100" \
    >"${web_dir}/organization-secrets.json" 2>/dev/null \
    || rm -f "${web_dir}/organization-secrets.json"
  if uv run fedcourts assert-website-environment \
    --environment-file "${web_dir}/environment.json" \
    --branch-policies-file "${web_dir}/branch-policies.json" \
    --secrets-file "${web_dir}/secrets.json" \
    --variables-file "${web_dir}/variables.json" \
    --repository-secrets-file "${web_dir}/repository-secrets.json" \
    --organization-secrets-file "${web_dir}/organization-secrets.json"; then
    echo "contexts: the website environment admits main alone and holds only the Buttondown key and the tag id"
  else
    echo "::error::contexts: fix the website environment before promoting — its branch policy is what keeps the Buttondown key on main (docs/security.md)"
    fail=1
  fi

  # The corpus-write environment, unconditionally, on the corpus-check
  # check's reasoning: the production read-write role's trust is to name
  # `environment:corpus-write` alone — an IAM statement this stage cannot
  # read, so it checks only the environment — and from the moment the trust
  # names it, an environment that is missing or open
  # to any branch hands that role to whatever branch workflow binds it — and
  # GitHub auto-creates a referenced environment with no branch policy.
  # Required: the environment exists, its branch policy admits `main` alone,
  # and it holds no secret or variable outside the names the writer jobs read.
  # The decision is tested Python (tests/test_environment_checks.py).
  local cw_dir="${workdir}/corpus-write-environment" cw_base
  cw_base="repos/${REPO}/environments/corpus-write"
  mkdir -p "$cw_dir"
  gh api "$cw_base" >"${cw_dir}/environment.json" 2>/dev/null \
    || rm -f "${cw_dir}/environment.json"
  gh api "${cw_base}/deployment-branch-policies?per_page=100" \
    >"${cw_dir}/branch-policies.json" 2>/dev/null || rm -f "${cw_dir}/branch-policies.json"
  gh api "${cw_base}/secrets?per_page=100" >"${cw_dir}/secrets.json" 2>/dev/null \
    || rm -f "${cw_dir}/secrets.json"
  gh api "${cw_base}/variables?per_page=30" >"${cw_dir}/variables.json" 2>/dev/null \
    || rm -f "${cw_dir}/variables.json"
  if uv run fedcourts assert-corpus-write-environment \
    --environment-file "${cw_dir}/environment.json" \
    --branch-policies-file "${cw_dir}/branch-policies.json" \
    --secrets-file "${cw_dir}/secrets.json" \
    --variables-file "${cw_dir}/variables.json"; then
    echo "contexts: the corpus-write environment admits main alone and holds only the writers' names"
  else
    echo "::error::contexts: fix the corpus-write environment before promoting — the production read-write role's trust is to name it (docs/security.md)"
    fail=1
  fi
}

registry() {
  local sha="$1" main
  # Refuse rather than read a missing `main`: the stage compares the batch
  # against main's ledger, registry and tags, and a ref that is not there
  # would read as a registry-less main with an empty ledger. The stage does
  # not fetch — CI's checkout already holds every branch and tag — so a local
  # run fetches first: `git fetch origin --tags`.
  if ! main="$(git rev-parse --verify -q "origin/main^{commit}")"; then
    echo "::error::registry: origin/main is not fetched — fetch main and the tags first"
    fail=1
    return
  fi
  echo "registry: checking ${sha} against origin/main at ${main}"
  # The checks are tested Python (tests/test_registry_gate.py); this only
  # names what it compares.
  if ! uv run fedcourts registry-gate --at "$sha" --main-ref origin/main; then
    fail=1
  fi
}

contexts_due() {
  local sha="$1"
  if ! git rev-parse --verify -q "origin/main^{commit}" >/dev/null; then
    echo "::warning::contexts-due: origin/main is not fetched, so whether this batch owes the contexts stage was not read"
    return
  fi
  # Advisory: a failed read is a warning, never a gate failure.
  if ! uv run fedcourts contexts-due --at "$sha" --main-ref origin/main; then
    echo "::warning::contexts-due: the batch's paths could not be read; run the contexts stage if unsure"
  fi
}

case "${1:-}" in
  quiesce)
    quiesce
    ;;
  freshness)
    ref="$(head_ref "${3:-}")"
    freshness "${2:?usage: promotion-gate.sh freshness <sha> [<head-ref>]}" "$ref"
    ;;
  provenance)
    ref="$(head_ref "${3:-}")"
    provenance "${2:?usage: promotion-gate.sh provenance <sha> [<head-ref>]}" "$ref"
    ;;
  contexts)
    contexts "${@:2}"
    ;;
  contexts-due)
    contexts_due "${2:?usage: promotion-gate.sh contexts-due <sha>}"
    ;;
  registry)
    registry "${2:?usage: promotion-gate.sh registry <sha>}"
    ;;
  all)
    ref="$(head_ref "${3:-}")"
    quiesce
    provenance "${2:?usage: promotion-gate.sh all <sha> [<head-ref>]}" "$ref"
    freshness "$2" "$ref"
    registry "$2"
    contexts_due "$2"
    ;;
  *)
    echo "usage: scripts/promotion-gate.sh {quiesce|freshness <sha> [<head-ref>]|provenance <sha> [<head-ref>]|contexts [candidate...]|contexts-due <sha>|registry <sha>|all <sha> [<head-ref>]}" >&2
    exit 2
    ;;
esac

if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "promotion gate: ${1} clean"
