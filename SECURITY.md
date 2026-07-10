# Security

## Principles enforced in this repo

- **Pin actions to a full commit SHA**, with the version in a trailing comment.
  `zizmor` (in `lint-actions.yml`) fails the build on unpinned actions; Dependabot
  bumps the pins.
- **Least-privilege permissions.** Every workflow sets top-level `permissions: {}`
  and grants only what each job needs.
- **No static key in the runner's process env where untrusted code runs.** The
  Codex action proxies `OPENAI_API_KEY` so the CLI never holds it; the Claude
  action handles `ANTHROPIC_API_KEY` and the Gemini action `GEMINI_API_KEY`
  similarly. The lower-sensitivity CourtListener token is passed as a scoped
  step env only where needed — with one deliberate carve-out: the cells'
  MCP-config step writes it into the runner-local, gitignored MCP
  client-config files the engines read. Exposure equals the step-env's own:
  the files are on an ephemeral runner, never committed, and the artifact
  upload is an explicit allowlist that excludes them. The accepted residual:
  the engines read that file while processing adversarial docket text, and it
  is the same token ingestion uses — a leaked or injection-abused token
  spends pull's quota and forces a rotation that touches pull.
- **Agents get a least-privilege GitHub App token, never a static one.** So a
  headless agent can post progress/questions on the triggering issue/PR, the
  `run:predict` / `run:evaluate` / `run:reconcile` agent steps receive a separate
  short-lived App installation token from `actions/create-github-app-token`, scoped
  `contents: read` + `issues` + `pull-requests: write` — **comment-only**. The
  *workflow* (a distinct `contents: write` app-token) does the commit/PR, so a
  prompt injection in docket text cannot push code with the agent's token. The
  `run:dev` agent, which commits and opens its own PR, holds
  `contents` + `pull-requests` + `workflows: write` — pipeline development includes
  the workflow files themselves, and GitHub rejects a push that edits
  `.github/workflows/` without the workflows scope. Its changes still land only
  through a reviewed PR, and the `runner` environment is restricted to `main` (see
  below), so a workflow the agent authors on its PR branch cannot reach any secret
  before the PR is merged. Issue and docket text stay untrusted input (treated as
  data, not instructions).
