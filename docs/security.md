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
  snapshots — to the DVC remote; its pointer and deterministic `outcome.json` to
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
    the guarantee independently of the workflow that produced the branch.
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
the CourtListener API token (used by pull's ingestion and, via the cells'
MCP config and the predict agent steps' scoped env for the REST fallback, by
agent retrieval; unset degrades the agents to anonymous rate
limits), the AWS role ARNs and region, and the DVC remote URL (referenced by
role, never committed). Every job that needs any of them declares
`environment: runner`.

**Deployment branches are restricted to `main`.** A job can read the environment's
secrets only when it runs from `main`, so a workflow authored on a PR branch runs
**without** the App key, agent tokens, or S3 role: a malicious or prompt-injected
workflow added in a PR cannot exfiltrate secrets on its own PR run; the change
reaches the privileged context only after it is merged to `main`, which required
review.

Every `runner` job already runs from a `main` ref for its trigger — `schedule`,
`workflow_dispatch`, and `issues` — so the restriction breaks nothing.

## S3 / the private stores

Two IAM roles, assumed via GitHub OIDC (no static keys), cover both private S3
stores — the DVC remote (the corpus index and metrics) and the per-case content
store:

- **Read-write role** (`AWS_ROLE_TO_ASSUME`, used by `run-pull`) —
  **append-only**: it can read, list, and add objects, with an explicit
  `Deny` on every delete and on bucket-versioning changes. Content-
  addressed `dvc push` only ever adds objects, no run garbage-collects the
  remote (the historical job's `dvc gc --workspace` prunes only its local runner cache,
  never `--cloud`), and the content store's write-once objects and versioned
  manifests never need a delete; this means no run can wipe corpus data.
- **Read-only role** (`AWS_ROLE_TO_ASSUME_READONLY`, used by every corpus
  *consumer* job — read and list only, so a compromised consumer runner
  cannot write or poison the corpus). Consumers reach it through two
  composites: `corpus-ranged` for the predict/evaluate **cell** jobs
  (role + backend env only; the cell reads the content store and queries the
  index blob in place, no pull) and `corpus-readonly` for the scan-heavy
  full-pull consumers (the plan jobs, `run-analytics`, the metrics refresh).

Access mirrors each workflow's role in the pipeline:

| Workflow                                  | Role / access | Why                              |
|-------------------------------------------|---------------|----------------------------------|
| `run-pull` (all three jobs)               | read-write    | corpus writers (`dvc push` + content-store mirror) |
| `run-predict`, `run-evaluate` — plan jobs | read-only | scope gating over the whole index (full `dvc pull`) |
| `run-backtest`                            | read-only     | replay: full index `dvc pull` + redacted snapshots from the content store |
| `run-predict`, `run-evaluate` — cell jobs | read-only | record provisioning from the content store + ranged index queries (no pull) |
| `run-analytics`                           | read-only     | scan-heavy analysis / metrics refresh (full `dvc pull`) |
| `integration-corpus`                      | read-only     | ranged read-path preflight (role assumed directly, no pull) |
| `run-ops`                                 | none          | dashboard reads GitHub state only |
| `ci`                                      | none          | gate stays offline/fast          |

The split is deliberate: a cell touches KBs of one case's data, so it reads the
per-case objects and the immutable index in place and moves no full blob; the
plan jobs and `run-analytics` scan the index and keep the full pull.

Developer access is separate from the workflow roles: the maintainer uses IAM
Identity Center SSO, and a contributor gets an on-demand IAM user scoped
read-only to the corpus bucket — the one static credential in the system.

Both roles' OIDC trust is scoped to this repo's `runner` environment
(`...:sub` like `repo:<owner>/<repo>:environment:runner`), so only `runner`-
environment jobs can assume them.

**Cells hold read-only credentials while processing adversarial docket text.**
A predict/evaluate cell runs an agent over third-party snapshot text
with the read-only role's credentials in its environment — prompt injection in
a docket must be assumed. The blast radius is bounded and acceptable: the role
can only read public court data back out of the bucket and spend egress; it
cannot write or delete (append-only remote, explicit deny, versioning on), and
the cell's GitHub token cannot push code (the collect job owns git with its own
token). A billing alarm bounds the egress-spend abuse case.

**The corpus-split mode constrains the read-only role's policy.**
**`FEDCOURTS_CORPUS_SPLIT=1`** (`Settings.corpus_split`) is set on the `runner`
environment: the entire forward predict/evaluate fleet provisions from the
casestore path (it overrides the env-configured `ranged` backend; an explicit
per-command `--corpus-backend` is the only thing that still wins), and the
casestore read path *does* list (`s3:ListBucket`) — a latest-snapshot-style
read lists a case's `snapshots/` to find the newest (`provision-snapshot`, the
writer's own change detection, the signal backfill), while pure `GetObject`
reads (`materialize-event`'s event/document reads, document leaves) do not.
The read-only role must therefore retain `s3:ListBucket` on the casestore
prefix for as long as the mode is on. A `GetObject`-only narrowing of the cell
path (no `ListBucket`; the ranged backend resolves index keys from the
committed pointer and never lists) remains the recorded target for the *index*
side, but it cannot be applied to the casestore prefix unless a per-case
snapshot pointer exists so the reader can `GetObject` without listing — do not
narrow the role and rely on the split mode in the same change.

On the bucket: **Versioning on** (recover from any accidental overwrite/delete),
a **lifecycle rule** expiring noncurrent versions after a recovery window, and
**Block Public Access on**.
