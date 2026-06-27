# Security

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
  environment. No long-lived AWS keys exist. **Two roles, split by access:** corpus
  writers (`run-seed`, `run-pull` → `AWS_ROLE_TO_ASSUME`) get a **read-write**
  role; retrieval consumers (`run-predict`, `run-evaluate`, `run-reconcile` →
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
  from the environment. DVC itself is an operational tool, installed where it is
  used (`pip install 'dvc[s3]'` / `uvx --from 'dvc[s3]' dvc ...`), not a package
  dependency. See [docs/data-pipeline.md](docs/data-pipeline.md).
- **Label triggers are maintainer-gated, two ways.** Applying a `run:*` label is
  the trust boundary for the pipeline, and two layers enforce it on a public repo —
  where an issue *form* would otherwise apply its declared labels on creation for
  any submitter. (1) No issue form auto-applies a `run:*` label — operating the
  pipeline (`pull` / `seed` / `reconcile`) is not exposed as a public form at all,
  so a maintainer applies the `run:*` label to an issue after triage. (2) Each
  issue-triggered privileged job re-checks, before it does anything, that
  the triggering actor has **write access** (via the collaborators API, failing
  closed), so a label applied by anyone else is inert. The App-driven reconcile
  handoff `run-pull` files (a Bot sender) is recognized and allowed — only a
  maintainer-installed App can apply a label that fires a workflow at all.
- **Branch protection and the deployment boundary.** `main` carries two rulesets.
  One requires a reviewed PR plus the `gate` check to merge; the GitHub App is a
  bypass actor on it, so the deterministic `run-seed` / `run-pull` writers can push
  corpus facts straight to `main` while agent code changes go through review. The
  second, with **no** bypass, blocks force-pushes and branch deletion for everyone
  — the App included — so the predictions, outcomes, and evaluations under `data/`
  cannot be rewritten or dropped. Secrets and the S3 roles live in the `runner`
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

## Reporting

These are experimental predictions, not legal advice. Do not feed privileged or
sealed material into the pipeline.
