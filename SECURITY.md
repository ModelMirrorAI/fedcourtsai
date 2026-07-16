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
  Claude and Codex engine *actions* proxy or scope their model API keys so those
  CLIs never hold them. The engines this repo drives directly — Gemini
  everywhere, and all three in the cert back-test — are the exception: their key
  is a scoped step env on the agent step, so the control there is the Gemini
  CLI's own sanitizer, which strips every env var it has not been asked to
  allowlist and **refuses to allowlist** any name matching
  `/TOKEN|SECRET|KEY|AUTH|CREDENTIAL|PRIVATE|CERT/i` — so a model key can never
  reach the agent's shell. That strict mode is forced by `GITHUB_SHA`, i.e. in CI
  (the residual: off-CI there is no such barrier, which is a local dev run with
  the dev's own key). The lower-sensitivity CourtListener token is passed as a scoped step env
  in exactly two deterministic places: the cells' **MCP sidecar launch step**,
  whose background `fedcourts mcp-serve` process inherits it and serves the
  CourtListener MCP tools over localhost HTTP, and the collect job's
  **aggregate step**, where the secret scan (below) needs the live value to
  search the run's output for it — a step that parses agent bytes with
  jq/git/tested Python but never executes them. (Pull's ingestion holds the
  same secret under its own name; the two places here are the agent
  workflows'.) **No agent step holds it, and no file an agent can read
  carries it:** the client configs name only the sidecar's `localhost` URL —
  the structural fix that retired the old stdio-transport residual, where the
  token sat as a literal value in a gitignored client-config file the agent's
  file tools could read. The cells have no REST fallback, so live
  CourtListener access is the MCP sidecar only (the agent calls it by tool
  name, never handling the token), and the token is never in the environment
  while an engine processes adversarial docket text.
  Residual blast radius if the token leaked despite this: it spends pull's
  quota and forces a rotation that touches pull — it is not a model key or a
  GitHub token.
  **The remaining residual is process-level, and the output channel is
  gated.** On-runner step-scoping is not hard isolation: the sidecar runs as
  the same user as the agent, so a determinedly-injected agent could still
  read a sibling process's environment — what the sidecar removes is every
  casual path (no agent env, no readable config file, no accidental log).
  And the sidecar is deliberately unauthenticated on `127.0.0.1`: anything on
  the runner can spend the token's rate limits *through* it, which equals the
  agent's designed tool access — while off-runner use of the credential now
  requires that process-environment read, a strictly higher bar than the old
  read-the-config-file path.
  Should any secret reach agent output by any means, the exfiltration
  sink is gated: agent free text (`reasoning.md`, a rationale, a flag
  message) is exactly what `validate` deliberately does not read, so before
  anything is pushed the `collect` job runs a **secret scan**
  (`fedcourts scan-diff-for-secrets`) over the run's changed files and the PR
  prose about to be posted: literal containment of the live token in the cheap
  encodings (base64, hex, URL-escaping), credential-shape patterns, and an
  entropy heuristic. A hit **withholds the branch** — nothing is pushed and no
  PR opens; a redacted file/rule/line report (never the matched text) lands on
  the trigger issue and the files stay in the run's cell artifacts for
  maintainer review. The scan fails closed: if its token env is missing, the
  branch is likewise withheld, with a misconfiguration note on the trigger
  issue in place of a findings report. The scan is a heuristic and the cell's
  uploaded artifacts remain downloadable from the Actions run by logged-in
  users regardless, so the last line stays what it always was: the *reachable*
  secret is not worth stealing — the single-account, **read-only**
  CourtListener token whose worst case is spending pull's quota and forcing a
  rotation (above), not a model key or a GitHub credential (the Claude cell's
  only token is comment-only; Codex and Gemini hold none).
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
- **Secrets are never written to `data/` or logs.** The `validate` gate, the
  collect job's secret scan (which withholds a run branch rather than push
  secret-shaped content), and review on every agent PR are the backstops.

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
