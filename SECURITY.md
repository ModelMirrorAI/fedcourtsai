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
- **No static cloud keys — OIDC for the DVC remote.** Workflows that touch the
  private S3 bucket behind the DVC remote assume a least-privilege IAM role via
  GitHub OIDC (`aws-actions/configure-aws-credentials`, SHA-pinned;
  `permissions: id-token: write`), reading the role ARN/region from the `runner`
  environment. No long-lived AWS keys exist. The committed `.dvc/config` carries
  no credentials and no bucket URL — it only names the default remote
  (`storage`). Each job (and each operator) defines the remote's URL out of band,
  into the gitignored `.dvc/config.local`, before any push/pull:

  ```bash
  dvc remote add --local -d storage "<bucket url from the runner env>"
  ```

  Boto3 (DVC's S3 backend) then picks up the OIDC-assumed credentials and region
  from the environment. DVC itself is an operational tool, installed where it is
  used (`pip install 'dvc[s3]'` / `uvx --from 'dvc[s3]' dvc ...`), not a package
  dependency. See [docs/data-pipeline.md](docs/data-pipeline.md).
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
