# Security

## Required one-time setup

These credentials live in a GitHub **Environment** named `runner`. Every job
that uses them declares `environment: runner` (the agent jobs and `run-pull`);
the `plan`, CI, and lint jobs do not, since they use no secrets. Environment
secrets/variables are *only* visible to jobs that name the environment — a job
without `environment: runner` sees repo/org-level values only.

> Protection rules note: if you add **required reviewers** to the `runner`
> environment, every matrix predictor/evaluator job will pause for manual
> approval, which stalls the automated cascade. The intended access control is
> that only maintainers (triage/write) can apply the `run:*` labels — so prefer
> leaving `runner` without required-reviewer gating, and make sure its
> deployment-branch policy (if any) allows the default branch.

1. **GitHub App for handoffs** (because `GITHUB_TOKEN` can't trigger workflows):
   - Create a GitHub App (org or personal), grant it repo permissions:
     **Contents: read/write**, **Issues: read/write**, **Pull requests: read/write**.
   - Install it on this repo.
   - In the `runner` environment, add **variable** `APP_CLIENT_ID` = the App's
     Client ID (this is **not** secret — it is on the App's public settings page;
     use `client-id`, the `app-id` input is deprecated).
   - In the `runner` environment, add **secret** `APP_PRIVATE_KEY` = the App's
     private key.
2. **Secrets** (in the `runner` environment; the first two already exist):
   - `CLAUDE_CODE_OAUTH_TOKEN` — Claude Code auth.
   - `OPENAI_API_KEY` — Codex auth.
   - `COURTLISTENER_API_TOKEN` — CourtListener REST/MCP token (**add this**).
3. Run the **bootstrap-labels** workflow once to create the `run:*` labels.
4. Allow the App to push to `main` (branch protection bypass or no protection on
   `main` for the App) so `run-pull` can commit snapshots.

## Principles enforced in this repo

- **Pin actions to a full commit SHA**, with the version in a trailing comment.
  `zizmor` (in `lint-actions.yml`) fails the build on unpinned actions; Dependabot
  bumps the pins.
- **Least-privilege permissions.** Every workflow sets top-level `permissions: {}`
  and grants only what each job needs.
- **No static key in the runner's process env where untrusted code runs.** The
  Codex action proxies `OPENAI_API_KEY` so the CLI never holds it; the Claude
  action handles `CLAUDE_CODE_OAUTH_TOKEN` similarly. The lower-sensitivity
  CourtListener token is passed as a scoped step env only where needed.
- **Label triggers are maintainer-gated** — only users with triage/write access
  can apply labels, which is the trust boundary for `run:*`.
- **Prompt-injection awareness.** Issue bodies are untrusted input. The agent
  actions (`anthropics/claude-code-action`) include actor-permission checks and are
  the supported path for issue-triggered runs; matrix inputs are parsed from a
  fixed JSON block rather than free text, and agents are instructed to treat docket
  text as data, not instructions.
- **`persist-credentials: false`** on read-only checkouts.
- **Secrets are never written to `data/` or logs.** The `validate` gate and review
  on every agent PR are the backstops.

## Reporting

These are experimental predictions, not legal advice. Do not feed privileged or
sealed material into the pipeline.
