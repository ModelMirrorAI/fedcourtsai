# Corpus checks for PRs (designed, not built)

**Status:** a design awaiting the maintainer's decisions below. No workflow,
environment or role trust implements it yet; until one does, a corpus-dependent
claim on a PR is checked from a dev checkout with the read-only role
(*Developer access* in [data-pipeline.md](data-pipeline.md)).

## The problem

`AGENTS.md` requires an executed check behind any claim about run-time
behaviour and a stated corpus vintage behind any corpus-dependent figure. A
session that can push branches but cannot read the corpus — a cloud coding
session, say — can write the check but not run it, so the figure waits for a
maintainer with a codespace. A corpus check lets such a PR declare its check
and have it run, read-only, after the maintainer approves it, with the output
posted back to the PR.

## What makes it hard

The check is PR-head code — the whole point is to measure the change — and it
must run where the corpus can be read. Three existing invariants stand in the
way, each for a reason that still holds:

- **Only promoted code holds credentials.** Every privileged job binds `prod`
  or `staging`, whose branch policies admit only `main` or `staging`
  ([SECURITY.md](../SECURITY.md), *The trigger surface*). A job that checks out
  PR-head code inside one of them hands that code the environment.
- **The OIDC token is job-wide.** The runner injects the token-request pair
  into every step of a job holding `id-token: write`, after the step's own
  `env:`, so no step can be fenced off from minting a token; only a job
  boundary removes it ([security.md](security.md), on the `run-repair`
  parse split). And
  `prod`'s trust is shared: the production **write** role trusts it too. PR
  code in a `prod` job could therefore mint the write role.
- **Artifacts are public.** On this public repository any signed-in user can
  download a run artifact while it exists, so the corpus cannot cross to a
  credential-free job as an artifact.

## The design

A separate workflow, `corpus-check.yml`, because its risk class — running
PR-head code with a corpus credential — is one no existing lane has. It runs on
a **dedicated ref**, not `main`, for the reason in *The cache* below, and its
top-level `permissions` is `{}`, each job granting only what it names. Four
jobs:

1. **`plan`** — no credential, `pull-requests: read`. On each start (see
   decision 4 for how a check starts), it lists open
   **same-repository** PRs whose body carries a fenced `corpus-check` block and
   whose head SHA has no result comment yet from the workflow's own bot (a
   look-alike comment from anyone else does not count), picks the oldest, and
   pins what
   will run: the head SHA and the command, as job outputs. It renders both to
   the run summary — the page the approver lands on — refusing a command that
   is multi-line or carries non-printable characters, fencing it with a fence
   longer than any backtick run inside it, and neutralising `@`-mentions.
2. **`approval`** — the hold, in a new environment `corpus-check` with the
   maintainer as required reviewer. The approval UI shows a workflow name and a
   ref, not a diff, which is why the plan job's summary carries the SHA and
   command.
3. **`run`** — binds `corpus-check`, holds `contents: read` and `id-token:
   write` and nothing else, and takes the SHA and the command **from the plan's
   outputs** — never re-reading the PR, whose head or body may have moved since
   the approval. It checks out that SHA with `persist-credentials: false`,
   installs with every cache off (`setup-uv`'s own included, which hosted
   runners may enable by default), pulls the corpus with the read-only role,
   and runs the command under a hard timeout. The command's stdout and stderr
   go to a file, not the job log, which is public on this repository, and the
   step unsets `GITHUB_STEP_SUMMARY`, `GITHUB_OUTPUT` and `GITHUB_ENV`. That
   keeps an honest check from leaking by accident; it is not a boundary,
   since the code can still reach the runtime token and upload an artifact. The check writes
   what it means to report to a summary file it is given (`CHECK_SUMMARY`), and
   the job emits that, clamped to ~50 KB, with the exit code and `fedcourts
   corpus-info`'s vintage as job outputs. The `corpus-check` environment holds
   the read-only role's ARN and region and nothing else — no App key, engine
   key or CourtListener token — and no repository-level secret may exist,
   since every job can read those.
4. **`post`** — no checkout, no environment, no `id-token`; `pull-requests:
   write` on the job's own token only. It writes one comment on the PR naming
   the SHA, the command, the exit code, the vintage and the summary, fenced and
   clamped under GitHub's 65,536-character comment limit (which refuses rather
   than truncates).

A later push to the PR leaves the comment naming the old SHA, and the next
poll sees the new head without a result and plans it again.

### The trust

The point of the new environment is its OIDC **trust**: the read-only role's
trust names `environment:corpus-check`, and no write role's trust does. PR
code in the `run` job can mint a token for every role that trusts the
environment, so it can reach exactly what the read-only role reaches — the
production stores read-only, the content store included, and the staging pair
— and nothing it can write. This is the shape docs/security.md already names
for giving arbitrary code a corpus lane (a separate environment, its own trust
statement, a required reviewer); here the deployment-branch policy is met only
on paper, since the code that runs is not the ref's, and the approval and the
trust split are what bound it.

