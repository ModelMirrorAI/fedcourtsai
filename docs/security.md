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
  - Only `gate` is a required check. **Not** `zizmor` — it is path-filtered to
    `.github/**`, so requiring it would hang any PR that does not touch workflows.
- **`main: protect history`** — blocks force-pushes and branch deletion. **No
  bypass — neither App.** This is what guarantees the predictions, outcomes,
  and evaluations under `data/` cannot be rewritten or dropped, even by a
  misbehaving writer that holds the data App's bypass token.
- **`ops-metrics: protect history`** — the same force-push and deletion block on the
  orphan `ops-metrics` branch, where `run-ops` appends its JSON snapshots. `run-ops`
  only ever does a normal append push (never a force-push), so the rule does not
  impede it; it guards the metrics history from accidental or malicious rewrite once
  the repo is public. No required PR (the job pushes directly) and no bypass needed.

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

- **Going public.** Before the repo is public:
  - Set Actions → "require approval for outside collaborators" so fork-PR workflows
    need a maintainer's go-ahead, and confirm fork PRs (which run without secrets)
    behave as intended on the `push` and `pull_request` paths. Note this setting
    gates only fork `pull_request` runs — it does **not** gate `issues` events, so
    it is not what protects the label triggers below.

    **Static verification (2026-06-27).** A code-level audit confirmed the
    secret-gating shape ahead of the live fork test; `tests/test_workflow_fork_pr_gate.py`
    locks it in so a later edit cannot route a secret onto the fork path:
    - *No secret-bearing job is reachable on `pull_request`.* The six workflows
      that read `runner` secrets (`run-pull` / `run-seed` / `run-predict` /
      `run-evaluate` / `run-reconcile` / `run-dev`) all declare `environment: runner`
      and trigger only on `issues` / `schedule` / `workflow_dispatch` / `push` to
      `main` — never `pull_request` — so the deployment-branch restriction never
      faces a fork ref. No workflow uses `pull_request_target` (which would expose
      base secrets on a fork's head ref).
    - *The fork-PR path is secret-free.* The only workflows reachable on
      `pull_request` are `ci` (the `gate`) and `lint-actions`; neither declares an
      environment nor references the `secrets.` context, and both set
      `persist-credentials: false` on checkout, so a fork-PR run holds no App key,
      agent or CourtListener token, or S3 role, and leaves no pushable
      `GITHUB_TOKEN`.

    **Live test still outstanding.** Two pieces cannot be confirmed from code and
    remain maintainer steps: enabling the repo Actions setting itself ("require
    approval for all outside collaborators"), and the end-to-end run. Recipe: from
    the test account, fork the repo and open a PR with a trivial change; confirm the
    run requires approval, approve it as maintainer, then inspect the run and verify
    its ref and environment show no `runner` job executed and no secret-dependent
    step ran (or it failed closed — never silently used a secret). A temporary debug
    step echoing whether a **non-sensitive** env var is set may be used to prove the
    gating; never echo a secret value. Record the date and the account used here when
    done.
  - The `issues: labeled` triggers are the privileged path that "require approval"
    does not cover. Two layers guard them (see SECURITY.md → *Label triggers*): no
    issue form auto-applies a `run:*` label (operating the pipeline isn't exposed
    as a public form), and every `run:*` workflow's first step verifies the
    triggering actor has write access (failing closed) before doing anything. After
    flipping the repo public, confirm with a non-collaborator test account that a
    stray `run:*` label from a non-maintainer is refused.

    **Static verification (2026-06-27).** A code-level audit confirmed both layers
    ahead of the live test:
    - *No public form applies a `run:*` label.* The three forms under
      `.github/ISSUE_TEMPLATE/` declare only `bug` / `enhancement`; `config.yml`
      keeps blank issues on (for maintainer-filed dev/ops issues) and exposes no
      pipeline-operation form. So a public submitter cannot get a `run:*` label
      applied on creation.
    - *Every `run:*` workflow refuses a non-write actor before any privileged
      step.* The deterministic writers (`run-pull` / `run-seed` / `run-reconcile`)
      already gated on the collaborators API. The agent stages (`run-predict` /
      `run-evaluate` / `run-dev`) previously relied only on `claude-code-action`'s
      own actor check, which fires after the job has minted its App token, assumed
      the read-only S3 role, and `dvc pull`ed the corpus (and, for `run-dev`,
      minted the `workflows: write` token). They now carry the same fail-closed
      pre-flight check as the deterministic writers — in `run-predict` /
      `run-evaluate` it is the first step of the `plan` job that gates the
      privileged `predict` / `evaluate` job, and in `run-dev` it precedes the token
      mint — so a non-write trigger is refused before any token mint, S3-role
      assumption, or corpus read. The legitimate `run-pull` App handoff (a Bot
      sender) is still allowed, and `claude-code-action` re-checks the actor before
      spending model tokens as defense in depth.
    - *Visibility.* Each refusal logs `::error::<actor> lacks write access
      (permission: <level>); refusing to run.` and exits non-zero, so the Actions
      run fails loudly rather than passing silently.

    **Live test still outstanding.** The end-to-end check against a real
    non-collaborator account cannot run headless or before the repo is public, so
    it remains a maintainer step. Recipe: from a read-only test account, (1) attempt
    to add each `run:*` label via the UI and `gh api -X POST
    repos/<owner>/<repo>/issues/<n>/labels` — GitHub should reject the write
    (labeling needs triage/write); (2) as defense-in-depth, have a triage-only
    account apply a `run:*` label and confirm the workflow's first step short-
    circuits with the `lacks write access` error before any privileged step. Record
    the date and the accounts used here when done.
