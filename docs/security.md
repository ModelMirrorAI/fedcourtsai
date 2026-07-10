# Security setup (operational runbook)

The concrete configuration behind the principles in [SECURITY.md](../SECURITY.md):
the GitHub App, branch protection, the `runner` environment, and the S3 roles.
SECURITY.md says *what* the invariants are; this says *how* they are wired, so a
maintainer can reproduce or audit the setup. For the data-side access table see
[data-pipeline.md](data-pipeline.md).

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

- **data App** — used by the deterministic writers `run-seed` / `run-pull`. Its
  client id is the `DATA_APP_CLIENT_ID` variable and its private key the
  `DATA_APP_PRIVATE_KEY` secret. This App **is** a bypass actor on `main: require
  PR`, so the writers push corpus facts straight to `main`.
- **dev App** — used by `run-dev` and the agent workflows `run-predict` /
  `run-evaluate` / `run-reconcile`. Its client id is the `DEV_APP_CLIENT_ID`
  variable and its private key the `DEV_APP_PRIVATE_KEY` secret. This App is
  **not** a bypass actor, so nothing it holds can reach `main` except through a
  reviewed PR.

All four live on the `runner` environment (the two client ids as variables, the
two keys as secrets). Each workflow mints a token scoped to only what it needs:

| Workflow | App | Token scope | Notes |
|----------|-----|-------------|-------|
| `run-seed`, `run-pull` | data | contents, issues, pull-requests | commit facts to `main`; open handoff issues |
| `run-predict`, `run-evaluate`, `run-reconcile` | dev | workflow token: contents, pull-requests · agent token: contents read + issues + pull-requests | the **agent** token is comment-only; the workflow commits |
| `run-dev` | dev | contents, pull-requests, **workflows** | develops the pipeline, including the workflow files |

**Repository permissions each App must grant** (App settings → Permissions), at
the App level the union of what its workflows mint:

- **data App**: Contents, Issues, Pull requests — all *read and write*.
- **dev App**: Contents, Issues, Pull requests, and **Workflows** — all *read and
  write*.

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
  merge. **Bypass: the data App only**, so the deterministic `run-seed` /
  `run-pull` writers push corpus facts (the corpus blob — rows and point-in-time
  snapshots — to the DVC remote; its pointer and deterministic `outcome.json` to
  `main`) while all agent code changes — including anything the dev App holds —
  go through a reviewed PR. The dev App is deliberately **absent** from this
  bypass list. Required approvals are `0` (a maintainer reviews at merge time); set
  to `1` if a second reviewer exists.
  - Required checks are `gate` and `paths`. **Not** `zizmor` — it is path-filtered
    to `.github/**`, so requiring it would hang any PR that does not touch workflows.
  - `paths` is the **auto-merge path jail**. The predict/evaluate/reconcile
    collect jobs open one PR per run that auto-merges when green, opened with the
    **dev App** token — which is *absent* from this bypass list, so its auto-merge
    is bound by these required checks rather than skipping them. `paths` enforces
    that such a PR only *adds* files under `data/` (the tested `fedcourts
    assert-paths`): a change touching code, a workflow, config, or an existing
    artifact fails the check and cannot auto-merge. It is a no-op that passes on
    every non-`*/run-*` branch, so requiring it never blocks an ordinary PR. The
    same jail runs producer-side in each collect job; requiring it here enforces
    the guarantee independently of the workflow that produced the branch.
  - `cleanup-paths` is the destructive counterpart for `run-cleanup`. That sweep
    *deletes* out-of-scope predictions, so it is the one branch the append-only
    `paths` jail cannot cover; `cleanup-paths` instead requires every change on a
    `cleanup/*` branch to be a **delete** under a `data/cases/**/events/*/predictions/`
    subtree (the tested `fedcourts assert-cleanup-paths`). A `run-cleanup` PR is
    **never auto-merged** — a maintainer reviews it — so this is review-time
    defense-in-depth, also run producer-side in the sweep. No-op on other branches.
- **`main: protect history`** — blocks force-pushes and branch deletion. **No
  bypass — neither App.** This is what guarantees the predictions, outcomes,
  and evaluations under `data/` cannot be rewritten or dropped, even by a
  misbehaving writer that holds the data App's bypass token.
