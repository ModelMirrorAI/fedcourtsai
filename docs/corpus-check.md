# Corpus checks for PRs

`AGENTS.md` requires an executed check behind any claim about run-time
behaviour and a stated corpus vintage behind any corpus-dependent figure. A
session that can push branches but cannot read the corpus — a cloud coding
session, say — can write the check but not run it. The `corpus-check` lane
runs it: the PR declares one command, the maintainer approves the run, the
command executes at the PR's head against the production corpus read-only,
and the result is posted back to the PR as a comment naming the commit, the
command and the corpus vintage.

The workflow is `.github/workflows/corpus-check.yml`; its decisions are
`src/fedcourtsai/corpus_check.py`, and the requester list is
`config/corpus-check.yaml`.

## Requesting a check

Put one fenced `corpus-check` block in the PR description:

````
```corpus-check
uv run python scripts/checks/corpus_vintage.py
```
````

The lane answers it when all of these hold:

- **The PR's head is in this repository.** A fork's code never runs.
- **The PR's author is on the requester list** (`config/corpus-check.yaml`:
  the agent account interactive sessions act as, `modelmirror-agent`, and the
  maintainer). A block from anyone else is passed over without a comment.
- **The block holds exactly one line in one of two forms:**
  `uv run fedcourts <subcommand> [args…]` or
  `uv run python scripts/checks/<name>.py [args…]`, `<name>` in
  `[A-Za-z0-9_-]`. Arguments are separated by spaces and drawn from
  `A-Z a-z 0-9 _ . / : = , + -` — no quotes, no `$`, no redirection, no
  separators — at most 40 of them and 400 characters in all. A listed
  author's block that breaks these rules is answered with a `refused` comment
  saying why, and nothing runs.
- **The PR's head SHA has no result yet.** Each head is answered once; a new
  push is a new head and asks again. To re-run an unchanged head, push a
  commit (an empty one will do).

The lane polls every 30 minutes (`:19` and `:49`). The maintainer can also
start it at once from the Actions tab (`corpus-check`, *Run workflow* on
`main`; it takes no inputs). Each run answers at most one request, the oldest
open one, so several requests are answered one per run in PR-creation order.

### Writing the check

The command runs from the root of the PR head's checkout, in that checkout's
own environment (`uv sync --locked` against its lockfile), with:

- **the production corpus** pulled read-only at the pointer `main` commits —
  the current production blob, not the possibly older one a branch off
  `staging` carries — and `FEDCOURTS_CORPUS_ROOT` naming it, so the
  package's corpus readers find it with no flag;
- **the content store reachable**: the read-only role's session and the
  corpus estate's base URL are in the environment, so payload reads under the
  corpus split work as they do in a dev checkout;
- **`CHECK_SUMMARY`**, the path of an empty file, `corpus-check-summary.md` in
  the working directory. **This file is the only thing posted.** The
  command's stdout and stderr go to a file on the runner that nobody sees,
  because the job log is public and a check's raw output can carry corpus
  content. A `fedcourts` command that takes a summary path can be pointed at
  the file by its fixed name (`--summary-out corpus-check-summary.md`); a
  script reads the variable.
- **a 30-minute timeout.** The check is stopped, with every process it
  started, and reported as `timed out`.

`scripts/checks/corpus_vintage.py` is the smallest example and the template:
compute the figure, append what it means to report to `CHECK_SUMMARY`, exit
non-zero if the check itself failed. Report counts and case identifiers,
never stored snapshot text — the summary is published (below).

## What comes back

One comment on the PR from `github-actions[bot]`, whatever became of the run.
Its hidden first line names the head SHA it answers; that marker, from that
bot, is how a later run knows the head is answered (the same text from anyone
else does not count). The comment carries:

