# The work cycle

Development here runs in a repeating cycle: **sweep** what has come in,
**rank** it, **fan out** one focused change per item, **promote** the batch
those changes form, and **close out** what the promotion owes. Each step has
its own session or sessions; this page says what each step reads, what it
produces, and where it hands over. The branch-and-PR rules every step follows
are in `AGENTS.md`; the promotion mechanics are *Promotion: staging → main* in
[pipeline.md](pipeline.md).

A cycle ends at a promotion, so its length is the maintainer's choice of
when to dispatch the train.

## 1. Sweep

One session reads everything that has arrived since the last sweep and writes
a triage note. Its inputs:

- **Open issues and PRs** on this repository and on the site repository
  (`ModelMirrorAI/fedcourts.ai`). List them page by page over REST
  (`gh api 'repos/<owner>/<repo>/issues?state=open&per_page=100&page=N'`);
  some session connections refuse `--paginate` and `search/issues`.
- **Agent feedback.** The `collect` job of every predict and evaluate run
  latches its `flags.json` roll-up onto the single open issue labelled
  `agent-feedback`, one comment per run, and a run with no flags posts
  nothing, so a quiet window is real. Read only what is new:
  `gh api 'repos/<owner>/<repo>/issues/<n>/comments?since=<cursor>'`, where
  the cursor is the last comment time the previous sweep's note recorded.
  Triage each flag as one of: a **bug** (file an issue with the case, run id
  and evidence), **already fixed** (compare the fix's merge into `main`, not
  `staging`, with the run time: a flag from a run before the promotion that
  carried its fix is expected), **by design** (say which doc says so), or
  **noise** (a harness check tripping on the agent's own prompt text, for
  example).
- **Pipeline health.** Issues labelled `pipeline-health`, `data-validation`
  and `merits-coverage`
  (bot-filed; never hand-label one: an alarm label means a failure filed it,
  and the writer closes only its own issue),
  failed scheduled runs, and the latest `run-ops` roll-up and `status.json`
  on `ops-metrics` (*`run-ops` — the daily operational roll-up* in
  [pipeline.md](pipeline.md)).
- **Waiting checks** whose date has passed without a result on their issue.

The **triage note** records the agent-feedback cursor the next sweep starts
from, what was filed, what was closed (each with its evidence), and the
ranked list below. It is a working note, kept outside the repository; what
must outlive it goes into issues.

## 2. Rank

The sweep ends with a ranked list of items, each one PR-sized, with its issue,
scope and the evidence that motivated it. The standing order, set by the
maintainer:

1. **Data quality and bugs**: anything that makes a cell see the wrong
   record, a writer store the wrong thing, or a figure read wrongly.
2. **Method work** on the current milestone (the topic method, a new
   moment, a scoring rule).
3. **Public surfaces**: the site, the feeds and the weekly update. High
   value, not rushed; groundwork counts.
4. Everything else (analytics expansion, observability, lower-court slices).

Leave out of the list, and say why in the note: items another live session
owns, items waiting on the maintainer or on a date, and items that cannot
merge yet. The last class is mostly **re-bless ordering**: a change that moves
a process digest or what cells see registers a new label as pending in its own
PR, and a promotion carries one label (*Pending registrations* in
[process-version.md](process-version.md)). So while `staging` already holds a
pending label, a second re-bless waits until the promotion stamping the first
has merged and synced; and one meant to miss a batch about to be cut waits
until the cut. Name, for each item, whether it
moves a digest, since the promotion step needs to know.

The maintainer reads the list and picks; nothing fans out unpicked.

## 3. Fan out

Each picked item gets its own session, started with the item's issue, scope
and evidence from the note, so that it needs nothing from the sweep session.
Each one follows `AGENTS.md`: a branch off `staging`, one focused PR, the
reviewer subagents, a self-merge into `staging` when green unless the change
touches an owned path (then ready for review, with the maintainer requested),
and a **handover note** in the PR description stating the effect check the
promotion will owe. Keep the items independent: a PR based on another PR's
branch can merge into that branch instead of `staging`, so base each one on
`staging` and resolve conflicts when they come.

In a Claude project, the coordinator starts one thread per item; a thread
cannot start another.

## 4. Promote

When the picked items have landed on `staging` (or the maintainer wants a
batch out sooner), one session prepares the promotion:

1. **Survey** `staging` over `main`: the batch (every first-parent merge
   `staging` holds that `main` lacks:
   `git log --first-parent --merges origin/main..origin/staging`), the owned paths it carries,
   `uv run fedcourts registry-gate --at origin/staging --main-ref origin/main`
   (pending registrations; a re-bless adds one label),
   `python3 -I -S scripts/cell_reach.py --base origin/main --head origin/staging`
   (whether the train will dispatch the paid `gate` or `offline-gate`),
   `uv run fedcourts contexts-due --at origin/staging --main-ref origin/main`,
   and the local gate on `staging`'s head.
2. **Write the owed list**: the batch, then the after-merge steps in order
   (record check, the admin-read `contexts` stage, the sync, a metrics refresh
   where scoring or salience moved, any dry-run and apply a batch PR asked
   for), then every handover note's effect check, sorted into *immediate*,
   *after the first refresh or round*, and *waits days*.
3. **The maintainer dispatches** the train
   (`gh workflow run promotion-prep.yml --ref main`), which cuts the
   candidate; the train dispatches the gate, marks the candidate ready and
   requests the maintainer's review; the maintainer approves; the train
   merges. The session watches the candidate and answers what goes red.

## 5. Close out

After the merge, the same session works the owed list: `uv run fedcourts
promotion-record --check-main origin/main` exits 0, the immediate effect
checks run on `main`, the sync lands, and the maintainer runs what only the
maintainer can (the `contexts` stage, writer dispatches). A check that waits
days becomes a scheduled routine on its issue (*A check that has to wait
becomes a scheduled routine* in `AGENTS.md`), and the session ends.

The next sweep starts from the cursor this cycle's note left, and from the
results those routines posted.
