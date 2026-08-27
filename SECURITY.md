# Security

## Invariants enforced in this repo

The concrete wiring behind each invariant — the GitHub Apps, rulesets, the
`prod` environment, and the IAM roles/policies — lives in the operational
runbook, [docs/security.md](docs/security.md).

- **Pin actions to a full commit SHA**, with the version in a trailing comment.
  `zizmor` (in `lint-actions.yml`) fails the build on unpinned actions; Dependabot
  bumps the pins.
- **Pin Python dependencies to `uv.lock`, and install with `--locked`.** The
  lockfile carries a hash per artifact, so it is the supply-chain control for
  the project's own dependencies — the counterpart of the action SHAs above.
  Every job that installs them goes through
  `.github/actions/setup-python-env`, whose `uv sync --locked` refuses a lock
  that has drifted from `pyproject.toml` rather than re-resolving. Dependabot
  bumps it. The packages `uvx` resolves at run time are *not* in that lock and
  are pinned by version alone: the CourtListener MCP server named in
  `config/predictors.yaml` / `config/evaluators.yaml`, and the workflow linters.
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
  in exactly two kinds of deterministic place, whatever the caller: the
  **MCP sidecar composite's launch step**,
  whose background `fedcourts mcp-serve` process inherits it and serves the
  CourtListener MCP tools over localhost HTTP — the cells launch it, and so
  does `integration-test`'s engine-smoke **codex** leg, which exists to
  exercise that very wiring — and the collect job's
  **aggregate step**, where the secret scan (below) needs the live value to
  search the run's output for it — a step that parses agent bytes with
  jq/git/tested Python but never executes them. (Pull's ingestion holds the
  same secret under its own name; the two kinds here are the agent
  workflows'. A new caller of the composite is a new *call site*, never a new
  kind of place — the token reaches the launch step's env and stops there.) **No agent step holds it, and no file an agent can read
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
  entropy heuristic — which skips exactly one family: the collected run's own
  ledger paths (the `predictions/` / `evaluations/` layouts and the
  cell-relative `<actor>/<run id>[/<file stem>]` /
  `<evaluator>/<predictor>/<run id>` forms), named by `--run-id` with the run
  id segment compared for equality and every free segment pinned lowercase
  and capped far below the heuristic's own minimum, so the skip can hide
  nothing the heuristic would convict standalone. A hit **withholds the branch** — nothing is pushed and no
  PR opens; a redacted file/rule/line report (never the matched text) lands on
  the trigger issue and the files stay in the run's cell artifacts for
  maintainer review. The scan fails closed: if its token env is missing, the
  branch is likewise withheld, with a misconfiguration note on the trigger
  issue in place of a findings report. The same command gates one surface
  outside a run branch on its own terms: the `qp-topic-label` run's
  turn-by-turn engine transcript is scanned (`--transcript-file`) before it is
  uploaded as a run artifact, with every detector *except* the generic entropy
  heuristic — a transcript's server-generated tool and request ids are
  high-entropy by format, so that rule convicts every real file and the
  artifact could only ever publish empty. Containment of the one credential
  the scan is given there — the engine's own API key — and the
  credential-shape patterns are that surface's whole gate, which is why it
  fails closed the same way: a hit, or a scan that could not run at all,
  withholds the artifact, and with no trigger issue on a dispatch run the
  run's warning and step summary are the record. Holding that key makes the
  scan's own **import path** part of the gate, and it follows an agent that
  writes freely in the tree the editable install resolves through — so the
  scanner is built from a checkout taken *after* the agent exits and fetched
  from GitHub, into a venv inside that fresh tree, with the package cache and
  the interpreter it is built on inside that tree too, and with the levers
  that put a caller's code inside a process it starts (`PYTHONPATH`,
  `LD_PRELOAD`, an executable `core.hooksPath` in global git config) closed
  alongside. The same job's tree-pristine assertion is a
  separate control for a separate threat, a rigged measurement rather than a
  stolen key, and it gates the measure step rather than the capture: a
  tampered run keeps the transcript that is its evidence. The toolchain that
  builds the scanner is held the same way: `uv` is checked against a digest
  recorded before the agent ran, since it sits where the runner user can
  rewrite it, and PATH is pinned to the root-owned directories so `git` is the
  image's. What that isolation still trusts, named rather than implied: the
  action bundles the runner unpacks before a job's first step, which sit in a
  runner-user-writable path and are pinned by identity and not by bytes; the
  runner image's own files, behind the passwordless sudo the runner user
  holds; and anything a process the agent left behind does between steps. What
  it removes is the drop-a-file class on the scanner's **Python import path**
  and on the toolchain that builds it — the class an editable install hands
  over for free. A different surface is
  handled a layer earlier instead: the tool-call log the harness harvests from
  an engine transcript into `retrieval_log.json` records whatever a tool call
  carried, which is not the agent's choice, so
  credential-shaped runs there are **redacted at capture** — rewritten to a
  `[redacted:…]` marker and the run allowed through, rather than costing a
  whole fan-out's model spend to a withheld branch. Redaction is not a gate:
  it spares only the shapes it can name, and anything it leaves still meets
  the scan. The scan is a heuristic and the cell's
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
  least-privilege IAM role via GitHub OIDC. **Three roles, split by access:**
  corpus writers get a **read-write, append-only** role (get/put/list, **no
  delete**) and every corpus consumer a **read-only** role, so a compromised
  consumer runner cannot tamper with the data; the buckets keep **versioning**
  on, so no run can wipe corpus objects. The third is the **staging read-write**
  role — read-only on the production stores, read-write on the staging corpus
  pair alone — so the production stores keep exactly one writer whatever
  happens to it. Every role's OIDC trust is scoped to named environments of
  this repo — the production read-write role to `prod`, the read-only role to
  `prod` and `staging` (which is what lets the pre-promotion integration runs
  read the corpus), the staging read-write role to `staging` — and each of
  those environments restricts deployments to one branch, so a PR-branch job
  cannot assume any of them. Within an environment the split is provenance,
  not identity, on both sides of the promotion: any `prod`-bound job could ask
  for the production write role and any `staging`-bound job for the staging
  one, and what stops the wrong job asking is review of the code the branch
  policy admits — deliberately symmetric, so a wrongly-writing change fails
  visibly against the disposable staging pair before promotion instead of
  succeeding first in production. No
  committed file carries credentials or the bucket URL — each job (and
  operator) supplies the URL out of band as the `CORPUS_REMOTE_URL`
  environment variable, and boto3 reads its credentials from the environment.
  Per-workflow role assignments and policies:
  [docs/security.md](docs/security.md).
