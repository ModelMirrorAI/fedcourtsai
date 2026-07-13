# Security

## Invariants enforced in this repo

The concrete wiring behind each invariant — the GitHub Apps, rulesets, the
`runner` environment, and the IAM roles/policies — lives in the operational
runbook, [docs/security.md](docs/security.md).

- **Pin actions to a full commit SHA**, with the version in a trailing comment.
  `zizmor` (in `lint-actions.yml`) fails the build on unpinned actions; Dependabot
  bumps the pins.
- **Least-privilege permissions.** Every workflow sets top-level `permissions: {}`
  and grants only what each job needs.
- **No static key in the runner's process env where untrusted code runs.** The
  engine actions proxy or scope their model API keys so the CLIs never hold
  them. The lower-sensitivity CourtListener token is passed as a scoped step
  env only where needed — with two deliberate carve-outs: the cells' MCP-config
  step writes it into runner-local, gitignored client-config files, and the
  predict cells' Claude and Codex agent steps carry it in their step env so the
  prompt contract's REST fallback can expand it by env-var reference (Gemini's
  CLI strips custom env, so its step stays token-free and its agent is told to
  skip the fallback). Exposure equals the step-env's own: the files are on an
  ephemeral runner, never committed, and the artifact upload is an explicit
  allowlist that excludes them. The
  prompt forbids ever writing the literal value into a command line or output
  file (tool-call command lines are harvested into the committed
  `retrieval_log.json`). The accepted residual: the engines hold that env while
  processing adversarial docket text — a leaked or injection-abused token
  spends pull's quota and forces a rotation that touches pull.
- **Agents get a least-privilege GitHub App token, never a static one.** The
  Claude agent steps in `run:predict` / `run:evaluate` receive a short-lived
  App installation token scoped **comment-only** (`contents: read` + `issues` +
  `pull-requests: write`); the Codex and Gemini cells get no GitHub token at
  all — their blocked-channel is `flags.json`, surfaced by the trusted
  `collect` job. The *workflow* (a distinct `contents: write` App token) does
  the commit/PR, so a prompt injection in docket text cannot push code with the
  agent's token. Issue and docket text stay untrusted input.
- **No static cloud keys — OIDC for S3.** Workflows that touch the private S3
  stores (the corpus remote and the per-case content store) assume a
  least-privilege IAM role via GitHub OIDC. **Two roles, split by access:**
  corpus writers get a **read-write, append-only** role (get/put/list, **no
  delete**) and every corpus consumer a **read-only** role, so a compromised
  consumer runner cannot tamper with the data; the buckets keep **versioning**
  on, so no run can wipe corpus objects. Both roles' OIDC trust is scoped to
  this repo's `runner` environment, so a PR-branch job cannot assume them. No
  committed file carries credentials or the bucket URL — each job (and
  operator) supplies the URL out of band as the `CORPUS_REMOTE_URL`
  environment variable, and boto3 reads its credentials from the environment.
  Per-workflow role assignments and policies:
  [docs/security.md](docs/security.md).
- **One scoped exception: developer corpus access from Codespaces.** Two
  developer flows, both read-only, both fed by **user-scoped** Codespaces
  secrets (never repo-level, never committed): the maintainer via IAM Identity
  Center's short-lived SSO tokens, and contributors via a dedicated read-only
  IAM user provisioned on demand. The exposure a leaked contributor key could
  buy is deliberately small: the corpus is public court data, neither principal
  can write or delete anything, and a billing alarm bounds egress abuse. See
  *Developer access* in [docs/data-pipeline.md](docs/data-pipeline.md).
- **Label triggers are maintainer-gated, two ways.** Applying a `run:*` label is
  the trust boundary for the pipeline. (1) No issue form auto-applies a `run:*`
  label — a maintainer applies it after triage. (2) Each issue-triggered
  privileged job re-checks, before any privileged work, that the triggering
  actor has **write access** (failing closed), so a label applied by anyone
  else is inert — nothing privileged runs ahead of that check in any `run:*`
  workflow. The App-driven handoffs `run-pull` files are recognized and allowed
  — only a maintainer-installed App can apply a label that fires a workflow at
  all.
- **Branch protection and the deployment boundary.** `main` requires a reviewed
  PR plus the `gate` check; the **data App** is the sole bypass actor, so the
  deterministic `run-pull` writers push corpus facts straight to `main` while
  everything agentic goes through a reviewed PR — enforced by identity, since
  the agent workflows authenticate as a separate, non-bypass **dev App**. A
  second ruleset with **no** bypass blocks force-pushes and branch deletion for
  everyone, so the predictions, outcomes, and evaluations under `data/` cannot
  be rewritten or dropped. Secrets and the S3 roles live in the `runner`
  environment, whose deployment branches are restricted to `main`: a workflow
  authored on a PR branch runs without them.
- **Prompt-injection awareness.** Issue bodies are untrusted input. The agent
  actions include actor-permission checks; matrix inputs are parsed from a
  fixed JSON block rather than free text, and agents are instructed to treat
  docket text as data, not instructions.
- **`persist-credentials: false`** on read-only checkouts.
- **Secrets are never written to `data/` or logs.** The `validate` gate and
  review on every agent PR are the backstops.

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
