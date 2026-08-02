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

- **data App** — used by the deterministic writer `run-pull`. Its
  client id is the `DATA_APP_CLIENT_ID` variable and its private key the
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
  to merge. **Bypass: the data App only**, so the deterministic
  `run-pull` writer jobs push corpus facts (the corpus blob — rows and point-in-time
  snapshots — to the S3 corpus remote; its pointer and deterministic `outcome.json` to
  `main`) while all agent code changes — including anything the dev App holds —
  go through a PR gated on the required checks. The dev App is deliberately
  **absent** from this bypass list. Required approvals are `0` — the maintainer
  reviews at merge time by convention, not by rule; set to `1` if a second
  reviewer exists.
  - Required checks are exactly `gate`, `paths`, and `promotion-gate` (which
    reports `skipped` — satisfying the requirement — on every PR that is not
    the staging→main promotion). **`main-base` is not among them.** It is the
    merge-routing jail: it runs — and fails — only on a PR to `main` whose head
    is not a same-repo `staging` or reviewed non-feature lane, so a feature PR
    cannot ride around the promotion path by mistake. Rulesets cannot constrain
    a PR's source branch, which is why it is a check rather than a rule. It
    cannot be *required* yet: on a `pull_request` the workflow runs from the
    merge ref, and every legitimate lane into `main` is cut **from** `main` —
    the collect run branches, the cleanup sweep, the metrics-refresh and
    cert-backtest PRs — so they run `main`'s own `ci.yml`, which carries no
    `main-base` job. The context would never report, and an auto-merging
    collect PR would hang pending forever. It becomes requireable once the job
    definition promotes into `main`; until then routing rests on the promotion
    convention and the maintainer's merge. `cleanup-paths` is
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
    secret. The scan has no merge-time counterpart by design: its job is to act
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
  bypass — neither App.** This is what guarantees the predictions, outcomes,
  and evaluations under `data/` cannot be rewritten or dropped, even by a
  misbehaving writer that holds the data App's bypass token.
- **`staging: require PR`** — the pre-merge branch every feature PR targets
  requires a pull request plus the required checks that can report on a
  staging-targeted PR: `gate` and `paths`. (`main`'s third, `promotion-gate`,
  is structurally always-`skipped` here — it keys on a base of `main` — so
  requiring it would add no signal. The same is true of the `main-base` job,
  which is not a required context anywhere.) **Bypass: the repository
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
  corpus-writer path (`run-pull`, via the `publish-corpus-verdict` action) publishes
  the data-validation verdict and live-frontier snapshot for `run-ops` to present.
  Both writers only ever do a normal append push (never a force-push), so the rule
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
it can fetch its run's cell artifacts one at a time instead of as a single
fail-fast batch (a transient failure of which once discarded a whole run's
output). The grant is repo-wide read, as Actions scopes cannot be run-scoped; it
is acceptable here because `collect` runs no agent code and nothing
agent-controlled steers which API it calls.

The predict/evaluate `plan` job carries the same **ambient `GITHUB_TOKEN`
`issues: write`** for the same reason: when the scope gate empties the matrix it
closes the trigger issue (with a note) so the run doesn't orphan it, and closing an
issue triggers no workflow — so this stays on the lower-trust ambient token, never
the App token.

## The `prod` environment