- the status: `exit <n>`, `timed out`, `refused` (the block broke the rules
  above), or `not run` — the run job ended before reporting, because the
  approval was rejected or left to expire, the run was cancelled, or a setup
  step failed (the run's own page says which);
- the commit and the command, and a link to the run;
- the **corpus vintage**: the pointer's `sha256` and the `freshness:` and
  `pointer:` lines `fedcourts corpus-info` printed, read by `main`'s code
  before any PR code ran — quote this beside any figure taken from the
  summary;
- the **summary** the check wrote, as plain text in a code block: control
  characters dropped, `@`-mentions broken, clamped to 50,000 bytes in the run
  job and further if the whole comment would pass GitHub's 65,536-character
  limit (which refuses an over-long comment rather than truncating it). The
  job's credential values and the corpus base URL are replaced by
  `[redacted]` before the summary leaves the runner.

## How it runs

Three jobs under a zero top-level grant, each holding only what it names:

1. **`plan`** — no environment and no credential: `contents: read`,
   `pull-requests: read`. Runs only on `main`. It lists the open PRs, reads the
   requester list from its own checkout of `main` (never from a PR), reads the
   comments of the PRs that qualify, and picks the oldest request whose head
   has no result. It pins the PR, head SHA and command as job outputs and
   writes them to the run summary — the page the approver lands on — with the
   command fenced and its mentions broken, and links to the commit and the
   PR's changes. The approval UI itself shows only a workflow name and a ref,
   which is why the summary is the thing to read.
2. **`run`** — binds the **`corpus-check`** environment, so it waits for the
   maintainer's approval; holds `contents: read` and `id-token: write`. It
   checks out the run's own ref first, so the composites, the corpus pull and
   the vintage read are `main`'s reviewed code, then the pinned SHA beside it
   (`check/`), both with `persist-credentials: false`. It installs with every
   cache off, assumes the read-only role through `corpus-readonly`, pulls the
   corpus, reads the vintage, installs the head's environment, and runs the
   command through `fedcourts corpus-check-exec`: re-validated, split without
   a shell and executed as an argument list, with `GITHUB_STEP_SUMMARY`,
   `GITHUB_OUTPUT`, `GITHUB_ENV`, `GITHUB_PATH`, `GITHUB_STATE` and the OIDC
   request pair removed from its environment. The command is taken from the
   plan's outputs, never re-read from the PR, whose head or body may have
   moved since the approval. Its outputs are the exit code, the timeout flag,
   the summary (base64, so no line in it can forge another output) and the
   vintage.
3. **`post`** — no environment, no `id-token`, no PR code (it checks out the
   run's own ref, for the renderer); `contents: read` and `pull-requests:
   write` on the job's own token. It renders the comment with `fedcourts
   corpus-check-comment`, treating every value the run job emitted as
   untrusted text, and posts it. It runs whenever the plan found a request,
   so a rejected or failed run still leaves a comment and the head is not
   planned again.

**One check at a time.** The workflow takes one concurrency group without
cancelling in progress. A run waiting on approval holds it, and GitHub keeps at
most one more run pending behind it, replacing that pending run whenever a
newer poll or dispatch arrives. Every run plans afresh from the PRs and their
comments when it starts, so a replaced run loses nothing, and the pending run
that does start sees the comment the previous run posted and plans the next
request rather than the same one again. While an approval waits, the run
history shows the half-hourly polls cancelling one another in the pending
slot; none of them ran anything. An approval left waiting blocks every other
request until it is decided or expires (GitHub's limit is 30 days); rejecting it
posts `not run` for that head and lets the queue move.

## Why it is bounded

The check is PR-head code — the whole point is to measure the change — and it
runs where the corpus can be read. What bounds it:

- **The approval.** The maintainer approves a named head SHA and command from
  a same-repository PR by a listed author. The lane's own trigger is a
  `schedule` or an input-less `workflow_dispatch`, both of which run `main`'s
  workflow file, and the environment's branch policy admits `main` alone, so
  the workflow that binds the environment is always the reviewed one. What
  runs inside it is not the ref's code — that is the point — so the branch
  policy is met on paper only; the reviewer is the gate.
- **The trust.** The OIDC token is job-wide: the runner injects the
  token-request pair into every step of a job holding `id-token: write`, so
  the PR's code can mint a token for any role that trusts
  `environment:corpus-check`. Only the read-only role does, so the PR's code
  reaches exactly what that role reaches — the production stores read-only,
  the content store included, and the staging pair — and nothing it can
  write. The environment holds the read-only role's ARN, the region and the
  corpus base URL, and nothing else: no App key, engine key or CourtListener
  token.
- **The cache.** A job's cache scope is its run's ref, and this lane runs on
  `main`, whose entries every branch restores. PR code runs as the job's own
  user, so it can reach the runtime token and **save** cache entries,
  including under keys no job has used yet. What makes that harmless is that
  **no credential-holding job restores a cache**: every job installs through
  `setup-python-env` with the cache off unless
  `tests/test_workflow_cache_restore.py` allows it, an allowed job is checked
  to hold nothing, and the same test refuses every other cache mechanism in
  any workflow or composite (`actions/cache` in any form, a `setup-*` action's
  cache input, an action whose cache is on by default). An entry the check
  saves is therefore restored only by a job with nothing to take and no
  verdict anything trusts.
- **The token.** The job's own token holds `contents: read` and nothing else
  in the `run` job; the comment is posted from a separate job that runs no PR
  code.

Removing the step-file variables and keeping raw output off the log keeps an
honest check from leaking by accident. Neither is a boundary: the check runs as
the job's own user and can reach the runtime token, write those files by path,
or upload an artifact. From the head's install step on, everything in the `run`
job is the PR's to shape — including its outputs — which is why the `post` job
treats them as untrusted and why the vintage is read before that step.

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
- **The comment is as trustworthy as the approved code.** Everything after the
  vintage line was produced in a job the check controlled; a check could
  forge its own exit code or summary. The comment records what the approved
  code reported, not an independent observation of it.
- **The result marker can be forged by a write holder.** Any workflow running
  with a token that can comment posts as `github-actions[bot]` too, so a
  same-repository PR whose own `pull_request` workflow grants itself comment
  rights could mark a head answered. That suppresses a check; it runs
  nothing, and only a write holder can do it.

## Operating it

- **Provisioning** (maintainer, once): the `corpus-check` environment with the
  maintainer as required reviewer, deployment branches restricted to `main`,
  and the three variables `AWS_ROLE_TO_ASSUME_READONLY`, `AWS_REGION` and
  `CORPUS_BASE_URL` set to the same values `prod` holds, and no secrets; and
  the read-only role's OIDC trust extended to `environment:corpus-check`,
  confirming no write role's `sub` condition matches it (wildcards such as
  `repo:…:*` included). [security.md](security.md) carries both.
- **Changing who may ask** is an edit to `config/corpus-check.yaml`, which is
  maintainer-owned (`.github/CODEOWNERS`) and takes effect only once promoted
  to `main`, since the plan job reads it from there.
- **Pausing the lane** is disabling the workflow; an approval left pending
  also holds it, one request at a time.