### The cache

The hardest part. A job's cache scope is its run's ref, and every branch
restores from the default branch's entries. PR code runs as the same user as
the job's action steps, so it can reach the runtime token and **save** cache
entries — including under keys no one has used yet, such as the next
lockfile's uv key. Run on `main`, a check could plant packages a later `prod`
writer restores while holding the write role; docs/security.md already names
this as the remaining risk for a parser, and here it is arbitrary code by
design. Two fixes, either sufficient:

- **A dedicated ref** (recommended). The lane runs only on a protected
  `corpus-check` branch kept identical to `main` (fast-forwarded with it, no
  other pushes), the environment's branch policy names that branch alone, and
  its cache entries are scoped to it, where no `main` or `staging` run
  restores them. A schedule fires only on the default branch, so on this ref
  the lane starts by dispatch. The dispatch can stand in for the approval only
  if its inputs name the PR and the expected head SHA, which `plan` checks and
  refuses on a mismatch, and only while the maintainer is the one identity that
  can dispatch (any token holding Actions write can, including any App
  later granted that scope); otherwise the environment's reviewer stays the required key.
  Whoever can push to this ref controls the workflow that binds the
  environment, so a ruleset must limit its pushes to the fast-forward from
  `main`.
- **No privileged job restores a cache.** Simpler to state, slower for every
  writer and agent lane, and it must hold for every future job too.

### The request

A fenced block in the PR description:

````
```corpus-check
uv run python scripts/checks/merits_partial_support.py
```
````

One command, run from the repository root of the PR head, after `uv sync`. It
may name a script the PR adds. The block is untrusted text: the plan job reads
it as data and passes it on as a job output, never through an expression
interpolated into a shell script.

## What it gives up, stated

- **Confidentiality of the corpus against an approved check.** The check's
  code can read the corpus and has network egress, so an approved check could
  send the corpus elsewhere. The corpus is public court data
  ([SECURITY.md](../SECURITY.md)), but its stored snapshots are kept private
  and carry details the pipeline scrubs before any agent sees them — a
  self-represented filer's contact information among them — so the exposure is
  not nil. The approval is the control: the maintainer approves a named SHA and
  command, from their own or their agents' same-repository PR.
- **Publication through the comment.** The summary is posted publicly. An
  honest check that writes a stored snapshot into it publishes what the
  pipeline scrubs elsewhere. The summary file, not raw output, is the only thing
  posted, which narrows this to what the check chose to report; reading it is
  part of the approval, and a check that must report payloads belongs in a
  codespace instead. This is a carve-out from the repository's
  no-republication posture, recorded here as one.
- **The approval is a deliberateness gate, not a review.** As with the
  `review` hold, nothing forces the diff to be read before the click.

## Decisions for the maintainer

1. **Adopt the separate `corpus-check` environment and the read-only role's
   trust change** (AWS console: add `environment:corpus-check` to the
   read-only role's OIDC trust; confirm no write role's `sub` condition
   matches `environment:corpus-check`, wildcards such as `repo:…:*`
   included).
2. **The cache fix:** the dedicated `corpus-check` ref, or no cache restores
   in privileged jobs. With the ref: who fast-forwards it and the ruleset that
   limits its pushes, and whether the dispatch (naming PR and SHA) replaces
   the reviewer — which first needs a list of who holds Actions write.
3. **Who may request.** Same-repository PRs only is the floor. Whether to also
   require a PR author on an allow-list matters once agent sessions have their
   own identity (separate from the maintainer's account).
4. **How a check starts:** a maintainer dispatch per check (natural on the
   dedicated ref), or a poll every 15–30 minutes (which needs the lane on the
   default branch for its schedule, and so the no-restore fix); and whether one
   pending check at a time is enough.
5. **Whether the declared command may be arbitrary shell** or must be
   `uv run fedcourts …` / `uv run python scripts/checks/…` only. The second
   narrows mistakes, not attacks: either way the PR's own code runs.

## What building it changes

- `tests/test_workflow_auth_gate.py`: `corpus-check` joins the
  branch-policied environments a privileged job may bind, and the
  `_is_privileged` sweep learns that the local `corpus-readonly` composite
  assumes a role (today it matches the AWS credentials action and the agent
  actions by name, not the composite that wraps the former).
- [security.md](security.md): the environment, its trust statement, and the
  App/token table row for the `post` job; [SECURITY.md](../SECURITY.md):
  the trigger-surface paragraph gains the one lane that runs PR-head code with
  a credential, and why its trust and its ref make that bounded; the cache
  rule joins the invariants.
- [pipeline.md](pipeline.md): the workflow table and the lane's operation.
