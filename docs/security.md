# Security setup (operational runbook)

The concrete configuration behind the principles in [SECURITY.md](../SECURITY.md):
the GitHub App, branch protection, the `runner` environment, and the S3 roles.
SECURITY.md says *what* the invariants are; this says *how* they are wired, so a
maintainer can reproduce or audit the setup. For the data-side access table see
[data-pipeline.md](data-pipeline.md).

## The GitHub App

Cross-workflow handoffs and PRs are made with a **GitHub App installation token**
(`actions/create-github-app-token`), never the default `GITHUB_TOKEN`: events
created with `GITHUB_TOKEN` do not trigger other workflows (GitHub's
loop-prevention), so a `run-pull` issue would never start `run-predict`, and an
agent PR would never start CI. The App's client id lives in the `APP_CLIENT_ID`
variable and its private key in the `APP_PRIVATE_KEY` secret, both on the `runner`
environment.

Each workflow mints a token scoped to only what it needs:

| Workflow | Token scope | Notes |
|----------|-------------|-------|
| `run-seed`, `run-pull` | contents, issues, pull-requests | commit facts to `main`; open handoff issues |
| `run-predict`, `run-evaluate`, `run-reconcile` | workflow token: contents, pull-requests · agent token: contents read + issues + pull-requests | the **agent** token is comment-only; the workflow commits |
| `run-dev` | contents, pull-requests, **workflows** | develops the pipeline, including the workflow files |

**Repository permissions the App must grant** (App settings → Permissions):
Contents, Issues, Pull requests, and **Workflows**, all *read and write*. After
changing an App permission, **re-approve the installation** on the repo — a new
permission stays pending until an owner accepts it, and the minted token is capped
at the granted set until then.

The App is also a **bypass actor** on the require-PR ruleset below.

## Branch protection — two rulesets on `main`

Split into two so the per-rule bypass is correct (a ruleset's bypass list applies
to the whole ruleset):

- **`main: require PR`** — requires a pull request plus the `gate` status check to
  merge. **Bypass: the GitHub App**, so the deterministic `run-seed` / `run-pull`
  writers push corpus facts (the corpus blob — rows and point-in-time snapshots —
  to the DVC remote; its pointer and deterministic `outcome.json` to `main`)
  while all agent code changes go through a reviewed PR. Required approvals are
  `0` (a maintainer reviews at merge time); set
  to `1` if a second reviewer exists.
  - Only `gate` is a required check. **Not** `zizmor` — it is path-filtered to
    `.github/**`, so requiring it would hang any PR that does not touch workflows.
- **`main: protect history`** — blocks force-pushes and branch deletion. **No
  bypass — not even the App.** This is what guarantees the predictions, outcomes,
  and evaluations under `data/` cannot be rewritten or dropped, even by a
  misbehaving agent that holds the bypass token.

## The `runner` environment

Every secret and both S3 role ARNs live on the `runner` environment — the App
credentials, the Claude OAuth token, the Codex/OpenAI key, the CourtListener API
token, the AWS role ARNs and region, and the DVC remote URL (referenced by role,
never committed). Every job that needs any of them declares `environment: runner`.

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
- **Read-only role** (`AWS_ROLE_TO_ASSUME_READONLY`, used by `run-predict` /
  `run-evaluate` / `run-reconcile`) — `GetObject` / `ListBucket` only, so a
  compromised consumer runner cannot write or poison the corpus.

Both roles' OIDC trust is scoped to this repo's `runner` environment
(`...:sub` like `repo:<owner>/<repo>:environment:runner`), so only `runner`-
environment jobs can assume them.

On the bucket: **Versioning on** (recover from any accidental overwrite/delete),
a **lifecycle rule** expiring noncurrent versions after a recovery window, and
**Block Public Access on**.

## Current limitations

- **One App, shared by writers and the dev agent.** Because `run-seed` / `run-pull`
  need to push to `main` directly, the App is a require-PR bypass actor — which
  means the *same* token used by `run-dev` could also push to `main` without
  review. The `protect history` ruleset still prevents force-push/deletion, and
  the append-only role still prevents corpus loss, so the blast radius is bounded.
  Splitting into two Apps — a data App with bypass and a dev App without — removes
  this gap and is the intended next step.
- **Going public.** Before the repo is public:
  - Set Actions → "require approval for outside collaborators" so fork-PR workflows
    need a maintainer's go-ahead, and confirm fork PRs (which run without secrets)
    behave as intended on the `push` and `pull_request` paths. Note this setting
    gates only fork `pull_request` runs — it does **not** gate `issues` events, so
    it is not what protects the label triggers below.
  - The `issues: labeled` triggers are the privileged path that "require approval"
    does not cover. Two layers guard them (see SECURITY.md → *Label triggers*): no
    issue form auto-applies a `run:*` label (the `pull`/`seed` triggers aren't
    public forms, and the `reconcile` form ships without one), and `run-pull` /
    `run-seed` / `run-reconcile` each verify the triggering actor has write access
    before doing anything. After flipping the repo public, confirm with a
    non-collaborator test account that a stray `run:*` label from a non-maintainer
    is refused.
