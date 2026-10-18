# Corpus checks for PRs

`AGENTS.md` requires an executed check behind any claim about run-time
behaviour and a stated corpus vintage behind any corpus-dependent figure. A
session that can push branches but cannot read the corpus — a cloud coding
session, say — can write the check but not run it. The `corpus-check` lane
runs it: the PR declares one command, the maintainer approves the run, the
command executes at the PR's head against the production corpus read-only,
and the result is posted back to the PR as a comment naming the commit, the
command and the corpus vintage.

One kind of request needs no approval, because it runs no PR code: a block
that asks for `main`'s code and names a read-only `fedcourts` subcommand on
the maintainer-owned auto allowlist runs at `main`'s own commit, with the PR
head never checked out ([below](#running-at-main-without-approval)). The
invariant the lane keeps either way: **no PR-supplied code runs with the
corpus credential without the maintainer's approval.**

The workflow is `.github/workflows/corpus-check.yml`; its decisions are
`src/fedcourtsai/corpus_check.py` and `src/fedcourtsai/environment_checks.py`,
and the requester list, the environment's approver and the auto allowlist are
`config/corpus-check.yaml`.

## Requesting a check

Put one fenced `corpus-check` block in the PR description:

````
```corpus-check
uv run python scripts/checks/corpus_vintage.py
```
````

The lane answers it when all of these hold:

- **The PR is ready for review** — a draft is passed over.
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
- **The PR's head SHA has no result yet.** Each head is answered once (an
  auto request: each head and command, below).

### Running at `main` without approval

A block may open with the line `at: main`, before its command:

````
```corpus-check
at: main
uv run fedcourts decision-census --first-term 2020
```
````

That asks for the command to run at `main`'s own commit rather than at the
PR's head. It is **auto-eligible** — answered without the maintainer's
approval — when all of these hold as well:

- the command is `uv run fedcourts <subcommand> [args…]` within the grammar
  above, never a `scripts/checks/` script;
- `<subcommand>` is on the **auto allowlist**, `auto_subcommands` in
  `config/corpus-check.yaml`: subcommands that only read the index and the
  content store, write nothing (not even the job's copy of the blob, which
  they open read-only), take no path or URL, call no model, and print counts,
  rates and identifiers to stdout — never stored snapshot or document text.
  The list today is `corpus-info`, `decision-census`, `caption-census`,
  `party-census` and `distribution-census`;
- the `corpus-check-auto` environment exists with its branch policy admitting
  `main` alone (below).

An auto-eligible request runs in the `run-auto` job: it checks out this run's
own commit of `main` — never the PR head, which is not fetched at all — and
runs the command there exactly as a held check runs a head (the same
unprivileged account, the same proofs, the same timeouts). Nothing from the
PR reaches the job but the parsed command line. So **the figure is `main`'s
code's figure, not the change's**: use it for a corpus figure that does not
depend on the PR, and leave out `at: main` when the point is to measure the
change.

Everything else waits on the approval and runs at the PR head. That includes
an `at: main` block that is not auto-eligible — an unlisted subcommand, a
script, an allowlist the plan cannot read, a `corpus-check-auto` that is
missing or not restricted to `main` — whose run summary and comment say why it
was held; approving it runs the command at the PR head, like any held request.
Any other line before the command (`at: head`, `at:main`, a second `at: main`)
is refused.

An auto request is identified by its head SHA **and** its command, and is
answered once per pair: editing the block's command asks again at the same
head, and the same command at the same head is never run twice. When an auto
request and a held one are both waiting, the auto one is answered first, since
it waits on no one.

**Every new head asks again.** A push to a PR still carrying the block is a new
head with no result, so the next poll plans it: an `at: main` request runs
again without approval, and any other holds the lane for another approval —
and while one approval waits, every other request waits behind it.
So remove the block once the check is answered, and put it back only for a head
that needs checking; to re-run an unchanged head, push a commit (an empty one
will do). A head whose comment cannot be posted — a locked conversation, say —
is planned again on every poll until the block goes or the conversation
reopens.

The lane polls every 30 minutes (`:19` and `:49`). The maintainer can also
start it at once from the Actions tab (`corpus-check`, *Run workflow* on
`main`; it takes no inputs) — the run gate admits a dispatch, or a re-run,
only from a human `config/dispatchers.json` names, never the agent account. Each run answers at most one request: the oldest open
auto request, else the oldest open held one, so several requests are answered
one per run, auto ones first, each kind in PR-creation order.

### Writing the check

The check runs as a separate, unprivileged UNIX account (below), from the root
of its own copy of the PR head, after `uv sync --locked` has installed that
head's environment under the same account. It gets:

- **the production corpus**, pulled read-only at the pointer `main` commits —
  the current production blob, not the possibly older one a branch off
  `staging` carries — copied into the account's home, with
  `FEDCOURTS_CORPUS_ROOT` naming it, so the package's corpus readers find it
  with no flag;
- **the content store reachable**: the read-only role's session and the
  corpus estate's base URL are in its environment, so payload reads under the
  corpus split work as they do in a dev checkout;
- **`CHECK_SUMMARY`**, the path of an empty file, `corpus-check-summary.md` in
  the working directory. **This file is the only thing posted.** The install's
  and the check's stdout and stderr go to a file on the runner that nobody
  sees, because the job log is public and a check's raw output can carry
  corpus content. A `fedcourts` command that takes a summary path can be
  pointed at the file by its fixed name (`--summary-out
  corpus-check-summary.md`); a script reads the variable;
- **nothing else from the job**: its environment is those variables, `HOME`
  (the account's own) and `sudo`'s default `PATH`;
- **an 8-minute install timeout and a 30-minute check timeout.** Each phase
  is stopped, with every process the account owns, and reported as timed out.

`scripts/checks/corpus_vintage.py` is the smallest example and the template:
compute the figure, append what it means to report to `CHECK_SUMMARY`, exit
non-zero if the check itself failed. Report counts and case identifiers,
never stored snapshot text — the summary is published (below).

An auto check is an allowlisted subcommand, not something written for the PR,
and those print their figure rather than writing a file: its **stdout** is the
summary, captured to a runner-owned file, while its stderr joins the unposted
output.

## What comes back

One comment on the PR from `github-actions[bot]`, whatever became of the run.
Its hidden first line names the head SHA it answers; that marker, from that
bot, is how a later run knows the head is answered. The comment carries:

- the status: `exit <n>`, `timed out`, `install failed` or `install timed out`
  (the head's `uv sync --locked` did not finish; the check did not run),
  `refused` (the block broke the rules above), or `not run` — the run job
  ended before reporting, because the approval was rejected or left to expire,
  the run was cancelled, or a setup step failed (the run's own page says
  which);
- the commit and the command, and a link to the run — for an auto run, a line
  saying it **ran at `main@<sha>`, not at the PR head**, with that commit as
  the code and the PR head named only as the request; for a held `at: main`
  request, why it was held;
- the **corpus vintage**: the pointer's `sha256` and the `freshness:` and
  `pointer:` lines `fedcourts corpus-info` printed, read by `main`'s code
  before any PR code ran — quote this beside any figure taken from the
  summary;
- the **summary** the check wrote (an auto run: the command's stdout), as
  plain text in a code block: control,
  bidirectional and zero-width characters dropped, `@`-mentions broken,
  clamped to 50,000 bytes in the run job and further if the whole comment
  would pass GitHub's 65,536-character limit (which refuses an over-long
  comment rather than truncating it). The job's credential values and the
  corpus base URL are replaced by `[redacted]` before the summary leaves the
  runner.

**A result counts only when it checks out.** Any workflow running with a token
that can comment posts as `github-actions[bot]` too, so the comment alone
proves nothing. The `post` job writes the sha256 of the exact comment body it
posted to its own run summary; a result is the lane's when its comment links a
`corpus-check` run on `main` whose `post` summary carries the sha256 of that
comment's body.

## How it runs

Four jobs under a zero top-level grant, each holding only what it names,
between the run gate's two (`src/fedcourtsai/run_gate.py`; *The run gate and
its allow-list* in [security.md](security.md)): **`authorize`** opens the
run, holding `contents: read` alone, and every job below needs it and ends its
condition with its guard. The scheduled poll passes it; a dispatch passes only
for a human on `config/dispatchers.json`, and a re-run of any job only for a
human that list names — a re-run of `run` waits on a fresh `corpus-check`
approval besides. **`run-gate`** closes the run and fails one the gate
refused.

1. **`plan`** — no environment and no credential: `contents: read`,
   `pull-requests: read` and `actions: read`. Runs only on `main`.
   - A poll whose open PRs never mention `corpus-check` stops after listing
     them, before any install.
   - It reads the `corpus-check` environment and plans **nothing** unless its
     required reviewers are exactly the configured approver — no other user,
     no team — and its branch policy admits `main` alone; the run summary
     says what is missing.
   - It reads the `corpus-check-auto` environment and its branch policies too;
     unless that environment exists admitting `main` alone, every request is
     routed to the approval.
   - It reads the requester list and the auto allowlist from its own checkout
     of `main` (never from a PR), reads the comments and head commit of the
     PRs that qualify, routes each `at: main` request auto or held, and picks
     the oldest unanswered auto request, else the oldest held request whose
     head has no result. It pins the PR, head SHA, command and route as job
     outputs.
   - It writes the run summary the approver lands on (the approval UI shows
     only a workflow name and a ref): the PR and its author, the pinned head
     SHA, the head commit's author, committer and signature state, the command
     fenced with its mentions broken, a comparison link pinned to
     `<base sha>...<head sha>` (never the PR's moving page), a reminder that
     approval runs the head's whole tree — `uv sync --locked` builds and
     installs the head's own project and lockfile, so `pyproject.toml`,
     `uv.lock` and build-hook changes deserve the same reading as the check —
     and the instruction to reject if the PR's head is no longer that SHA.
2. **`run`** — binds the **`corpus-check`** environment, so it waits for the
   maintainer's approval; holds `contents: read` and `id-token: write`.
   - As the runner's own account, running `main`'s reviewed code: it checks
     out the run's own ref (so the composites resolve from it), installs with
     every cache off, assumes the read-only role through `corpus-readonly`,
     pulls the corpus and reads its vintage. Then it checks out the pinned
     SHA beside it, with `persist-credentials: false`.
   - Before any PR code runs, it provisions the unprivileged account
     `corpuscheck`: its own group and no other, no sudo right, a home closed
     to everyone else holding its own copies of the head and the corpus, and
     `uv` on `sudo`'s default path. It denies the account `cron` and `at`
     (`/etc/cron.deny`, `/etc/at.deny`), turns off unprivileged user
     namespaces (`kernel.apparmor_restrict_unprivileged_userns=1`, which must
     take, and `kernel.unprivileged_userns_clone=0` where the kernel has it),
     rejects the account's traffic to the platform's metadata endpoints
     (`169.254.169.254` and `168.63.129.16`, both IPv4-only), and closes the
     runner's home and temp tree to other accounts. It derives the runner's
     install root from the `Runner.Worker` process, failing the step if it
     cannot.
   - It then proves the separation by attempting each of these as the account
     and failing the job if one succeeds: `sudo`, `sudo -l`, reading the
     runner step's or the worker's `/proc/<pid>/environ`, listing the runner's
     home, temp tree, workspace or install root, reading a workspace file, the
     runner's `.runner` file or the step's `GITHUB_ENV` file, writing the
     Docker socket, installing a crontab, listing `at` jobs, and creating a
     user namespace where the older switch exists; and by requiring that a
     connection to each metadata endpoint is refused, not merely slow. An
     image whose layout moves a path fails the job rather than leaving the
     path unproven.
   - It runs `fedcourts corpus-check-exec`, which re-validates the command and
     runs, as the account through `sudo -u` with no shell and only the
     variables above carried across: the head's `uv sync --locked` under its
     own timeout, then the command, split without a shell, under its own.
     Both write to the output file through the only descriptors they inherit.
     After each phase every process the account owns is killed, by effective
     and by real user id, until `pgrep` finds none; one that survives ten
     passes fails the run. The summary is read back as the account.
   - The command is taken from the plan's outputs, never re-read from the PR,
     whose head or body may have moved since the approval. Its outputs are the
     phase, the exit code, the timeout flag, the summary (base64, so no line
     in it can forge another output) and the vintage.
3. **`run-auto`** — binds the **`corpus-check-auto`** environment, which has
   no reviewer, so it starts at once; holds `contents: read` and
   `id-token: write`, and runs only for a request the plan routed auto (`run`
   runs for every other, so exactly one of the two runs).
   - Its steps are `run`'s with one difference of substance: the tree beside
     the workspace is a second checkout of this run's own commit
     (`ref: ${{ github.sha }}`), not the planned head. No step names the head
     SHA, fetches anything from the PR, or reads any plan output but the route
     and the command (`tests/test_workflow_corpus_check.py` pins all of it).
   - The account is provisioned and proven by the step `run` uses, byte for
     byte, and the command runs through the same wrapper, so an option of an
     allowlisted subcommand reaches only what that account can. The
     command's stdout goes to a runner-owned file and is the summary.
4. **`post`** — no environment, no `id-token`, no PR code (it checks out the
   run's own ref, for the renderer); `contents: read` and `pull-requests:
   write` on the job's own token. It renders the comment with `fedcourts
   corpus-check-comment`, treating every value the run job emitted as
   untrusted text, posts it, and writes the posted body's sha256 to its run
   summary. It runs whenever the plan found a request, so a rejected or
   failed run still leaves a comment and the request is not planned again;
   the plan's route picks which run job's result it reports, and for an auto
   run it names this run's own commit as the code that ran.

**One check at a time.** The workflow takes one concurrency group without
cancelling in progress. A run waiting on approval holds it, and GitHub keeps at
most one more run pending behind it, replacing that pending run whenever a
newer poll or dispatch arrives. Every run plans afresh from the PRs and their
comments when it starts, so a replaced run loses nothing, and the pending run
that does start sees the comment the previous run posted and plans the next
request rather than the same one again. While an approval waits, the run
history shows the half-hourly polls cancelling one another in the pending
slot; none of them ran anything, and `run-ops`' health report does not count
them as failures. An approval left waiting blocks every other request — auto
ones included — until it is decided or expires (GitHub's limit is 30 days);
rejecting it posts `not run` for that head and lets the queue move.

## Why it is bounded

The check is PR-head code — the whole point is to measure the change — and it
runs where the corpus can be read. What bounds it:

- **The approval.** The maintainer approves a named head SHA and command from
  a ready same-repository PR by a listed author, reading a diff pinned to that
  SHA. The lane's own trigger is a `schedule` or an input-less
  `workflow_dispatch`, both of which run `main`'s workflow file, and the
  environment's branch policy admits `main` alone, so the workflow that binds
  the environment is always the reviewed one. What runs inside it is not the
  ref's code — that is the point — so the branch policy is met on paper only;
  the reviewer is the gate. The plan job will not plan while the reviewer or
  the policy is missing, and the promotion gate refuses to promote anything
  while the environment lacks either, holds a secret, or holds a variable but
  the read-only role's three — because the read-only role's trust makes an
  unprotected `corpus-check` environment that role for any branch workflow
  that binds it.
- **The account.** The runner's own account holds passwordless sudo, and its
  processes and files hold the job's OIDC request pair (which mints a token
  for any audience), its Actions runtime token (which saves cache entries and
  uploads artifacts), its step files and its log. None of that reaches the
  check's account, which has no sudo, cannot read another account's
  `/proc/<pid>/environ`, cannot enter the runner's home, temp tree, workspace
  or install root, is in no group but its own, can schedule nothing, and
  inherits no descriptor but its output file — each proven as the account
  before PR code runs. So
  PR code cannot mint an OIDC token — for AWS or for any other exchange,
  among them the one through which the Claude GitHub App, which is installed
  on this repository, issues an installation token — cannot save a cache
  entry, upload an artifact or write the job log, and cannot write the
  runner's outputs. Unprivileged execution is what bounds those paths; the
  run job's grants alone would not.
- **The trust.** What the account does hold is the read-only role's session.
  That role reaches the production stores read-only, the content store
  included, and the staging pair, and nothing it can write. And because the
  job itself still holds `id-token: write`, the environment's trust stays
  narrow for the case the separation fails: no role but the read-only one, in
  any account or cloud, and no other OIDC exchange may accept a token whose
  subject is `environment:corpus-check` ([security.md](security.md)).
- **The cache.** No credential-holding job restores a cache: every job
  installs through `setup-python-env` with the cache off unless
  `tests/test_workflow_cache_restore.py` allows it, an allowed job is checked
  to hold nothing, and the same test refuses every other cache mechanism in
  any workflow or composite. With the runtime token out of the check's reach
  it cannot save an entry at all; the rule is what makes an entry harmless
  should one be saved anyway.

- **The unapproved path runs no PR code.** `run-auto` never checks out or
  fetches the PR head: its tree is this run's own commit of `main`, reviewed
  code, and the one thing from the PR in the job is the command line — which
  the plan accepts only within the grammar, only for a `fedcourts` subcommand
  on the maintainer-owned allowlist, and which the wrapper re-validates and
  runs with no shell. What the PR author chooses is which read-only query
  `main`'s code answers, and its arguments. So the approval is skipped
  exactly where there is no PR code for it to judge, and the invariant holds:
  no PR-supplied code runs with the corpus credential without the
  maintainer's approval. `corpus-check-auto` has no reviewer, so its `main`-only
  branch policy is what keeps any other ref's workflow from binding it; the
  plan routes nothing auto while that policy is missing, and the promotion
  gate refuses a promotion until the environment exists with it and holds no
  secret and no variable but the read-only role's three. The read-only role's
  trust names `environment:corpus-check-auto` beside `corpus-check`, under the
  same rule: no other role and no other OIDC exchange may accept it.

What stays open: **network egress** — the account can reach the internet,
the metadata endpoints apart — **the read-only session** for the rest of the
role's hour, which the check can use or send elsewhere, and **the kernel**. A
Linux account is not a sandbox: a kernel privilege escalation from
`corpuscheck` reaches root, and through root the runner's processes and their
tokens. Turning off unprivileged user namespaces narrows that surface; it does
not close it. The approval and the read-only trust are why even that case is
bounded: the code ran only because the maintainer approved that SHA, and the
most any token it could then mint reaches is the read-only role.

## What it gives up, stated

- **Confidentiality of the corpus against an approved check.** The check's
  code can read the corpus and has network egress, so an approved check could
  send the corpus elsewhere, or send the read-only session, which stays valid
  for the rest of its hour. The corpus is public court data
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
- **A listed author does not vouch for every commit.** The requester list
  names the PR's author; anyone with write can push a commit to that PR's
  branch. The run summary names the head commit's author, committer and
  signature state so the approver sees whose code it is.
- **An auto result is published unread.** No one reads an auto summary
  before it is posted, so what may be posted is decided in advance, by the
  allowlist: subcommands whose stdout is counts, rates and identifiers. A
  subcommand added there that prints stored text would publish it with no
  approval in between, which is why the allowlist is maintainer-owned and its
  test pins it exactly.
- **An auto result answers a different question.** It is `main`'s code's
  figure at the corpus vintage it names, not the PR's: it cannot show what
  the change does. The comment says so; quoting it as the change's effect is
  the reader's error to avoid.
- **The comment is as trustworthy as the approved code.** Everything after the
  vintage line was produced by the check; it could report any exit code or
  summary it likes. The comment records what the approved code reported, not
  an independent observation of it.
- **A write holder can forge, suppress or remove a result.** Any workflow
  running with a comment-capable token posts as `github-actions[bot]` too, so
  a same-repository PR whose own `pull_request` workflow grants itself that
  right could post a fake result, mark a head answered so it is never
  checked, or delete a real result. The sha256 the `post` job records in its
  own run summary is what tells the lane's results from the rest; none of
  this runs anything, and only a write holder can do it.

## Operating it

- **Provisioning** (maintainer, once), **in this order**:
  1. create the `corpus-check` environment with the maintainer
     (`config/corpus-check.yaml`'s `approver`) as its only required reviewer —
     no other user and no team,
     deployment branches restricted to `main` by a named custom policy, the
     three variables `AWS_ROLE_TO_ASSUME_READONLY`, `AWS_REGION` and
     `CORPUS_BASE_URL` set to the values `prod` holds, and no secrets;
  2. only then extend the read-only role's OIDC trust to
     `environment:corpus-check`, confirming no other role — in any account or
     cloud — and no other OIDC exchange accepts that subject, wildcards such
     as `repo:…:*` included.

  The other order leaves a window in which the trust names an environment any
  write holder's branch workflow can create unprotected by binding it.
  [security.md](security.md) carries both steps, and the promotion gate's
  maintainer-run `contexts` stage checks the environment.
- **Provisioning the unapproved path** (maintainer, once, **before the
  promotion that carries it**: the gate's `contexts` stage fails until the
  environment is in place, and that promotion's `contexts-due` verdict marks
  it *due*), in the same order:
  1. create the `corpus-check-auto` environment with **no** required
     reviewers, deployment branches restricted to `main` by a named custom
     policy, the same three variables with the values `prod` holds, and no
     secrets;
  2. only then add `environment:corpus-check-auto` to the read-only role's
     OIDC trust, beside `environment:corpus-check`, confirming as for that
     subject that no other role or OIDC exchange accepts it.

  Until step 2, an auto run fails at its role assumption and posts `not run`;
  nothing else is affected.
- **Changing the auto allowlist** is an edit to `auto_subcommands` in
  `config/corpus-check.yaml` and to the tests that pin it — the names in
  `tests/test_corpus_check.py` and each command's full option surface in
  `tests/test_corpus_check_auto_surface.py` — all maintainer-owned, effective once
  promoted. Vet an addition against the rule in that file's comment: reads
  only, writes nothing, no path or URL option, no model, stdout of counts and
  identifiers.
- **Stopping the unapproved path at once**, with no commit: add a required
  reviewer to `corpus-check-auto`. Every auto run then waits for a click like
  a held one — the promotion gate does not object to the reviewer. Deleting
  the environment also stops it, routing every request to the approval, but
  blocks promotion until it is restored.
- **Changing who may ask, or who approves,** is an edit to
  `config/corpus-check.yaml`, which is maintainer-owned (`.github/CODEOWNERS`)
  and takes effect only once promoted to `main`, since the plan job reads it
  from there. A new approver must be made the environment's reviewer first.
- **Pausing the lane** is disabling the workflow; an approval left pending
  also holds it, one request at a time.