- **`ops-metrics: protect history`** — the same force-push and deletion block on the
  orphan `ops-metrics` branch, where `run-ops` appends its JSON snapshots. `run-ops`
  only ever does a normal append push (never a force-push), so the rule does not
  impede it; it guards the metrics history from accidental or malicious rewrite once
  the repo is public. No required PR (the job pushes directly) and no bypass needed.

## Repository merge settings

Settings → General → Pull Requests. The predict `collect` job (and, as they are
converted, evaluate/reconcile) opens one PR per run and asks GitHub to merge it
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
MCP config, by agent retrieval; unset degrades the agents to anonymous rate
limits), the AWS role ARNs and region, and the DVC remote URL (referenced by
role, never committed). Every job that needs any of them declares
`environment: runner`.

**Deployment branches are restricted to `main`.** A job can read the environment's
secrets only when it runs from `main`, so a workflow authored on a PR branch —
including one `run-dev` adds with its workflows scope — runs **without** the App
key, agent tokens, or S3 role. This is the control that makes `run-dev`'s
`workflows: write` safe: a malicious or prompt-injected workflow added in a PR
cannot exfiltrate secrets on its own PR run; the change reaches the privileged
context only after it is merged to `main`, which required review.

Every `runner` job already runs from a `main` ref for its trigger — `schedule`,
`workflow_dispatch`, `issues`, and the `run-reconcile` handoff's `push` to `main`
— so the restriction breaks nothing. (The handoff fires on the push that lands the
reconciled `outcome.json` on `main`, precisely so its ref is `main` rather than a
`pull_request` merge ref.)

## S3 / the DVC remote

Two IAM roles, assumed via GitHub OIDC (no static keys); see
[data-pipeline.md](data-pipeline.md) for the per-workflow access table.

- **Read-write role** (`AWS_ROLE_TO_ASSUME`, used by `run-seed` / `run-pull`) —
  **append-only**: `s3:GetObject` / `PutObject` / `ListBucket`, and an explicit
  `Deny` on every delete plus `DeleteBucket` / `PutBucketVersioning`. Content-
  addressed `dvc push` only ever adds objects, and no run garbage-collects the
  remote (`run-seed`'s `dvc gc --workspace` prunes only its local runner cache,
  never `--cloud`), so the writers never need delete; this means no run can wipe
  corpus data.
- **Read-only role** (`AWS_ROLE_TO_ASSUME_READONLY`, used by every corpus
  *consumer* job — `GetObject` / `ListBucket` only, so a compromised consumer
  runner cannot write or poison the corpus). Consumers reach it through two
  composites: `corpus-ranged` for the predict/evaluate/reconcile **cell** jobs
  (role + backend env only; the cell queries the blob in place, no pull) and
  `corpus-readonly` for the scan-heavy full-pull consumers (the plan jobs,
  `run-analytics`, `run-cleanup`, the metrics refresh).

Both roles' OIDC trust is scoped to this repo's `runner` environment
(`...:sub` like `repo:<owner>/<repo>:environment:runner`), so only `runner`-
environment jobs can assume them.

**Cells hold read-only credentials while processing adversarial docket text.**
A predict/evaluate/reconcile cell runs an agent over third-party snapshot text
with the read-only role's credentials in its environment — prompt injection in
a docket must be assumed. The blast radius is bounded and acceptable: the role
can only read public court data back out of the bucket and spend egress; it
cannot write or delete (append-only remote, explicit deny, versioning on), and
the cell's GitHub token cannot push code (the collect job owns git with its own
token). A billing alarm bounds the egress-spend abuse case. **Narrowing target
for the read-only role:** the cell path needs only `s3:GetObject` /
`s3:GetObjectVersion` on the DVC cache prefix (`<remote-prefix>/files/*`) — no
`ListBucket` (the ranged backend resolves keys from the committed pointer and
never lists). Splitting that narrower policy out (cells on the narrowed role,
full-pull consumers on the current one) is a maintainer-side IAM change,
recorded here as the target.

On the bucket: **Versioning on** (recover from any accidental overwrite/delete),
a **lifecycle rule** expiring noncurrent versions after a recovery window, and
**Block Public Access on**.
