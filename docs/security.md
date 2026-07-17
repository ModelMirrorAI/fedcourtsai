# Security setup (operational runbook)

The concrete configuration behind the invariants in [SECURITY.md](../SECURITY.md):
the GitHub App, branch protection, the `runner` environment, and the S3 roles.
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
lands via a reviewed PR" an *identity*-enforced invariant rather than a policy the
agent is merely instructed to follow:

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
  reviewed PR.

All four live on the `runner` environment (the two client ids as variables, the
two keys as secrets). Each workflow mints a token scoped to only what it needs:

| Workflow | App | Token scope | Notes |
|----------|-----|-------------|-------|
| `run-pull` | data | contents, issues | commit facts to `main`; open handoff issues; publish the verdict/frontier JSONs to `ops-metrics` |
| `run-seed` | data | contents (walker steps); ambient issues (guard) | commit historical facts to `main`; publish the verdict; the guard raises the `pipeline-health` issue on the ambient token |
| `run-predict`, `run-evaluate` | dev | workflow token: contents, pull-requests · agent token: contents read + issues + pull-requests | the **agent** token is comment-only; the workflow commits |
| `run-backtest` | dev | contents, pull-requests | open the reviewed back-test PR (minted after the replay ran) |
| `run-analytics` (metrics-refresh job only) | dev | contents, pull-requests | open the reviewed metrics-refresh PR; the analysis modes hold no write token |

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

## Branch protection — three rulesets

The two `main` rulesets are split so the per-rule bypass is correct (a ruleset's
bypass list applies to the whole ruleset); a third protects the `ops-metrics`
branch:

- **`main: require PR`** — requires a pull request plus the `gate` status check to
  merge. **Bypass: the data App only**, so the deterministic
  `run-pull` writer jobs push corpus facts (the corpus blob — rows and point-in-time
  snapshots — to the S3 corpus remote; its pointer and deterministic `outcome.json` to
  `main`) while all agent code changes — including anything the dev App holds —
  go through a reviewed PR. The dev App is deliberately **absent** from this
  bypass list. Required approvals are `0` (a maintainer reviews at merge time); set
  to `1` if a second reviewer exists.
  - Required checks are `gate` and `paths`. **Not** `zizmor` — it is path-filtered
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
    running on PR branches without the `runner` environment — cannot hold.
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
| **Automatically delete head branches** | **on** | A new `predict/run-<id>` branch is pushed every run; without this they accumulate. |

Merge-commit and rebase-merge are not used by the pipeline; leave them at
whatever the repo prefers. Auto-merge does **not** weaken the gate: it is a
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
same way. The capability is therefore on the lower-trust, non-bypass token, scoped
to issue comments/creation only; and the agent never touches it (the per-cell agent
token stays comment-only and writes `flags.json` locally — the trusted `collect`
job does the surfacing). So docket text the agent ingests cannot reach it, and the
worst a misbehaving `collect` run can do with it is post an issue comment.

The predict/evaluate `plan` job carries the same **ambient `GITHUB_TOKEN`
`issues: write`** for the same reason: when the scope gate empties the matrix it
closes the trigger issue (with a note) so the run doesn't orphan it, and closing an
issue triggers no workflow — so this stays on the lower-trust ambient token, never
the App token.

## The `runner` environment

Every secret and both S3 role ARNs live on the `runner` environment — the App
credentials, the Anthropic API key, the Codex/OpenAI key, the Gemini API key,
the CourtListener API token (used by pull's ingestion; by the cells' MCP
sidecar launch step, whose background `mcp-serve` process serves agent
retrieval over localhost — the cells have no REST fallback, so no agent step
carries the token and no client config file does either; unset degrades the
agents to anonymous rate limits; and by the collect jobs' secret scan, which
needs the live value to search the run's output for it), the AWS role ARNs
and region, and the corpus remote URL (referenced by role, never committed). Every job that needs any of
them declares `environment: runner`.

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

Every `runner` job already runs from a `main` ref for its trigger — `schedule`,
`workflow_dispatch`, and `issues` — so the restriction breaks nothing.

**The integration-test workflow selects its environment by input**
(`deploy-environment`, default `runner`). Today that is fail-closed twice over
for any branch dispatch: naming `runner` is refused at its deployment-branch
gate before any step runs, and naming any other environment resolves no role
variables — and the AWS roles' trust policies additionally pin the OIDC `sub`
to the `runner` environment, so an auto-created empty environment can assume
nothing. Standing up a real pre-merge environment (any-branch deployment
policy) therefore requires two deliberate steps **in this order**: add its
required-reviewer protection rule first, then widen the read-only role's trust
policy to that environment's `sub` — the reviewer rule is the gate, and
widening trust before it exists would make the gate decorative.

The workflow's engine-smoke scenario additionally reads one model-provider
secret — the selected engine's API key, chosen by expression ternary so the
other engines' keys never enter the job. Like every secret in this repo the
keys live on the `runner` environment, so the scenario fully resolves only on
a main dispatch; a branch dispatch gets an empty key and fails closed right
alongside the role variables, independent of step ordering. Standing up the
gated pre-merge environment extends to engine-smoke only if the maintainer
also places the engine keys on it as environment secrets — the
required-reviewer rule then gates model spend exactly as it gates the
read-only role. Within a run, the key rides the single cascade step's env,
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

Both roles' OIDC trust is scoped to this repo's `runner` environment
(`...:sub` like `repo:<owner>/<repo>:environment:runner`), so only `runner`-
environment jobs can assume them.

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

**The corpus-split mode constrains the read-only role's policy.**
**`FEDCOURTS_CORPUS_SPLIT=1`** (`Settings.corpus_split`) is set on the `runner`
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
