# Security setup (operational runbook)

The concrete configuration behind the invariants in [SECURITY.md](../SECURITY.md):
the GitHub App, branch protection, the `prod` environment, and the S3 roles.
SECURITY.md says *what* the invariants are; this says *how* they are wired, so a
maintainer can reproduce or audit the setup.

## The two GitHub Apps

Cross-workflow handoffs and PRs are made with a **GitHub App installation token**
(`actions/create-github-app-token`), never the default `GITHUB_TOKEN`: events
created with `GITHUB_TOKEN` do not trigger other workflows (GitHub's
loop-prevention), so a `run-pull` issue would never start `run-predict`, and an
agent PR would never start CI.

The token comes from one of **two Apps, split by trust** — mirroring the two S3
roles. The split is what makes "data writes land directly, everything agentic
lands via a PR" an *identity*-enforced invariant rather than a policy the
agent is merely instructed to follow (that the PR is *reviewed* is a
convention `AGENTS.md` carries, not something identity enforces):

- **data App** — used by the deterministic writers `run-pull` and `run-seed`.
  Its client id is the `DATA_APP_CLIENT_ID` variable and its private key the
  `DATA_APP_PRIVATE_KEY` secret. This App **is** a bypass actor on `main: require
  PR`, so the writers push corpus facts straight to `main`.
- **dev App** — used by the agent workflows `run-predict` /
  `run-evaluate` and the reviewed-PR openers (`run-backtest`, and
  `run-analytics`'s metrics-refresh job). Its client id
  is the `DEV_APP_CLIENT_ID`
  variable and its private key the `DEV_APP_PRIVATE_KEY` secret. This App is
  **not** a bypass actor, so nothing it holds can reach `main` except through a
  PR that satisfies the required checks.

All four live on the `prod` environment (the two client ids as variables, the
two keys as secrets). Each workflow mints a token scoped to only what it needs:

| Workflow | App | Token scope | Notes |
|----------|-----|-------------|-------|
| `run-pull` | data | contents, issues | commit facts to `main`; open handoff issues; publish the verdict/frontier JSONs to `ops-metrics` |
| `run-seed` | data | contents (walker steps); ambient issues + actions:read (guard) | commit historical facts to `main`; publish the verdict; the guard raises the `pipeline-health` issue on the ambient token |
| `run-predict`, `run-evaluate` | dev | workflow token: contents, pull-requests · agent token: contents read + issues + pull-requests | the **agent** token is comment-only; the workflow commits |
| `run-backtest` | dev | contents, pull-requests | open the reviewed back-test PR (minted after the replay ran) |
| `run-analytics` (metrics-refresh job only) | dev | contents, pull-requests | open the reviewed metrics-refresh PR; the analysis modes hold no write token |
| `run-analytics` (qp-topic-label job only) | dev | contents, pull-requests | open the reviewed qp-topic labels PR; minted **after** the agent has run and the gate has passed, so no write-capable token exists while the labeler does — the agent step is passed the job's own ambient token as `github_token` (the action requires one, and its OIDC fallback would mint an App installation token defaulting to contents/issues/pull-requests *write*), capped at `contents: read` by the job's permissions block |
| `sync-staging` | dev | contents, pull-requests | open the main→staging sync PR and arm auto-merge. Deliberately the dev App, not the data App: an unattended scheduled job must not hold the one identity that bypasses `main: require PR`, and it needs no `main` write at all |

**Repository permissions each App must grant** (App settings → Permissions), at
the App level the union of what its workflows mint:

- **data App**: Contents and Issues — *read and write*. (No workflow mints a
  Pull-requests scope from it any more; dropping that grant at the App level is
  a safe tightening.)
- **dev App**: Contents, Issues, and Pull requests — all *read and write*. (No
  workflow mints a Workflows scope from it any more; dropping that grant at the
  App level is a safe tightening.)

After changing an App permission, **re-approve the installation** on the repo — a
new permission stays pending until an owner accepts it, and the minted token is
capped at the granted set until then.

Commits and PRs are attributed to each App's own bot user (the
`configure-git-identity` action resolves `<app-slug>[bot]` from the token), so
deterministic corpus pushes and agent PRs are visibly authored by different bots.

## Branch protection — the rulesets

The two `main` rulesets are split so the per-rule bypass is correct (a ruleset's
bypass list applies to the whole ruleset); further rulesets protect the
`staging` and `ops-metrics` branches. Both require-PR rulesets pin
`allowed_merge_methods` to **`merge, squash`**: `merge` because the sync and the
promotion must keep `main` and `staging` sharing history, `squash` because the
data-run `collect` PRs auto-merge with it, and no rebase because replaying
commits onto either branch would break that shared history and rewrite the
pre-registration record's commit ids.

- **`main: require PR`** — requires a pull request plus the status checks below
  to merge. **Bypass: the data App only**, so the deterministic writer jobs
  (`run-pull`, `run-seed`) push corpus facts (the corpus blob — rows and
  point-in-time snapshots — to the S3 corpus remote; its pointer, deterministic
  `outcome.json` and `event.yaml` records, and the seed lane's bounded
  attribution repairs to `main`) while all agent code changes — including
  anything the dev App holds —
  go through a PR gated on the required checks. The dev App is deliberately
  **absent** from this bypass list. Required approvals are `0` — the maintainer
  reviews at merge time by convention, not by rule; set to `1` if a second
  reviewer exists.
  - Required checks are exactly `gate`, `paths`, `promotion-gate`, and
    `main-base` (the latter two report `skipped` — satisfying the requirement —
    on every PR they do not gate). `main-base` is the merge-routing jail: it
    runs — and fails — only on a PR to `main` whose head
    is not a same-repo `staging` or reviewed non-feature lane, so a feature PR
    cannot ride around the promotion path by mistake. Rulesets cannot constrain
    a PR's source branch, which is why it is a check rather than a rule. Its
    job definition lives in `main`'s own `ci.yml`, so the context reports on
    every lane into `main`; adding a context like it goes through the *Adding
    a required status check* procedure in
    [pipeline.md](pipeline.md). `cleanup-paths` is
    deliberately **not** in the required list — a cleanup PR is never
    auto-merged, so it is review-time
    defense-in-depth. **Not** `zizmor` — it is path-filtered
    to `.github/**`, so requiring it would hang any PR that does not touch workflows.
  - `paths` is the **auto-merge path jail**. The predict/evaluate
    collect jobs open one PR per run that auto-merges when green, opened with the
    **dev App** token — which is *absent* from this bypass list, so its auto-merge
    is bound by these required checks rather than skipping them. `paths` enforces
    that such a PR only *adds* files under `data/` (the tested `fedcourts
    assert-paths`): a change touching code, a workflow, config, or an existing
    artifact fails the check and cannot auto-merge. It is a no-op that passes on
    every non-`*/run-*` branch, so requiring it never blocks an ordinary PR. The
    same jail runs producer-side in each collect job; requiring it here enforces
    the guarantee independently of the workflow that produced the branch. Two
    more producer-side gates run beside it there: a schema re-validation
    (failure downgrades the PR to a draft) and a secret scan (`fedcourts
    scan-diff-for-secrets`) over the run's changed files and its PR prose — a hit
    **withholds the branch** (nothing pushed, no PR; a redacted file/rule/line
    report goes to the trigger issue) because pushing would itself publish the
    secret. Earlier still, capture-time redaction rewrites credential-shaped
    runs in the harness-captured tool-call transcript (`retrieval_log.json`) to
    a `[redacted:…]` marker rather than withholding the run over them: that
    text is whatever a tool call carried, not something the agent chose to
    write. It names only the shapes it recognizes, and what it declines to
    rewrite it leaves byte-for-byte, so the scan reads exactly what it would
    have read had redaction never run and no finding is silenced. What it does
    not get is a backstop. The Fernet-token rule — the one prefix short enough
    to occur inside ordinary agent-authored text — therefore confirms a run's
    entropy before rewriting, and a run padded below the bar is what the scan's
    own entropy detector also reads as ordinary. Containment still catches the
    pipeline's own token however it is padded; for a third-party credential
    riding in a payload the confirmation is the only layer that sees it, which
    is why it scores windows and the run as a whole rather than averaging one
    span. The scan has no merge-time counterpart by design: its job is to act
    before the push, and it needs a live token env that the merge-time check —
    running on PR branches without the `prod` environment — cannot hold.
  - `cleanup-paths` is the destructive counterpart for the cleanup sweep. That
    sweep *deletes* out-of-scope predictions (the tested `fedcourts
    cleanup-out-of-scope-predictions`, run locally by a maintainer), so it is the
    one branch the append-only `paths` jail cannot cover; `cleanup-paths` instead
    requires every change on a `cleanup/*` branch to be a **delete** under a
    `data/cases/**/events/*/predictions/` subtree (the tested `fedcourts
    assert-cleanup-paths`). A cleanup PR is **never auto-merged** — a maintainer
    reviews and merges it — so this is review-time defense-in-depth. No-op on
    other branches.