- **One scoped exception: developer corpus access from Codespaces.** Two
  developer flows, both read-only, both fed by **user-scoped** Codespaces
  secrets (never repo-level, never committed): the maintainer via IAM Identity
  Center's short-lived SSO tokens — the role-assumed flow, whose read-only
  role also reads the staging pair — and contributors via a dedicated
  read-only IAM user provisioned on demand, scoped to the production stores
  alone. The exposure a leaked contributor key could
  buy is deliberately small: the corpus is public court data, neither principal
  can write or delete anything, and a billing alarm bounds egress abuse. See
  *Developer access* in [docs/data-pipeline.md](docs/data-pipeline.md).
- **The codespace GitHub token reaches one repository beyond this one — a
  write grant, conditioned on a control this repo cannot enforce.** The
  devcontainer requests `contents: write` on the maintainer's dotfiles
  repository for the codespace token (an exception to that token's repo
  scope, not to the corpus rules above), so the Claude project-memory
  snapshot that repository seeds into new codespaces can be pushed back from
  the codespace that wrote it. The grant reaches only a creator who can
  already write that repository — anyone else's codespace is created without
  it — but where it is live it is ambient: every process in the codespace,
  agent sessions included, holds it, and the repository it writes has an
  installer that runs at the maintainer's next codespace creation. The grant
  is therefore conditioned on a restriction the dotfiles repository must
  carry **before any codespace authorizes the grant**: a no-bypass push
  ruleset over its executing file paths, leaving only the memory-snapshot
  directory writable with the ambient token — durability without execution.
  This repository can neither configure nor verify that ruleset; *The
  codespace token* in [docs/security.md](docs/security.md) specifies it.
  Snapshot prose follows the standing norm for committed files — no
  credential, no bucket URL.
