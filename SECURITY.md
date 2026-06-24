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
  environment. No long-lived AWS keys exist, and `.dvc/config` carries no
  credentials. See [docs/data-pipeline.md](docs/data-pipeline.md).

## DVC remote setup

The packed historical [corpus](corpus/README.md) and the
[metrics](metrics/README.md) are versioned with DVC. The committed `.dvc/config`
holds only the remote **URL** — never a key, token, or session credential:

```ini
['remote "storage"']
    url = s3://fedcourtsai-dvc/store
```

- **Bucket** — a *private* S3 (or S3-compatible) bucket the maintainer provisions
  out of band (issue #17), distinct from the *public* CourtListener bulk-data
  bucket that `seed` reads from. Point the remote at it with
  `dvc remote modify storage url s3://<bucket>/<prefix>` if the default name
  changes; commit the result.
- **Credentials** — supplied only at runtime by `aws-actions/configure-aws-credentials`
  (GitHub OIDC → a least-privilege IAM role). Locally, use a normal AWS profile
  (`AWS_PROFILE` / `aws sso login`); DVC reads it via `s3fs`/boto. Never run
  `dvc remote modify --local storage access_key_id …` against the committed config.
- **Access mirrors role** — `run-seed`/`run-pull` get read-write (corpus writers,
  `dvc push`); `run-predict`/`run-evaluate` get read-only (`dvc pull`); the `ci`
  gate gets none and stays offline. The split is enforced by the IAM role's
  policy (a single role today). The `dvc[s3]` toolchain is an opt-in extra
  (`uv sync --extra dvc`) so the offline gate never installs it.
- **Telemetry off** — `core.analytics = false` in `.dvc/config` disables DVC's
  anonymous usage reporting.
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