- **`main: protect history`** — blocks force-pushes and branch deletion. **No
  bypass — neither App.** This is what guarantees the committed *history* of
  the predictions, outcomes, and evaluations under `data/` cannot be rewritten
  or dropped, even by a misbehaving writer that holds the data App's bypass
  token: a forward commit can delete a ledger record — the writer lane's
  attribution repairs do, bounded by their per-run blast-radius cap — but the
  deletion is itself a permanent, attributable commit, visible and revertible
  rather than silent.
- **`staging: require PR`** — the pre-merge branch every feature PR targets
  requires a pull request plus the required checks that can report on a
  staging-targeted PR: `gate` and `paths`. (`main`'s other two,
  `promotion-gate` and `main-base`, are structurally always-`skipped` here —
  each keys on a base of `main` — so requiring them would add no
  signal.) **Bypass: the repository
  admin role only**, the escape hatch for a main→staging sync when the ordinary
  PR path is unavailable; its content is by construction already-gated `main`
  history merged with already-gated `staging` history.
  (The GitHub Actions app is not offered as a ruleset bypass actor, and the
  `promote` workflow is deliberately read-only.) The scheduled `sync-staging`
  workflow does hold a write token to this branch — but it **bypasses
  nothing**: it opens an ordinary PR that must satisfy the same required checks
  as any other, and merges it only through them. Worth being precise about what
  binds there, since the sync PR is a special shape: `paths` is a genuine no-op
  for a head that is not a data-production branch, and the head sha may already
  carry a green `gate` from its push-to-`main` run — so the real control is
  `gate` re-running over the merged tree, which re-validates data and schemas.
  That is adequate for content that is by construction already-gated `main`
  history, and it is not the same as a human reading the diff.
  **Neither App is a bypass actor here**, so the
  identity-enforced "everything agentic lands via a PR" invariant
  holds one hop before `main` as well: the dev App token minted in the agent
  runs has no zero-PR path onto the promotion train or onto the ref the
  staging-environment deployments execute.
- **`ops-metrics: protect history`** — the same force-push and deletion block on the
  orphan `ops-metrics` branch, where `run-ops` appends its JSON snapshots and the
  corpus-writer path (`run-pull` and `run-seed`, via the `publish-corpus-verdict`
  action) publishes
  the data-validation verdict and live-frontier snapshot for `run-ops` to present.
  Every writer only ever does a normal append push (never a force-push), so the rule
  does not impede them; it guards the metrics history from accidental or malicious
  rewrite once the repo is public. No required PR (the jobs push directly) and no
  bypass needed.

## Repository merge settings

Settings → General → Pull Requests. The predict and evaluate `collect` jobs each
open one PR per run and ask GitHub to merge it
when the required checks pass; these settings are what let that happen and keep
the branch list clean. To reproduce the repo (or use it as a template), set:

| Setting | Value | Why |
|---------|-------|-----|
| **Allow auto-merge** | **on** | The `collect` job runs `gh pr merge --auto --squash`. With it off that call errors — the job degrades gracefully (logs a warning, leaves the PR open for a manual merge) but nothing auto-merges. |
| **Allow squash merging** | **on** | The run PR is squash-merged, so each run lands as one commit. |
| **Automatically delete head branches** | **on** | A new `predict/run-<id>` branch is pushed every run; without this they accumulate. (It cannot touch `main`: GitHub skips the default branch, and `main: protect history` refuses deletion from anyone.) |
| **Allow merge commits** | **on** | `sync-staging` merges `main` into `staging` with `--merge`. A squash or rebase would land a commit with no parent link to `main`'s tip, so the promotion gate's ancestry check would fail and the next sync would reopen the same PR forever. |

Rebase-merge is not used by the pipeline, and both require-PR rulesets pin
`allowed_merge_methods` to `merge, squash` — so it is refused on `main` and
`staging` regardless of the repo-level toggle. A rebase-merge of either
ancestry-critical merge would replay commits onto the target, breaking the
shared history *and* rewriting the pre-registration record's commit ids; no
lane needs it. Auto-merge does **not** weaken the gate: it is a
deferred merge that still waits for the required `gate` + `paths` checks, and the
dev App that opens these PRs is not a branch-protection bypass actor (above), so
the checks bind. The append-only `data/` jail (`paths`) is what makes
auto-merging agent output safe.