- **Label triggers are maintainer-gated, two ways.** Applying a `run:*` label is
  the trust boundary for the pipeline. (1) No issue form auto-applies a `run:*`
  label — a maintainer applies it after triage. (2) Each issue-triggered
  privileged job re-checks, before any privileged work, that the triggering
  actor has **write access** (failing closed), so a label applied by anyone
  else is inert — nothing privileged runs ahead of that check in any `run:*`
  workflow. The App-driven handoffs `run-pull` files are recognized and allowed
  — only a maintainer-installed App can apply a label that fires a workflow at
  all.
- **Branch protection and the deployment boundary.** `main` requires a PR
  passing `gate`, `paths`, `promotion-gate`, and `main-base`; the **data App**
  is the sole bypass actor, so the deterministic writer jobs (`run-pull`,
  `run-seed`) push corpus facts
  straight to `main` while everything agentic goes through that PR — enforced
  by identity, since the agent workflows authenticate as a separate,
  non-bypass **dev App**. Both rulesets require **zero** approving reviews, so
  maintainer review is a convention `AGENTS.md` carries, not something the
  platform enforces. Code and config reach `main` only as a gated promotion
  batch from `staging`, whose own ruleset requires a PR passing `gate` and
  `paths` (sole bypass: the repository admin role, for the maintainer's
  deterministic sync push — neither App bypasses it, and the `sync-staging`
  workflow's write token reaches the branch only through a PR that satisfies
  the same checks). A ruleset with **no** bypass blocks force-pushes and branch
  deletion for everyone, so the committed *history* of the predictions,
  outcomes, and evaluations under `data/` is immutable — every forward change
  is a new, attributable commit. Forward deletions of ledger records are
  confined to two bounded channels: the maintainer-reviewed `cleanup/*` PR
  lane, and the run-seed writer lane's attribution-repair sweeps, whose CLI
  refuses to apply above a per-run blast-radius cap. Secrets and the two
  production S3 role ARNs live in the
  `prod` environment, whose deployment branches are restricted to `main`: a
  workflow authored on a PR branch runs without them. A second environment,
  `staging`, is restricted to the `staging` branch and holds the read-only role
  and its own engine keys for the pre-promotion integration runs. A third,
  `review`, holds no secret, no role, and no branch policy: its entire content
  is a required-reviewer rule, and it exists only as the audit-logged hold
  between a paid fan-out's plan and its token spend — run-predict and
  run-evaluate both bind it; one environment serves every spend hold rather
  than each minting its own. The promotion gate's
  admin-read stage verifies the rule is present, because an auto-created
  environment is unprotected and an unprotected hold releases instantly.
  Self-review is deliberately permitted: with a single maintainer the hold is
  a deliberateness gate — an explicit, audit-logged reading of the plan before
  the spend — not two-person control, and blocking the run's own actor would
  make a maintainer-labeled run unreleasable. Revisit if a second maintainer
  joins. The `staging` environment also carries the **staging read-write
  role**'s trust — the only credential in the system that can write a corpus
  store other than through the `prod` writers, read-only on production and
  read-write on the staging bucket pair alone, so production's single-writer
  discipline is unchanged and the worst a staging-bound write can corrupt is
  the re-seedable fixture the refresh lane rebuilds in one dispatch.
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