- **No static cloud keys — OIDC for the DVC remote.** Workflows that touch the
  private S3 bucket behind the DVC remote assume a least-privilege IAM role via
  GitHub OIDC (`aws-actions/configure-aws-credentials`, SHA-pinned;
  `permissions: id-token: write`), reading the role ARN/region from the `runner`
  environment. No long-lived AWS key reaches a workflow (the one static
  credential in the system is the contributor path's read-only key below).
  **Two roles,
  split by access:** corpus writers (`run-seed`, `run-pull` →
  `AWS_ROLE_TO_ASSUME`) get a **read-write** role; retrieval consumers
  (`run-predict`, `run-evaluate`, `run-reconcile` →
  `AWS_ROLE_TO_ASSUME_READONLY`) get a **read-only** role, so a compromised
  consumer runner cannot tamper with the corpus. The write role is **append-only**
  (get/put/list, **no delete**) and the bucket keeps **versioning** on, so no run
  can wipe corpus data. Both roles' OIDC trust is scoped to the repo's `runner`
  environment, so a PR-branch job cannot assume them. The committed `.dvc/config`
  carries no credentials and no bucket URL — it only names the default remote
  (`storage`). Each job (and each operator) defines the remote's URL out of band,
  into the gitignored `.dvc/config.local`, before any push/pull:

  ```bash
  dvc remote add --local -d storage "<bucket url from the runner env>"
  ```

  Boto3 (DVC's S3 backend) then picks up the OIDC-assumed credentials and region
  from the environment. DVC is not a runtime dependency: CI installs it where it
  is used (`uvx --from 'dvc[s3]' dvc ...`), and local work gets it from the
  optional `data` dependency group (`uv sync`, then `uv run dvc ...`). See
  [docs/data-pipeline.md](docs/data-pipeline.md).
- **One scoped exception: developer corpus access from Codespaces.** Interactive
  data discovery runs in codespaces, which sit outside the workflows' OIDC trust
  (the roles' trust policy admits only this repo's `runner` environment), so two
  developer flows serve it — both read-only, both fed by **user-scoped Codespaces
  secrets** (never repo-level, never committed, so forks and other contributors'
  codespaces see nothing). The **maintainer** authenticates through IAM Identity
  Center: short-lived SSO tokens assume the read-only corpus role, so no static
  key exists on that path. **Contributors** use a dedicated **read-only IAM
  user** — provisioned on demand, only when a contributor without Identity
  Center access actually needs corpus reads, so until then no long-lived
  credential exists anywhere in the system. Its policy grants only
  `GetObject` / `GetObjectVersion` / `ListBucket` on the corpus bucket. The
  devcontainer's post-create hook configures whichever flow's secrets are
  present (the SSO profiles in `~/.aws/config` and/or the gitignored
  `.dvc/config.local`) and prints a note and continues when none are. The
  exposure a leaked contributor key could buy is deliberately small: the corpus
  is public court data, neither principal can write or delete anything (and the
  bucket is versioned and append-only regardless), and a billing alarm bounds
  egress abuse. See the *Developer access (Codespaces)* section of
  [docs/data-pipeline.md](docs/data-pipeline.md).
- **Label triggers are maintainer-gated, two ways.** Applying a `run:*` label is
  the trust boundary for the pipeline, and two layers enforce it on a public repo —
  where an issue *form* would otherwise apply its declared labels on creation for
  any submitter. (1) No issue form auto-applies a `run:*` label — operating the
  pipeline (`pull` / `seed` / `reconcile`) is not exposed as a public form at all,
  so a maintainer applies the `run:*` label to an issue after triage. (2) Each
  issue-triggered privileged job re-checks, before it does any privileged work,
  that the triggering actor has **write access** (via the collaborators API,
  failing closed), so a label applied by anyone else is inert. This pre-flight
  check runs ahead of every privileged step in every `run:*` workflow — the
  deterministic writers (`run-pull` / `run-seed` / `run-reconcile`) and the agent
  stages (`run-predict` / `run-evaluate` / `run-dev`) alike — so a non-write
  trigger is refused before any token is minted, the S3 role is assumed, or the
  corpus is read; the agent actions re-check the actor again before spending model
  tokens. The fan-out workflows delegate the decision to the tested
  `authorize-trigger` command (so it sits just after an unprivileged checkout +
  env setup rather than literally first), while the deterministic writers keep it
  inline; either way nothing privileged runs ahead of it. The App-driven
  handoffs `run-pull` files (the `run:predict` / `run:evaluate` / `run:reconcile`
  issues, a Bot sender) are recognized and allowed — only a maintainer-installed
  App can apply a label that fires a workflow at all.
- **Branch protection and the deployment boundary.** `main` carries two rulesets.
  One requires a reviewed PR plus the `gate` check to merge; the **data App** is a
  bypass actor on it, so the deterministic `run-seed` / `run-pull` writers can push
  corpus facts straight to `main` while agent code changes go through review. The
  agent workflows authenticate as a separate **dev App** that is *not* a bypass
  actor, so "data writes direct, everything agentic via a reviewed PR" is enforced
  by identity. The second ruleset, with **no** bypass, blocks force-pushes and
  branch deletion for everyone — both Apps included — so the predictions, outcomes,
  and evaluations under `data/` cannot be rewritten or dropped. Secrets and the S3 roles live in the `runner`
  environment, whose deployment branches are restricted to `main`: only workflows
  already on `main` can read them, so a workflow authored on a PR branch (including
  one `run:dev` adds with its workflows scope) runs without `runner` secrets or the
  S3 role.
- **Prompt-injection awareness.** Issue bodies are untrusted input. The agent
  actions (`anthropics/claude-code-action`) include actor-permission checks and are
  the supported path for issue-triggered runs; matrix inputs are parsed from a
  fixed JSON block rather than free text, and agents are instructed to treat docket
  text as data, not instructions.
- **`persist-credentials: false`** on read-only checkouts.
- **Secrets are never written to `data/` or logs.** The `validate` gate and review
  on every agent PR are the backstops.

## Reporting a vulnerability

Please report security issues **privately**, not in a public issue — use
[GitHub private vulnerability reporting](https://github.com/ModelMirrorAI/fedcourtsai/security/advisories/new)
(Security → Report a vulnerability). We aim to acknowledge within a few days
and ask for a reasonable window to remediate before public disclosure. Do not 
include privileged, sealed, or otherwise sensitive court material in a report.

## Scope & disclaimers

These are experimental model predictions, not legal advice. Do not feed privileged
or sealed material into the pipeline. For data terms, redistribution, and the PII
stance, see [docs/data-sources.md](docs/data-sources.md).