The predict/evaluate `collect` job latches each run's rolled-up agent flags onto
one long-lived `agent-feedback` tracking issue — the durable, centralized home for
a note that must survive even a fully-failed run that opens no PR. It posts that
comment with the job's **ambient `GITHUB_TOKEN`** (job-scoped **`issues: write`**),
*not* the dev App token: latching needs no cross-workflow trigger (`agent-feedback`
is a non-triggering label), which is the only reason a workflow here ever reaches
for the App token — so issue-write deliberately stays **off** the App token that
carries `contents: write` and opens the auto-merging PR. This mirrors `run-ops`,
which posts its `ops-dashboard` / `data-validation` issues with `GITHUB_TOKEN` the
same way, and `run-pull`, whose pipeline-runs dashboard row and failure-only
run-log issues ride the ambient token for the same reason (its App token is
reserved for the writes that must trigger downstream: the corpus commits and
the `run:predict` / `run:evaluate` handoff issues). The capability is therefore on the lower-trust, non-bypass token, scoped
to issue comments/creation only; and the agent never touches it (the per-cell agent
token stays comment-only and writes `flags.json` locally — the trusted `collect`
job does the surfacing). So docket text the agent ingests cannot reach it, and the
worst a misbehaving `collect` run can do with it is post an issue comment or read
the repository's own Actions artifacts — that job also holds `actions: read`, so
it can fetch its run's cell artifacts per artifact (four at a time) instead of
as a single fail-fast batch (a transient failure of which once discarded a
whole run's output). The grant is repo-wide read, as Actions scopes cannot be run-scoped; it
is acceptable here because `collect` runs no agent code and nothing
agent-controlled steers which API it calls.

The predict/evaluate `plan` job carries the same **ambient `GITHUB_TOKEN`
`issues: write`** for the same reason: when the scope gate empties the matrix it
closes the trigger issue (with a note) so the run doesn't orphan it, and closing an
issue triggers no workflow — so this stays on the lower-trust ambient token, never
the App token. Predict's `plan` also holds **`actions: read`**, on the same
ambient token and the same reasoning as `collect`: its stranded-run guard lists
recent runs and their artifact *names* (it downloads nothing) to avoid re-minting
cells that already ran, the grant is repo-wide because Actions scopes cannot be
run-scoped, and `plan` runs no agent code — the census step's only inputs are
this workflow's own run history.

## The `prod` environment

Every secret and the two production S3 role ARNs live on the `prod`
environment — the App
credentials, the Anthropic API key, the Codex/OpenAI key, the Gemini API key,
the CourtListener API token (used by pull's ingestion; by the MCP
sidecar composite's launch step — the cells', and `integration-test`'s
engine-smoke **codex** leg, which wires the same sidecar to exercise it —
whose background `mcp-serve` process serves agent
retrieval over localhost, the cells having no REST fallback, so no agent step
carries the token and no client config file does either; unset degrades the
agents to anonymous rate limits; and by the collect jobs' secret scan, which
needs the live value to search the run's output for it), the AWS role ARNs
and region, and the corpus remote URL (referenced by role, never committed). Every job that needs any of
them declares an environment, and every job outside `integration-test` declares
`prod` — with two deliberate exceptions. run-predict's `approval` job declares
**`review`**, an environment that exists *only* for its required reviewers.
It carries no secrets, no variables, no role, and no deployment-branch
policy; the job it gates runs one echo under `permissions: {}`, so the
environment grants nothing and merely withholds the matrix until a named
reviewer releases it — and any later spend hold (the evaluate gate, when it
lands) binds this same environment rather than minting its own. It must be
created **with required reviewers configured before the gate promotes**:
GitHub auto-creates a referenced environment unprotected, and an unprotected
`review` environment is no gate at all. Leave **prevent self-review off**: the run's actor is the
maintainer whenever the trigger label was applied by hand, and in a
single-maintainer org blocking self-approval would strand exactly those runs
in *Waiting* until the thirty-day expiry — the hold is a deliberateness gate
here, not two-person control, a call to revisit if a second maintainer
joins. `staging-corpus-refresh` declares **`staging`** — the same environment
the integration scenarios bind, because the staging read-write role's trust
deliberately names it (see *The staging corpus* below).

**The Gemini cell env allowlist carries `_cell_env`'s identifiers, the corpus
sidecar's two non-secret names, and nothing else.** Gemini's CLI sanitizer
strips every env var from the agent's shell in CI
(strict mode is forced by `GITHUB_SHA`), so the cell workflows name the cell
contract — court/docket/event/actor/run/model ids, plus the back-test's
`DECIDED_BEFORE` clock, plus `FEDCOURTS_CORPUS_BACKEND` and
`FEDCOURTS_CORPUS_SERVICE_URL` (a backend name and a localhost URL: the corpus
sidecar contract, and what gives this engine the corpus retrieval the sanitizer
could never grant via AWS credentials) —
under `security.environmentVariableRedaction.allowed` in
the `.gemini/settings.json` they generate. Those are public identifiers the agent
already holds inline in its own prompt, so the allowlist adds no information; it
exists so the agent can resolve its own cell's paths the way Claude and Codex do.
**Adding a name outside that contract needs a security review**: the CLI refuses
to allowlist `/TOKEN|SECRET|KEY|AUTH|CREDENTIAL|PRIVATE|CERT/i` names and screens
a handful of credential-shaped *values*, but both are heuristics — a
secret-carrying name that dodges the keyword list (and a value that is not one of
the ~8 known shapes) would pass. Relatedly, never put anything sensitive in a
`GEMINI_CLI_*` variable: that prefix is an unconditional bypass of both screens.

**Deployment branches are restricted to `main`** — on `prod` (and to `staging`
on the `staging` environment, whose policy is load-bearing twice over: the
read-only role's trust names it, and so does the one write-capable role
outside `prod`); `review`
deliberately carries no branch policy, since it holds nothing a branch could
take. A job can read the environment's
secrets only when it runs from `main`, so a workflow authored on a PR branch runs
**without** the App key, agent tokens, or S3 role: a malicious or prompt-injected
workflow added in a PR cannot exfiltrate secrets on its own PR run; the change
reaches the privileged context only after it is merged to `main`, which required
review.

Every `prod` job already runs from a `main` ref for its trigger — `schedule`,
`workflow_dispatch`, and `issues` — so the restriction breaks nothing.

**The integration-test workflow selects its environment by input**
(`deploy-environment`, a closed choice of `auto`/`prod`/`staging` defaulting to
branch resolution: a `main` dispatch resolves `prod`, a `staging` dispatch
`staging`, and any other branch its own
name; an explicit choice still wins). A dispatch whose job *binds* `prod` from
anything but `main`, or binds `staging` from anything but `staging`, is refused
at its deployment-branch gate before any step runs; an `auto` dispatch from any
other branch resolves that branch's own name, auto-creating an unprotected,
empty environment with no role variables —
the AWS roles' trust policies pin the OIDC `sub` to the named environments, so
it can assume nothing. The refusal keys on binding, not on the input string: the
collect scenario binds no environment and so dispatches from anywhere regardless
of what its input says.

**`staging` is restricted to the `staging` branch, and carries no reviewer
rule** — the same shape as `prod`, one branch lower. The branch policy is the
gate, and what it enforces is **code provenance**: only code that passed a pull
request plus the `gate` and `paths` checks on the `staging` ruleset can bind the
environment — with two carve-outs this document records above: the admin bypass
on that ruleset, and the absence of `strict_required_status_checks_policy`, so a
PR may be green against a stale base. It holds without a human present at
dispatch time, and it is a property of the *code* — which a per-run approval
does not assert, since the approval UI shows a workflow name and a ref, not a
diff.

A per-run approval is the stronger control against a *second* write-access
human, who could otherwise merge to `staging` (the ruleset requires zero
approving reviews) and reach the environment without the maintainer. It is
redundant against the arrangement that exists: no workflow declares
`actions: write`, neither App is granted an Actions scope, and the repo-scoped
token agents hold is refused on `workflow_dispatch` — so dispatching is already
a maintainer-only act, and with `prevent_self_review` off the approval is a
second click on the same decision by the same person. **Revisit the moment any
premise changes**: a second write-access collaborator; the first *token* that
can dispatch, whether a workflow declaring `actions: write` or either App
granted an Actions scope; the first workflow that binds `staging` on a
**non-dispatch trigger** — a `push` or `pull_request` filter naming the branch
would bind the environment on the merge itself, and agents merge their own PRs
to `staging`, which since the environment carries the staging write role's
trust would hand *write* reach on the fixture, not just read and spend, at an
agent's own merge; or **the `staging` environment being repointed at the
staging corpus** (the runbook's step 5), from which point the promotion gate's
freshness evidence is produced against a corpus the staging lane can write,
and the code that can write the evidence is the thing a reviewer would be
approving. The premise is the repointing, not the code that makes it
possible: an override no environment sets redirects nothing, so the wiring
landing leaves the gate's evidence exactly where it was. The re-seed practice
above keeps the evidence honest between reviews but does not answer that
question, so step 5 is where it must be answered rather than left standing on
this paragraph. No workflow filters on a
staging ref today; every branch filter names `main`.

What neither shape covers: the `staging` ruleset requires no workflow linter, so
a workflow change that reads a secret is caught by no *required* check.
`lint-actions` still runs zizmor and actionlint on any PR touching `.github/**`,
non-blockingly, and the branch policy forces such a change to become a PR diff
at all. The real control is `AGENTS.md`'s rule that `.github/workflows/**` and
`.github/actions/**` — the permission surface, composites included, since a
composite runs inside the job and reads the same secrets — wait for the
maintainer even into `staging`. Convention, not ruleset, and recorded as such.

Blast radius is bounded on **integrity of production**, not on confidentiality
or spend: staging's engine keys are separate and independently revocable, and
its **read-only** AWS role has no write path to the *production* corpus — but
that role reads and lists the access-gated corpus and the per-case content
store, and the environment now also carries a role that writes the staging
pair (next paragraph). So the exposure a workflow change at the staging head
buys is corpus *read*, model *spend*, and a write to the re-seedable staging
fixture — which is why the linter gap above is worth naming rather than
glossing.

**The staging read-write role adds a write to that radius, and it is the
kind that does not move the integrity bound.** Its trust names the `staging`
environment itself — deliberately, so staging rehearses production's
provenance model rather than adding an identity boundary production does not
have: in `prod` too, the write role trusts the environment every reader
binds, and review of what reaches the branch is the control. The symmetry is
the point — a change that wrongly writes fails *visibly here*, against the
disposable staging pair, in the testing the maintainer reads before
promotion, instead of failing an AssumeRole in staging (reading as
misconfiguration) and then succeeding first in production. What staging-head
code can now write is the staging pair: a lean slice of real cases, rebuilt
from production by one dispatch. It buys **no production write path** (the
role is read-only on the production stores by policy) and **no new read
surface** (the same slice the already-trusted read-only role can read in
full). What it does *not* dilute: the production corpus keeps exactly one
writer, and that writer is still reachable only from `main`. One control
changes weight rather than shape: the agent-env scrub (every `AWS_*` name and
every credential-shaped name stripped from the agent subprocess) was a read-
confidentiality control while staging's OIDC bought read alone; a
staging-bound job that holds `id-token: write` *and* runs an agent over
untrusted docket text — the engine-smoke legs — could otherwise mint the
write role's credentials, so the scrub is now load-bearing for the staging
pair's write integrity too.

What corrupting it *costs* depends on a coupling worth stating rather than
discovering. While the `staging` environment still names the production pair,
nothing committed depends on the staging corpus — the scenarios read
production's — so a corrupted slice is caught by the next integration run and
fixed by another dispatch. **The moment step 5 repoints it, the coupling is
immediate and not
hypothetical**: the staging integration runs are the promotion gate's freshness
evidence, so a staging corpus that is corrupt, empty, or subtly wrong makes
those runs fail or — worse — pass against the wrong content, and promotions
stall or proceed on evidence that did not test what it claims. That is a
denial-of-promotion and an evidence-integrity problem, not a nuisance, and it
arrives with the next change in this area rather than at some distant
contingency.

The corruption cost has a standing mitigation that keeps the evidence
honest: **re-seed before an evidence-bearing run**. The refresh lane rebuilds
the slice from production in one dispatch, so a promotion that leans on
staging results starts from a fixture the maintainer just reset — a poisoned
slice persists across runs in a way a lying workflow does not, and the
re-seed is what clears it.

The read-only role's trust names `staging`'s `sub` (the staging integration runs
assume it, so this is observed, not assumed); the **production** write role's
trust never names `staging` at all.
Restoring a lane for arbitrary branches, if one is ever wanted, means a
**separate** environment — its own keys, its own trust statement, and a required
reviewer, since arbitrary code is exactly what a human should see — not widening
this one. It needs no workflow change: `auto` resolution binds an environment
named after the dispatching branch, so provisioning the environment is itself
what opens its branch's lane — the environment's existence and contents, not
the workflow's choice list, are the control surface. The explicit
`deploy-environment` choices stay a closed vocabulary; the run title renders
the *resolved* environment (under `auto`, a branch name), and the promotion
gate's freshness match does not lean on that title being free of
dispatcher-chosen text — it pins the run's head branch to `staging` and
anchors its matches, and a ref name cannot carry the title's ` @ ` shape.

**The invariant behind the wiring order:** the environment must never be
reachable from an arbitrary branch while the read-only role's trust names it.
The trust is the standing fact, so the deployment-branch restriction is the
piece that must be in place first, and any future loosening of that branch
policy is a change to the trust statement too — not to the branch policy alone.
An environment reachable from any branch, with no gate above it, hands the
read-only role to whatever an agent last pushed.

The workflow's collect scenario binds no environment at all: its job holds no
secret and no role — the collect-run composite under test is handed a
placeholder in place of the App token, a `gh` shim stubs its PR surface, and
a git URL rewrite keyed on that placeholder diverts its branch push to a
runner-local scratch remote — so it dispatches from any branch, and there is
nothing for such a dispatch to reach. Its only
real credential is the ambient read-only token that lists and fetches the
run's own synthetic cell artifacts.

The workflow's engine-smoke scenario additionally — beyond the role
variables — reads one model-provider
secret — the selected engine's API key, chosen by expression ternary so the
other engines' keys never enter the job. An `all` dispatch fans one smoke per
engine, so a single run reads all three keys — each confined to its own job —
and spends three cells; `all-offline`, the same suite without the smoke legs,
reads no engine key and spends nothing. The keys live on the `prod`
environment and, as **separate per-environment secrets**, on `staging` — a
smoke dispatched at the staging head spends against staging's own keys
(independently revocable, isolated from tournament spend), so a promotion's
freshness runs cannot touch the tournament's budget. Spend is gated the same way
the read-only role is: by who may dispatch, and from which branch. A dispatch
naming an environment without the keys gets an
empty key and fails closed right alongside the role variables, independent of
step ordering. A codex smoke reads one secret more — the CourtListener token,
which reaches only the MCP sidecar composite's launch step env, exactly as a
live cell's does, so the agent step and the generated client config carry a
localhost URL and no token. That leg exists to exercise the MCP wiring itself:
it is the one engine whose transcript shapes no committed retrieval log has
ever exhibited, and the leg distills its rollout to item types and key names
(never a value) as an uploaded artifact — written to the runner temp dir
rather than the workspace the cell could write, so the published file is the
tested command's own output. The claim that survives scrutiny is the one about
values; a key name is emitted verbatim where it is identifier-shaped, so an
object keyed by retrieved data can export a fragment of up to 64 characters
(`docs/cli.md` states the bound). **Which of two artifacts a dispatch
yields depends on the environment it binds**, and a reader must know which
they hold: the token is a `prod` secret, and an environment that carries no
copy of its own — `staging` included, unless one has been added there
alongside its engine keys — launches the sidecar **token-free**, exactly as
the `mcp-sidecar` scenario does on purpose. That is a degradation, not a
failure: warn-only health, the handshake and the tool listing still succeed,
and tool *calls* error. Both artifacts answer the question the leg is for —
what an invocation looks like in the transcript, which under code mode is not
an MCP item at all but a call inside the freeform call's own source, so the
shape the retrieval parser keys on is the one a real rollout confirms — but
only the token-bearing one also shows what a settled call looks like. A codex smoke additionally loosens
the runner kernel's
AppArmor userns restriction (codex-action's own prerequisite for the live
cells) without dropping sudo afterwards — accepted for the same reason as in
the back-test residual below: same-user co-residency is already conceded as
a non-boundary, and this job holds only the read-only role, one engine
key, and the read-only CourtListener token. Within a run, the engine key rides the
single cascade step's env,
alongside the corpus sidecar's step-scoped read-only AWS credentials for the
cascade's own provisioning reads; the spawned agent sees neither, because the
runner seam's scrubbed base environment strips every AWS variable and every
credential-shaped name except the engine's own auth — the same posture as a
back-test replay cell.

## S3 / the private stores

Three IAM roles, assumed via GitHub OIDC (no static keys), cover both private
S3 stores — the corpus remote (the index blob under its content-addressed
`index/sha256/<digest>` keys) and the per-case content store — plus the staging
pair the third one writes:

- **Read-write role** (`AWS_ROLE_TO_ASSUME`, used by `run-pull` and `run-seed`) —
  **append-only**: it can read, list, and add objects, with an explicit
  `Deny` on every delete and on bucket-versioning changes. The
  content-addressed `fedcourts corpus-push` only ever adds objects (an
  existing digest key is left untouched), no run garbage-collects the remote,
  and the content store's write-once objects and versioned
  manifests never need a delete; this means no run can wipe corpus data.
- **Read-only role** (`AWS_ROLE_TO_ASSUME_READONLY`, used by every corpus
  *consumer* job — read and list only, so a compromised consumer runner
  cannot write or poison the corpus). Consumers reach it through three
  composites: `corpus-ranged` for the predict/evaluate **plan** jobs (role +
  backend env job-wide — fine where no agent runs; scope gating is point
  lookups over the named cases), `corpus-sidecar` for the predict/evaluate
  **cell** jobs (credentials stay step-scoped: the background `corpus-serve`
  process and the deterministic provisioning steps hold them, the agent steps
  never do — see below), and `corpus-readonly` for the scan-heavy
  full-pull consumers (`run-analytics` / the metrics refresh, and `run-backtest`).
- **Staging read-write role** (`AWS_ROLE_TO_ASSUME_STAGING_RW`, used by
  `staging-corpus-refresh` alone) — **read + list on the production stores**
  (the slice's source, the same access the read-only role grants) and
  **read + write on the staging corpus pair alone**. It is the only
  write-capable role outside `prod`, and it can write nothing production owns,
  so the production stores keep exactly one writer. Its trust names the
  `staging` environment and nothing else — the same environment the
  integration scenarios bind, deliberately (see the runbook's provenance
  note). Provisioning it — and the
  variable above, which step 4 of *The staging corpus* below sets and the
  workflow reads — is a maintainer task; see that runbook.

Access mirrors each workflow's role in the pipeline:

| Workflow                                  | Role / access | Why                              |
|-------------------------------------------|---------------|----------------------------------|
| `run-pull` (pull + live + enrich jobs), `run-seed` | read-write | corpus writers (`corpus-push` + content-store mirror) |
| `run-predict`, `run-evaluate` — plan jobs | read-only | scope gating over the named cases — ranged point lookups, no pull |
| `run-backtest`                            | read-only     | replay: full index `corpus-pull` + redacted snapshots from the content store |
| `run-predict`, `run-evaluate` — cell jobs | read-only, **step-scoped** | record provisioning + the corpus sidecar's ranged queries; the credentials ride the sidecar/provisioning steps only, never an agent step (no pull) |
| `run-analytics`                           | read-only     | scan-heavy analysis / metrics refresh (full `corpus-pull`) |
| `run-analytics` — qp-topic-extract        | read-only     | the labeler's extract (full `corpus-pull`), handed to the labeling job as an artifact |
| `run-analytics` — qp-topic-label          | none          | the agent job assumes no role and has no `id-token: write`: its whole *evidentiary* input is that artifact, and a step asserts both the AWS and the OIDC variables are absent before the agent runs |
| `integration-test`                        | read-only     | infrastructure preflight scenarios (role assumed directly or via the sidecar composite; no pull) |
| `staging-corpus-refresh`                  | **staging read-write** (read-only on production) | seeds the staging pair from a production slice; the only write-capable role outside `prod`, and it can write nothing production owns |
| `run-ops`                                 | none          | dashboard reads GitHub state only |
| `ci`                                      | none          | gate stays offline/fast          |

The split is deliberate: a plan job gates only the cases its trigger names and
a cell touches KBs of one case's data, so both read the immutable index in
place and move no full blob; only the whole-corpus scanners (`run-analytics`
and `run-backtest`) keep the full pull.

Developer access is separate from the workflow roles: the maintainer uses IAM
Identity Center SSO, and a contributor gets an on-demand IAM user scoped
read-only to the corpus bucket — the one static credential in the system.

Every role's OIDC trust is scoped to named environments of this repo
(`...:sub` like `repo:<owner>/<repo>:environment:prod`), so only a job binding
one of those environments can assume it. The production read-write role names
`prod` alone; the read-only role also names `staging`, which is what lets the
integration scenarios read the corpus from the staging branch; and the staging
read-write role names `staging` alone. The trusts stay disjoint on
the write side by construction — no environment names two write-capable roles,
and no write-capable role names two environments — so "who can write which
store" is answerable from the trust statements without reading a policy.

**Agent shells hold no cloud credential; the residual is a localhost query
surface.** A predict/evaluate cell runs an agent over third-party snapshot
text — prompt injection in a docket must be assumed — but the read-only role's
credentials never enter an agent step's environment: the `corpus-sidecar`
composite takes them as masked step *outputs* (`output-credentials`, with the
job-env export disabled) and they appear only pre-agent — in the composite's
launch step, whose env the background `corpus-serve` process inherits, and in
the deterministic provisioning steps' step-scoped env. A guard step fails the job if any `AWS_*` credential is
visible in the job env when the agent steps begin, and this also levels the
engines: the Gemini sanitizer could never allowlist a credential, so every
engine queries the same credential-free surface rather than whichever one its
harness happens to let credentials reach. What replaces the old residual: the sidecar is
an **unauthenticated localhost HTTP surface**, so any process on the runner —
including the injected agent itself, which is the *intended* client — can
query the corpus and spend ranged-read egress through it. That is the same
read surface the cell is handed on purpose (public court data, KB-scale
lookups, no bucket enumeration or presigned URLs — the wire accepts a
structured query, not S3 operations), the role still cannot write or delete
(append-only remote, explicit deny, versioning on), the cell's GitHub token
cannot push code (the collect job owns git with its own token), and a billing
alarm bounds the egress-spend abuse case. On-runner step-scoping is a strict
improvement, not hard isolation: processes of the same runner user are not a
security boundary against a determined co-resident process; the boundary this
buys is that no agent's env, config file, or casual file read ever contains a
credential. The **qp-topic labeler** is the third agent surface and takes the
strictest form of the same line, because it needs no corpus access at all while
it runs: the credentialed half is a separate job, and the labeling job assumes
no role, declares no `id-token: write`, launches no sidecar, and is passed no
MCP config — so its whole evidentiary input is one downloaded extract, and its
guard step asserts both the `AWS_*` and the OIDC request variables are absent
before the agent starts. It also holds no write-capable GitHub token while it
runs: the App token is minted only after the agent finishes and the publication
gate passes. The cert back-test's replay cells hold the same line at a
different seam: their workflow process legitimately keeps the read-only
credentials job-wide (`corpus-readonly` — the replay needs a full local pull,
and under the corpus-split mode mid-replay content-store reads), so the shared
runner seam spawns each agent CLI from a scrubbed base environment instead —
every `AWS_*` variable except the region names is dropped, along with every
credential-shaped name (token/secret/password/credential/api-key/auth) that is
not the running engine's own declared auth, so the posture holds for names
nobody enumerated (a dev shell's GitHub token, an SSH agent socket). The
result matches the live cells — no agent process env carries a cloud
credential or another provider's key, enforced in one tested seam that also
covers the local cascade — with one residual stated plainly: unlike a live
cell, the credentialed process here is the agent's own concurrently-running
parent, so the same-user non-boundary above is more direct in this job.
(Codex's API-key auth adds one file to that same non-boundary: the pinned CLI
only accepts a key via `codex login`, so the runner seam logs in to a
run-scoped temp `CODEX_HOME` whose `auth.json` holds codex's own key for the
rest of the job — same-user readable, like the parent's environment already
is. The temp home is what the seam picks when the caller names none; a caller
that pins `CODEX_HOME` keeps it, and the engine-smoke codex leg does pin it —
to the workspace `.codex` the live cells use, because the cell must read the
MCP config written there and the shape distillation must find the session
rollout under it. That trades the temp dir for a gitignored workspace dir on
the same runner, under the same same-user non-boundary, and the job commits
nothing.) Running codex here also requires loosening the runner kernel's AppArmor
restriction on unprivileged user namespaces — the same sysctl prerequisite
codex-action applies for the live cells — and unlike codex-action, the
runner-seam jobs do not drop sudo afterwards: accepted out loud, because the
same-user parent-process residual above already dominates what reachable
sudo adds, and the other engines have always run unsandboxed in these jobs.

**The corpus-split mode constrains the read-only role's policy.**
**`FEDCOURTS_CORPUS_SPLIT=1`** (`Settings.corpus_split`) is set on the `prod`
environment: the entire forward predict/evaluate fleet provisions from the
casestore path (it overrides the env-configured `ranged` backend; an explicit
per-command `--corpus-backend` is the only thing that still wins), and the
casestore read path *does* list (`s3:ListBucket`) — a latest-snapshot-style
read lists a case's `snapshots/` to find the newest (`provision-snapshot`, the
writer's own change detection, the signal backfill), while pure `GetObject`
reads (`materialize-event`'s event/document reads, document leaves) do not.
The read-only role therefore keeps `s3:ListBucket`, and by decision it stays.
A `GetObject`-only narrowing was considered and not pursued: the casestore path
genuinely needs the list while the split is on, so dropping it is not an IAM
change but a code change (a per-case snapshot pointer to resolve the newest
snapshot as a deterministic key the reader can `GetObject` without listing) for
a marginal gain — and the index side already never lists (ranged reads resolve
the key from the committed pointer). The residual this leaves is bounded and
understood: on a bucket of only public court-derived objects, `ListBucket` lets
a holder *enumerate* the ingested-set extent — the compilation extent, the same
boundary `data/scope/scope.json` withholds from the committed public surface
(it can enumerate keys for ingested-but-unpublished dockets). The stated,
bounded exception to that boundary covers exactly two committed artifacts, both
argued and accepted in `docs/qp-topic.md` and nowhere else: the
hand-labeled qp-topic reference set, and a labeling run's per-case qp-topic
labels file over the roughly 1,200 QP-bearing rows. Each names
ingested-but-unpublished dockets by public docket number; the reference set's
membership is outcome-conditioned (presence predicts a cert grant), the labels
file's is fetch-conditioned (a questions-presented document is stored for that
case), and because the two are committed together the pair reconstructs the
QP-bearing non-grants by difference. That composition is the thing argued in
`docs/qp-topic.md`, alongside the non-git channel the labeling run adds — two
artifacts under the same one-day window, publicly downloadable on this
repository: its extract of stored petition text, riding between the mode's two
jobs, and the labeler's scanned turn-by-turn transcript, which embeds the same
text plus the agent's own turns. But it
widens
discovery, not reach: the role can already `GetObject` that content by key, and
the no-republication posture is license/content-based (see
[data-sources.md](data-sources.md)), not identity-based, so enumeration reads
out nothing the role could not already read given the keys. `ListBucket` is also
useful for console/Codespaces inspection and future read-side work. The
least-privilege line that carries the threat model is the one the role already
holds: **no write or delete** (append-only remote, explicit deny, versioning
on), the cell-blast-radius bound stated above.

On the bucket: **Versioning on** (recover from any accidental overwrite/delete),
a **lifecycle rule** expiring noncurrent versions after a recovery window, and
**Block Public Access on**.

## The staging corpus (provisioning runbook)

The production corpus is single-writer by construction — the write credentials
exist only inside `run-pull` and `run-seed` — which is exactly why no
orchestration change can be rehearsed against a real corpus before it is
promoted. The **staging corpus** is the surface that closes that gap: a lean
slice of real cases, in its **own bucket/prefix pair**, with the same two-store
shape the split-mode production system has, seeded by
`fedcourts corpus-seed-slice` from the dispatch-only
`staging-corpus-refresh` workflow.

**What does not change.** Production keeps its single-writer discipline
untouched: the production read-write role's trust still names `prod` alone and
no new job assumes it. **The guarantee is IAM** — the staging role's policy is
read-only on the production stores, so nothing in this lane can reach the
production write path whatever it is pointed at. The seeder's own rail, which
refuses a destination that *is, or is inside*, either store of its **pinned
source**, is the second line: it turns a misconfiguration into a local refusal
before anything is read. The source is pinned on the command line — dedicated
production-source variables in the workflow, explicit options in a shell —
never resolved from the ambient environment, so repointing the environment's
corpus variables moves neither what the seeder reads nor what its rail
compares against. Codespaces stays read-only: against production for
both developer flows, and against the staging pair for the maintainer's
role-assumed flow, whose read-only role's policy also reads it (see
[data-pipeline.md](data-pipeline.md)'s *Developer access* for the
`scripts/corpus-env` switch). A dev checkout can dry-run the seeder against
the read-only role, and its write half exists nowhere but the workflow below.
The pin makes the dry run shell-proof for the ranged read and the rail alike:
a staging-flipped shell cannot re-base what the rail refuses, and one carrying
the staging pointer override is refused outright. The one residual is the
`local` backend, which reads whatever pulled blob is on disk — the pin
governs the content store, the rail, and the ranged read — so dry-run ranged,
or re-pull production first.

Provisioning is AWS-and-environment work only the maintainer can do. **Steps
1-4 are the whole of what the refresh lane needs**, and they are ordered: each
is a prerequisite of the next, and until all four are done a dispatch fails
closed (an unset role variable resolves empty and the assume-role step
refuses). Do those four and the lane works — you can seed the staging corpus,
and step 6's first half is its acceptance.

**Step 5 and step 6's second half repoint the scenarios** at the seeded pair —
and only the scenarios. Step 5 hands the `staging` environment all four
scenario corpus variables at once, the pointer among them (see *How a consumer
resolves the staging index* below for why the pointer cannot be committed).
The refresh lane's source is pinned to its own production-source variables,
which this step never touches, so re-seeding stays available before and after
the repoint. Read step 5's two ordering notes before doing either.

1. **Create the staging bucket/prefix pair.** Two destinations, named by role
   rather than by literal here as everywhere in this document: a *staging
   corpus remote* (the content-addressed index blobs) and a *staging content
   store* (the per-case objects). Same bucket posture as production —
   versioning on, a noncurrent-version lifecycle rule, Block Public Access on —
   because it holds the same court-derived content, just less of it. Separate
   from the production bucket, not a prefix inside it: the point is that a role
   able to write staging is unable to **write** production at all — it reads
   and lists there, which is where the slice comes from (step 3), and that is
   the whole of its production reach. The seeder's rail enforces the separation
   from the other side, refusing any destination sharing a bucket with its
   pinned source — production, in this lane. The licence travels with the
   slice: it is CourtListener content
   under the same CC BY-ND no-republication posture
   ([data-sources.md](data-sources.md)), so the staging pair is access-gated on
   the same terms — **no wider read principal than production's**, nothing
   published from it, and it does not become a convenient place to stage a
   public extract.
2. **Verify the `staging` environment restricts deployments with a custom
   branch policy naming `staging`** — the named-policy mode, not "protected
   branches only": the gate's check reads the named policies, and the other
   mode reads as a missing policy. No new environment is created; the write
   role's trust
   deliberately names the environment the integration scenarios already bind,
   so staging rehearses production's provenance model (in `prod` too, the
   write role trusts the environment every reader binds, and review of what
   reaches the branch is the control — a change that wrongly writes fails
   visibly here, against the disposable pair, before it can succeed in
   production). The branch policy is the gate, and what it enforces is code
   provenance: only code that passed a pull request and the `staging`
   ruleset's checks can bind the environment and reach the role. It predates
   this role, but from the moment the trust statement below names the
   environment it is load-bearing for write provenance, and it must be in
   place *before* that trust exists, or the role is handed to whatever an
   agent last pushed.
   Because this policy is the load-bearing part, two other places check it
   rather than trusting it. The
   promotion gate's **admin-read `contexts` stage**, which the maintainer runs
   with their own token, verifies the environment's deployment-branch policy
   names `staging` — the same shape as its `review`-environment reviewer check,
   and skipped until main's workflows bind the staging write role's variable
   (main will reference the `staging` environment itself long before anything
   arms the role). It is
   deliberately **not** part of any automatic gate: reading environment and
   ruleset settings needs admin-level access that ci.yml's promotion-gate job
   does not hold, so a required check would 403 (see the rationale in
   `scripts/promotion-gate.sh`). It reports; it does not block. The
   **workflow itself** refuses a dispatch whose ref is not `staging` in its
   first step, so the lane never rests solely on a setting the job cannot read
   — that one *does* stop a run, and it is the only one of the three that runs
   automatically. Neither check replaces the policy: a job that binds the
   environment has already been let in by it, and the in-job check runs after
   that. They exist so a *misprovisioned* environment is loud instead of
   silent.
3. **Create the staging read-write role**, assumed via OIDC (no static keys),
   with two halves and no third: **read + list on the production stores** (what
   the seeder reads its slice from — the same access the read-only role already
   grants) and **read + write on the staging pair alone**. Its trust names
   **only** the `staging` environment — the same `...:sub` shape the other
   roles use, `repo:<owner>/<repo>:environment:staging` — so any staging-bound
   job may ask for it and nothing on any other ref can, and production's
   writer trust is untouched. Keep
   the production half explicitly read-only: this role must be unable to write
   the production corpus by policy, not merely by the command's refusal.
4. **Set the variables on the `staging` environment** — the destinations
   `STAGING_CORPUS_REMOTE_URL` and `STAGING_CASESTORE_URL`, the pinned
   sources `PROD_CORPUS_REMOTE_URL` and `PROD_CASESTORE_URL` (the production
   pair, by value — the refresh lane reads its slice from these and its rail
   compares destinations against them, so they are dedicated names step 5
   never touches), and the role
   `AWS_ROLE_TO_ASSUME_STAGING_RW` (`AWS_REGION` and the scenario variables
   `CORPUS_REMOTE_URL` / `CASESTORE_URL` are already there at their production
   values for the integration runs; the seeder deliberately reads neither).
   Values stay out of git, as the production ones do. The source pins live on
   the environment rather than the repository because environment values are
   the one slot nothing can shadow — and they join any store-rotation
   checklist: a rotation that moves the production pair must move these two
   with it, or the lane seeds from whatever the old bucket still resolves to
   — the census's source-blob line (step 6) is where that staleness shows.
   Type them carefully: the pin is also what the rail refuses to write to,
   so a mis-set pin re-bases the local check with it — IAM, read-only on
   production, is what keeps a typo harmless rather than the rail.
5. **Point the `staging` environment at the staging corpus.** Set its
   `CORPUS_REMOTE_URL` and `CASESTORE_URL` to the staging pair,
   `FEDCOURTS_CORPUS_SPLIT=1`, and `FEDCOURTS_CORPUS_POINTER` to the pointer
   JSON the seed's apply run published — the block its step summary prints
   (step 6), copied verbatim. The first three name the pair's two stores and
   its read mode; the fourth is what makes the *index* half resolvable. A
   consumer otherwise resolves the committed `corpus/corpus.db.ref`, whose
   digest names the production blob, and content addressing means a lean
   slice can never publish under that digest. With all four set, the
   integration scenarios dispatched from `staging` run split-on against the
   staging corpus rather than production's.

   **Set all four on the `staging` environment only** — never repository- or
   organization-wide. `vars` resolves environment first and falls back to the
   repository and organization, and the scenario job's environment is
   branch-resolved, so a repository-level pointer reaches `prod`-bound
   dispatches too. Most such mistakes are loud (a staging digest against the
   production bucket is a missing key), but one is silent: a pointer naming a
   *stale production* digest resolves cleanly, because the remote is add-only
   and still holds it — every production scenario would then certify the
   seams against an old corpus and pass.

   **The refresh lane never receives the pointer, and the command enforces
   it.** Its source is production's index, which is exactly what the
   committed pointer names, so `staging-corpus-refresh` forwards no pointer
   and `corpus-seed-slice` refuses to run while the pointer override is set
   anywhere in its environment. An override asks the index read for another
   blob than the pin's committed pointer — against the pinned production
   remote a staging pointer is a missing key, not a mis-read — and a command
   whose correctness depends on which blob it saw does not run under one;
   the refusal names the cause where the missing key would not.

   **Order this after the override is live on the ref the scenarios run
   from.** An environment carrying the pointer variable while the running
   code ignores it has repointed the store URLs without repointing the
   pointer — exactly the failing state the variable exists to prevent. A
   dispatch runs the dispatched ref's own code, and only `staging`-ref
   dispatches bind this environment, so the condition is that `staging`
   carries the override — not that it has been promoted. (Requiring a
   promotion would invert the order the gate itself depends on: staging
   integration runs are the freshness evidence a promotion is granted on.)
   Confirm rather than assume:

   ```bash
   git fetch origin staging
   git grep -q corpus_pointer origin/staging -- src/fedcourtsai/config.py \
     && echo "override live on staging"
   ```

   The reverse order is safe: the override is inert until a variable sets it,
   so the code may land arbitrarily far ahead of this step.

   **Re-set the pointer variable after every re-seed.** The published digest
   changes with the slice's contents, and a stale pointer names a blob the
   remote still holds (the remote is add-only), so the scenarios would go on
   reading the *previous* slice — green, and wrong. The apply run's summary
   prints the value to copy — the JSON object inside the fenced block, not
   the fence. It is pretty-printed: paste it whole, newlines included.
   Nothing interpolates it into a shell — it travels as an environment
   mapping and as a composite input — so its shape is inert, and a compacted
   single line resolves identically if that is easier to handle.

   **The developer shell needs the same re-set.** Its half of the pointer is
   a user-scoped Codespaces secret rather than an environment variable
   ([data-pipeline.md](data-pipeline.md)'s *Developer access*), and it goes
   stale on a re-seed for the identical reason — reading the previous slice,
   green and wrong.

   Two further consequences to accept deliberately: the production
   **read-only** role that the `staging` environment binds must be able
   to read and list the staging pair (the read-side extension below, which may
   land at any time and is already absorbed if it landed early), and a
   staging-head preflight from then on certifies
   the seams against a real but *small* corpus — real shapes, not production's
   volume.
6. **Accept it.** The first half is runnable as soon as steps 1-4 are done; the
   second waits on step 5.

   *Runnable today.* Dispatch the refresh **from the `staging` ref** — the
   environment accepts no other, so a dispatch from `main` is refused at its
   deployment-branch gate before any step runs:

   ```bash
   gh workflow run staging-corpus-refresh.yml --ref staging \
     -f dockets="$(printf 'scotus/74112233\nscotus/74112234\n')"
   # read the census off the run summary, then:
   gh workflow run staging-corpus-refresh.yml --ref staging \
     -f dockets="$(printf 'scotus/74112233\nscotus/74112234\n')" -f apply=true
   ```

   **The observable is the apply run's step summary**: a per-case census (rows,
   events, snapshots, documents, objects, and the source index blob's
   resolved key and size — the pin's value at this run, which is where a
   stale source pin shows) plus the published-pointer JSON
   block. Both present, with the case counts you asked for, is the acceptance
   available today — it proves the role, the environment, the variables, and
   both destination stores are provisioned and writable.

   *After step 5.* Then:

   ```bash
   # substitute a docket from the seeded slice
   gh workflow run integration-test.yml --ref staging -f scenario=stub-cascade \
     -f court=scotus -f docket=74112233
   ```

   **Name a slice member explicitly.** The scenario's default case is a
   production docket, and the slice is a lean cut that does not hold it — a
   defaulted dispatch fails as a missing case, which reads as a regression
   and is not one. The case must also meet the scenario's own input contract:
   an open event, a snapshot in the content store, and — for the provisioning
   guard — a genuinely undisposed posture. The apply run's per-case census
   lists the slice's cases with their row/event/snapshot/document counts, so
   it narrows the field to cases carrying events and snapshots; whether one
   is *open* and *undisposed* is a `fedcourts query` against the pair.

   Green there is the full acceptance — provision → predict → validate over a
   real, split-on corpus that no production credential was involved in writing.

**One read-side extension sits outside the lane's ordering**: extend the
**read-only** role's policy — the role Codespaces assumes and the integration
scenarios bind — with the same read + list statements on the staging pair,
mirrored from its production statements (where the explicit write/delete deny
names resources, the staging pair joins that list too). The refresh lane does
not need it; two consumers do. It serves the maintainer's developer reads of
the pair from Codespaces ([data-pipeline.md](data-pipeline.md)'s *Developer
access*; the contributor IAM user is deliberately not extended, so the
system's one static credential stays scoped to production), and step 5
requires it for the repointed scenarios — landing it early turns a step-5
prerequisite into a done item. It stays inside step 1's "no wider read
principal than production's": the widening lands on production's existing
reader principal, not a new one. And no trust statement changes, only the
permission policy — Codespaces reaches the role by STS from the Identity
Center profile, and the CI readers bind it through the OIDC trust that
already names `prod` and `staging`.

**How a consumer resolves the staging index.** A corpus consumer resolves the
**committed** `corpus/corpus.db.ref` pointer, which carries the digest and size
of the *production* blob — content addressing means a lean slice can never
publish under the same key, so a consumer pointed at the staging remote alone
would resolve a key that bucket does not hold. The pointer is therefore
supplied **out of band**, the way the remote URL already is: an environment
variable carrying the published pointer JSON verbatim, which read paths prefer
over the committed file. `integration-test.yml` forwards it job-wide beside the
content-store URL and the split flag — and explicitly into the corpus sidecar,
whose separate process resolves its own connection — so the environment a
dispatch resolves supplies the whole pair;
`scripts/corpus-env` does the same for a developer shell
([data-pipeline.md](data-pipeline.md)'s *Developer access*). The seeder renders
the pointer it published into the apply run's summary, which is the value both
consumers take.

Three properties make this safe to prefer over a committed file. It passes the
committed pointer's exact validation, the key↔digest binding included, so it
can only ever select an already-published immutable blob and never route a
reader to bytes its checksum does not vouch for. It is read-only: writers never
honor it, and `corpus-push` refuses to run while it is set, so the committed
pointer stays the sole pre-registration record and `main` carries exactly one
corpus digest. And unset — the production lane — reads as "the committed
pointer, unchanged", so the default path is untouched.