Every secret and both S3 role ARNs live on the `prod` environment — the App
credentials, the Anthropic API key, the Codex/OpenAI key, the Gemini API key,
the CourtListener API token (used by pull's ingestion; by the cells' MCP
sidecar launch step, whose background `mcp-serve` process serves agent
retrieval over localhost — the cells have no REST fallback, so no agent step
carries the token and no client config file does either; unset degrades the
agents to anonymous rate limits; and by the collect jobs' secret scan, which
needs the live value to search the run's output for it), the AWS role ARNs
and region, and the corpus remote URL (referenced by role, never committed). Every job that needs any of
them declares an environment, and every job outside `integration-test` declares
`prod`.

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

**Deployment branches are restricted to `main`.** A job can read the environment's
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
at its deployment-branch gate before any step runs; one naming anything else
auto-creates an unprotected, empty environment and resolves no role variables —
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
granted an Actions scope; or the first workflow that binds `staging` on a
**non-dispatch trigger** — a `push` or `pull_request` filter naming the branch
would bind the environment on the merge itself, and agents merge their own PRs
to `staging`. No workflow filters on a staging ref today; every branch filter
names `main`.

What neither shape covers: the `staging` ruleset requires no workflow linter, so
a workflow change that reads a secret is caught by no *required* check.
`lint-actions` still runs zizmor and actionlint on any PR touching `.github/**`,
non-blockingly, and the branch policy forces such a change to become a PR diff
at all. The real control is `AGENTS.md`'s rule that `.github/workflows/**` and
`.github/actions/**` — the permission surface, composites included, since a
composite runs inside the job and reads the same secrets — wait for the
maintainer even into `staging`. Convention, not ruleset, and recorded as such.

Blast radius is bounded on **integrity**, not on confidentiality or spend:
staging's engine keys are separate and independently revocable, and its AWS role
is read-only with no write path to the corpus — but that role reads and lists
the access-gated corpus and the per-case content store. So the exposure a
workflow change at the staging head buys is corpus *read* and model *spend*,
which is why the linter gap above is worth naming rather than glossing.

The read-only role's trust names `staging`'s `sub` (the staging integration runs
assume it, so this is observed, not assumed); the write role's trust never does.
Restoring a lane for arbitrary branches, if one is ever wanted, means a
**separate** environment — its own keys, its own trust statement, and a required
reviewer, since arbitrary code is exactly what a human should see — not widening
this one. It costs one workflow change: adding the environment's name to
`deploy-environment`'s choice list, which is deliberately a closed vocabulary —
run titles render the input verbatim and feed the promotion gate's freshness
matching, so no dispatcher-controlled free text may reach a title.

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
other engines' keys never enter the job. The keys live on the `prod`
environment and, as **separate per-environment secrets**, on `staging` — a
smoke dispatched at the staging head spends against staging's own keys
(independently revocable, isolated from tournament spend), so a promotion's
freshness runs cannot touch the tournament's budget. Spend is gated the same way
the read-only role is: by who may dispatch, and from which branch. A dispatch
naming an environment without the keys gets an
empty key and fails closed right alongside the role variables, independent of
step ordering. A codex smoke additionally loosens the runner kernel's
AppArmor userns restriction (codex-action's own prerequisite for the live
cells) without dropping sudo afterwards — accepted for the same reason as in
the back-test residual below: same-user co-residency is already conceded as
a non-boundary, and this job holds only the read-only role and one engine
key. Within a run, the key rides the single cascade step's env,
alongside the corpus sidecar's step-scoped read-only AWS credentials for the
cascade's own provisioning reads; the spawned agent sees neither, because the
runner seam's scrubbed base environment strips every AWS variable and every
credential-shaped name except the engine's own auth — the same posture as a
back-test replay cell.

## S3 / the private stores

Two IAM roles, assumed via GitHub OIDC (no static keys), cover both private S3
stores — the corpus remote (the index blob under its content-addressed
`index/sha256/<digest>` keys) and the per-case content store:

- **Read-write role** (`AWS_ROLE_TO_ASSUME`, used by `run-pull`) —
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

Access mirrors each workflow's role in the pipeline:

| Workflow                                  | Role / access | Why                              |
|-------------------------------------------|---------------|----------------------------------|
| `run-pull` (pull + live jobs), `run-seed` | read-write    | corpus writers (`corpus-push` + content-store mirror) |
| `run-predict`, `run-evaluate` — plan jobs | read-only | scope gating over the named cases — ranged point lookups, no pull |
| `run-backtest`                            | read-only     | replay: full index `corpus-pull` + redacted snapshots from the content store |
| `run-predict`, `run-evaluate` — cell jobs | read-only, **step-scoped** | record provisioning + the corpus sidecar's ranged queries; the credentials ride the sidecar/provisioning steps only, never an agent step (no pull) |
| `run-analytics`                           | read-only     | scan-heavy analysis / metrics refresh (full `corpus-pull`) |
| `integration-test`                        | read-only     | infrastructure preflight scenarios (role assumed directly or via the sidecar composite; no pull) |
| `run-ops`                                 | none          | dashboard reads GitHub state only |
| `ci`                                      | none          | gate stays offline/fast          |

The split is deliberate: a plan job gates only the cases its trigger names and
a cell touches KBs of one case's data, so both read the immutable index in
place and move no full blob; only the whole-corpus scanners (`run-analytics`
and `run-backtest`) keep the full pull.

Developer access is separate from the workflow roles: the maintainer uses IAM
Identity Center SSO, and a contributor gets an on-demand IAM user scoped
read-only to the corpus bucket — the one static credential in the system.

Both roles' OIDC trust is scoped to named environments of this repo
(`...:sub` like `repo:<owner>/<repo>:environment:prod`), so only a job binding
one of those environments can assume them. The read-write role names `prod`
alone; the read-only role also names `staging`, which is what lets the
integration scenarios read the corpus from the staging branch.

**Agent shells hold no cloud credential; the residual is a localhost query
surface.** A predict/evaluate cell runs an agent over third-party snapshot
text — prompt injection in a docket must be assumed — but the read-only role's
credentials never enter an agent step's environment: the `corpus-sidecar`
composite takes them as masked step *outputs* (`output-credentials`, with the
job-env export disabled) and they appear only pre-agent — in the composite's
launch step, whose env the background `corpus-serve` process inherits, and in
the deterministic provisioning steps' step-scoped env. A guard step fails the job if any `AWS_*` credential is
visible in the job env when the agent steps begin, and this also levels the
engines: the Gemini sanitizer could never allowlist a credential, so corpus
retrieval used to be an accident of harness — now every engine queries the
same credential-free surface. What replaces the old residual: the sidecar is
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
credential. The cert back-test's replay cells hold the same line at a
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
is.) Running codex here also requires loosening the runner kernel's AppArmor
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
(it can enumerate keys for ingested-but-unpublished dockets). But it widens
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
