# Pipeline & labels

Work is represented as GitHub issues; applying a `run:*` label triggers the
matching workflow. Where one stage hands off to the next it does so by creating
and labeling an issue — the predict channel; the evaluate stage instead derives
its own work on a schedule and needs no issue.
The label is the pipeline's trust boundary, so every label-triggered
workflow opens with the fail-closed `fedcourts authorize-trigger` gate†: a
labeler without write permission is refused before any token is minted, role
assumed, or agent run. The handoff Bot is the one non-collaborator the gate
admits, and every gate pins it to the data App's own login — so if every
`run:*` label starts refusing Bot handoffs at once, check the App's slug
against the pinned login before suspecting the gate.

| Label           | Workflow         | Trigger(s)                          | Engine(s)            |
|-----------------|------------------|-------------------------------------|----------------------|
| `run:pull`      | `run-pull`       | daily schedules (pull + live jobs), label, manual (+ dispatch-only `enrich-opinions` mode) | script (no agent)    |
| _(none)_        | `run-seed`       | daily schedules (4 dead-zone windows), manual | script (no agent)    |
| _(none)_        | `run-repair`     | manual dispatch only (one maintenance pass per dispatch, dry-run by default) | script (no agent)    |
| `run:predict`   | `run-predict`    | issue labeled (created by run-pull) | Claude Code + Codex + Gemini |
| `run:evaluate`  | `run-evaluate`   | daily schedule (15:09 UTC), manual dispatch, issue labeled | Claude Code + Codex + Gemini |
| `run:backtest`  | `run-backtest`   | issue labeled, manual dispatch (replay/engine/limit/terms params; `replay: salience-gate` runs the token-free gate replay instead of the predictors) | Claude Code + Codex + Gemini (replay) |
| _(none)_        | `run-ops`        | daily schedule (dashboard + prediction-reading digest; a Monday tick adds the weekly performance digest), manual | script (no agent)    |
| _(none)_        | `run-analytics`  | manual dispatch + weekly schedule   | script; the `qp-topic-label` mode runs one Claude Code labeler |
| _(none)_        | `integration-test` | manual dispatch + daily canary  | script; engine-smoke runs one real agent cell, engine-actions-smoke one boot probe per engine (the canary) |
| _(none)_        | `staging-corpus-refresh` | manual dispatch (dry-run by default) | script (no agent)    |
| _(none)_        | `promote`        | manual dispatch                     | script (no agent)    |
| _(none)_        | `sync-staging`   | daily schedule + manual dispatch    | script (no agent)    |

† The four label rows — `run:pull`, `run:predict`, `run:evaluate`,
`run:backtest` — are the gated ones: each runs `authorize-trigger` as its entry
job's first non-setup step, and `tests/test_workflow_auth_gate.py` locks that
shape in so an edit cannot quietly drop a guard. A workflow with no label row is
dispatch- or schedule-only, which GitHub already write-gates; `run-evaluate` is
both, and gates its label path while leaving its schedule and dispatch to the
platform gates that already cover them (a cron runs only from the default
branch, a dispatch needs repository write, and the `prod` environment admits
only `main`) — the carve-out is stated in [SECURITY.md](../SECURITY.md). The refusal
posture, and what a lookup outage means, is the *Label triggers* bullet in
[SECURITY.md](../SECURITY.md); the lookup's bounded retry is in *Authoring or
changing a workflow* below.

## `run-ops` — the daily operational roll-up

`run-ops` is not part of the issue cascade: it is a read-only daily roll-up of
operational analytics, consolidated so it reads as a summary — pipeline health
(the Actions run history, dormant workflows folded into one line), **substance**
(is the machine producing: scored cells by stratum with deltas against the
week-old snapshot when one exists — else the newest,
replay calibration vs the modern-cert deny base rate with the sample size beside
every number, per-predictor evaluation-score distributions, and live-frontier
readiness — each sub-block shown only once its feed exists), **spend & cost**
(the `usage.json` ledger + Actions minutes from run durations), **agent signals**
(the committed `flags.json` / `tooling.json` and evaluator leakage gradings,
scoped to a recent window so old, fixed flags age out of the summary — the
`agent-feedback` issue and the raw ledger still keep every flag), and **open
trigger issues** (still-open `run:*` fan-out triggers = stalled runs, oldest
first, so an orphaned issue never sits invisible) — rendered by
`fedcourts ops-report`. It surfaces the current view in one long-lived "Ops
dashboard" issue and appends each JSON snapshot to a dedicated **`ops-metrics`
branch** (an orphan time-series that never merges to `main`, so the default
branch stays clean and a prior snapshot backs the substance deltas). On the
Monday schedule tick it additionally opens the **weekly performance digest** as
its own issue (below), with the daily dashboard staying the reference view. It triggers
nothing and touches neither `main` nor the corpus. It reports the **promoted**
state: scheduled runs execute from the default branch, so the dashboard describes
the tree that is actually running rather than the one staged for the next batch —
and the lag is confined to code and config, since the substance and spend
sections read `data/` and `metrics/`, which the writers commit to `main`
directly. One reading note the dashboard now carries itself: `promote` is
level-triggered, so its failures are unsatisfied-gate reports rather than
incidents, and its success rate counts promotion attempts.

It is also the **presenter** of the published corpus-side artifacts (see *Data
validation* in [data-pipeline.md](data-pipeline.md)): the corpus-writer path
produces a correctness verdict and the live-frontier readiness snapshot where
the corpus is already pulled, and `run-ops`
renders them as the **data-health** section and the substance section's
watchlist view, escalating a failing verdict to one
long-lived issue — so the dashboard surfaces run-health, data-health, and
substance while staying a read-only presenter that never touches the corpus.

### The weekly performance digest

On the Monday tick the same job opens the **weekly performance digest** as its
own issue under the non-triggering `weekly-digest` label — one per ISO week,
which is what its `<!-- weekly-digest: YYYY-Www -->` marker makes the create
idempotent on. Its own issue rather than a comment on the standing dashboard for
the same reason the daily digest gets one: a digest is a thing to read and close,
so the open issues under the label are the unread backlog.

Four blocks, in the order a reader needs them:

- **Health questions** — the fixed interrogative bullets (replay calibration,
  forward cells scored, watchlist vs next conference, oldest stalled trigger,
  spend vs budget): numbers as questions demanding a reaction. These carry the
  dashboard's un-vintaged framing, which is why the vintage rule below is
  scoped to the two blocks that publish figures to quote.
- **Analytics state** — what the committed boards hold. An empty one names the
  condition that empties it — which cells the frozen headline ranks, and how
  many have reached it — rather than showing a bare zero, and an artifact that
  has never landed reads differently from one that landed empty. Plus the
  statpack's two headline rates — stated with each one's own denominator, and
  with the plain statement that **neither anchors a scored cell**: a forward
  cert cell is scored against its own band's strictly-prior-Term risk-set rate,
  and the pooled band rate is a fit diagnostic for the ranking constant rather
  than a scoring baseline ([salience.md](salience.md)).
- **Produced this week** — cells landed by role and stage, how many events they
  covered, and the week's measured spend, all over one window and one set of
  `usage.json` records; then the spend backstop's own (longer) window and how
  much of its ceiling the trailing period has consumed. An unenforced ceiling
  says so instead of reporting a fraction of a budget that does not exist.
- **Backtest results** — the historical replay **per court**, with each court's
  own always-deny floor beside its accuracy and the pooled row labelled as the
  mixture it is (`granted` means cert on a SCOTUS row and a motion granted on a
  court-of-appeals docket, and the pooled floor mixes an ~80% one with near-zero
  ones, so a pooled lift can be bought entirely on a docket this pipeline never
  predicts); the salience-gate replay with the scorer version that produced
  it named (a per-band figure means something only under the function that
  assigned the band, so an older version's numbers are history rather than a
  current reading), and the plain statement that **no cert back-test has landed**
  — `metrics/cert-backtest.json` is off the scheduled refresh because a
  real-engine replay spends tokens.

**In the analytics and back-test blocks, every figure carries the vintage of the
artifact it came from.** None of those artifacts is refreshed on this schedule —
a board is byte-stable and a statpack moves only when the corpus does — so a
figure without its vintage would silently claim to be this week's. The vintage
is the commit that last wrote the file, and a **shallow** checkout yields none:
in a depth-1 clone the one grafted commit matches every path, so a pathspec'd
`git log` would stamp every board with today's date — the exact misreading the
vintage exists to prevent. The renderer refuses to read a shallow history and
says the vintage is unknown; the `ops` job checks out full history so the dates
are real ones.

Only the Monday cron posts. Every run renders the digest to a file; only the
Monday step hands it to `post-weekly-digest`, so the repair for a Monday run that
failed before that step is a **re-run of that scheduled run**, not a dispatch.
The create is the job's final step, after the dashboard, the snapshot push, and
the data-validation escalation, so a degraded API costs the week's digest and
nothing else — and because the poster takes the already-rendered body rather than
re-deriving it, the report build stays read-only.

Week-over-week deltas read the `ops-metrics` orphan-branch snapshots, which is
what makes the substance section's `(+n)` figures mean anything.

### The daily prediction-reading digest

A second job opens the **prediction-reading digest**: one predicted event with
every predictor side by side — the case/event header, each cell's probability
and claims, its `predicted_reasoning.md` and `reasoning.md` inline, its flags,
and links to the committed cell paths — on its own issue under the
non-triggering `daily-digest` label. The dashboard answers whether the machine
is producing; this answers *what it said*, which nothing else surfaces for a
human to read.

The maintainer **closes the issue once read**, so the open `daily-digest` issues
are the unread backlog and no reading-state store exists. Two HTML markers in
the body's leading lines are the whole of the state, read back by the same
substring idempotency the `agent-feedback` latch uses. The **event** marker
(`<!-- daily-digest-event: <court>/<docket>/<event> -->`) says which event a
digest featured: selection takes the newest event no prior body carries, and
rotates to the least-recently-featured one on a day nothing new landed. The
**day** marker (`<!-- daily-digest-day: <YYYY-MM-DD> -->`) is what the issue
create is idempotent on, and it has to be a separate key: guarded on the event
marker, a rotated re-read would find its own past issue and post nothing,
killing the rotation on the one path it exists for. Guarded on the day, a
re-dispatch of a day already digested is a no-op and a re-read still opens
today's issue. Both tests read only those leading lines — everything below them
is text the harness did not write, and a whole-body test would let a prediction
that quoted a marker retire an event from the queue for good. As a second,
independent control the whole body below the markers has its HTML-comment
openers defused in one pass, so a quoted marker is shown as written rather than
acting as one, and a field added to the digest later cannot miss the treatment.
The lookup reads the newest 200 digest issues, so the featured window is roughly
six months; an event that scrolls out of it re-reads as never featured, which
repeats a reading rather than skipping one.

The body is bounded by construction (one event, each document capped) and then
clamped under GitHub's issue-body limit, which is refused with a 422 rather than
truncated; a truncated document links its committed file. An empty ledger writes
no body and exits 0, and so does a run whose day was already digested — the
rendered body is written last, after the post, so what the file holds is what was
published rather than what selection happened to pick.

Everything under a `##` heading in the body is agent-authored and untrusted: the
predictors' own prose, verbatim. It is presented, not vouched for, and it can
spell markdown of its own — including headings that look like the digest's.

The job runs on every trigger the workflow has, including the Monday weekly
tick: the day marker, not a schedule filter, is what makes it once a day. That
is deliberate — a `schedule` filter is fail-open on any cron it does not name,
and the workflow-level `cancel-in-progress` lets the 08:30 weekly tick cancel an
08:00 run still retrying, which a filtered-out job could not make up.

Selection, rendering, and the once-a-day issue create are all
`fedcourts daily-digest`, so the workflow step is a thin wrapper with no `gh` of
its own and the bounded retry is the tested Python seam's
(`fedcourtsai.agent_feedback`). The job is separate from the dashboard job
because permissions are per-job and its needs are narrower: `contents: read`
plus `issues: write`, the ambient `GITHUB_TOKEN`, no corpus credential, no model
call, no branch write.

## `run-analytics` — corpus analysis & derived metrics

`run-analytics` is the **corpus analysis & derived metrics** surface, also outside
the cascade: every task that reads the corpus and answers a question or refreshes a
derived artifact is a mode here (dispatch `mode` input, or the weekly schedule),
each as its own least-privilege job holding only the credentials its mode needs:

- **`corpus-stats`** (dispatch) assumes the read-only S3 role, pulls the
  corpus (`fedcourts corpus-pull`), and runs `fedcourts stats` to aggregate disposition base-rates (overall,
  filtered to one SCOTUS Term via the `term` input, or grouped by court / topic /
  judge / SCOTUS Term / disposition / originating circuit / decade era, with a
  cert-stage cut restricted to modern discretionary-cert dockets). Read-only: results go
  to the Actions step summary and run log, nothing else.
- **`census`** (dispatch) assumes the same read-only role and pull, then runs
  `fedcourts distribution-census` — two registered readings of the DISTRIBUTED
  phrase counted over the salience gate's scored segment and banded by one
  scorer, the evidence a version pinning a new parse is argued from
  ([salience.md](salience.md)). `census_baseline_parse` / `census_candidate_parse`
  name the two readings (`dist-v1` against `dist-v2` by default — dispatch
  defaults left where the activation census set them, so a bare dispatch now
  re-reads what the flip moved rather than arguing a candidate); the band
  function is deliberately **not** a dispatch input — the census reads against the
  active scorer, and running it under a different salience version means
  registering one, which is a code change. Read-only like `corpus-stats`, with
  one difference that matters: the machine JSON is uploaded as a run artifact as
  well as summarised, because a statistical review is conducted over the file
  rather than the page. The artifact rides the **one-day** retention every
  analytics run artifact does — this repository is public, so one is
  downloadable by any logged-in user for as long as it exists, and the
  compilation-extent inventory in [security.md](security.md) bounds all three
  the same way. Re-reading a census after the day is therefore a re-dispatch
  rather than a longer window: it is deterministic over the blob its
  `corpus_sha256` names. Two things an operator needs before dispatching
  it. It carries by far the largest budget of the read-only modes — a
  latest-snapshot read per frame case under the corpus-split mode — and what
  bounds it is the read-only role's credential session rather than the wall
  clock: the census passes `role-duration-seconds: 8100` to the
  `corpus-readonly` composite, the scan step is capped at 110 minutes and the
  job at 125, so a scan too long for its credentials fails legibly inside
  them instead of dying on an expired token after the whole walk. Raising the
  ceiling further is that composite input again, within the read-only role's
  IAM maximum session duration. And it holds its
  **own** concurrency group — `run-analytics-census`, `cancel-in-progress:
  false` — rather than sharing `corpus-stats`'s: a cancelled job runs no upload
  step, so a sibling stats dispatch would otherwise take the artifact the mode
  exists to produce with it. Both jobs are read-only, so letting them overlap
  costs nothing.
- **`text-coverage`** (dispatch) assumes the same read-only role and pull, then
  runs `fedcourts corpus-info --text-coverage` — where the document text
  actually lives and for which cases it is missing, the enumeration whose
  store-side half only this job can produce (the content store is wired here
  and not on a dev checkout; the report's own `text source:` line names which
  side served it). The full report — the three untruncated case-id ledgers
  included, since a repair is a per-case question and a count names no case —
  is uploaded as a run artifact on the same **one-day** retention the census
  rides, for the same compilation-extent reason; the step summary carries only
  the part above the ledgers. Sized exactly like the census and for the same
  reason (a store round trip per live-slice case): `role-duration-seconds:
  8100`, a 110-minute step cap inside a 125-minute job, and its own
  never-cancelled concurrency group so a sibling dispatch cannot take the
  artifact with it.
- **`metrics-refresh`** (weekly schedule, or dispatch) keeps the committed metrics
  artifacts from drifting stale: `metrics/claim-scores.json` (input: the `data/`
  evaluations ledger), `metrics/leaderboard.json` (the same ledger plus the
  committed `metrics/statpack.json`, which its realized-Term skill column is
  scored against — so it regenerates *after* the pack)
  and `metrics/backtest.json` / `metrics/statpack.{json,md}`
  (input: the corpus) are deterministic stage commands that otherwise change
  only when someone reruns them locally. It reruns those tested
  `fedcourts` commands and — only when an artifact actually changed (they are
  byte-stable, so a no-op refresh diffs empty) — opens a **reviewed** PR rendered
  by the tested `metrics-refresh-plan` command: never a
  direct commit to `main`, never auto-merged. It mints the dev App token to do
  so; `qp-topic-label` below is the only other job here that does. The branch is fixed
  (`metrics/refresh`) and force-pushed, so an unmerged refresh PR is updated in
  place by the next tick rather than stacking.
- **`tool-usage`** (dispatch) rolls every committed `retrieval_log.json` into an
  **offered-vs-called** report: which configured MCP tools were never called,
  which are used by some engines and not others, and call counts per tool /
  engine / actor. The same walk adds per-engine result observability (whether an
  engine's transcript captures the answer side at all), how often the upstream
  quota turned a manifest-tool call away (denominated on the calls whose result
  condition was legible, so a capture-blind engine reads as unobserved rather
  than as throttle-free, and cut per engine only descriptively — one quota is
  consumed run-wide), cuts by mode / role /
  actor, calls beside each cell's estimated cost, and call volume against the
  evaluators' Brier scores — that last one scoped to blessed processes like any
  grade-bearing surface, and a denominator table with an under-powered verdict
  until a population clears the cell floor its module pre-declares. The dispatch
  takes the default scope, so while no committed cell is inside the freeze the
  usefulness section renders as empty and says so; the diagnostic read over every
  process version is `fedcourts tool-usage --all-versions`, run locally. It reads
  `data/` only — no corpus, no network — so it binds no
  environment and assumes no role, and the same `fedcourts tool-usage` runs
  locally and in the gate. Results go to the step summary; it commits nothing.
- **`qp-topic-label`** (dispatch) runs the `qp-topic-v0` topic labeler over the
  scoped extract of questions-presented texts (`fedcourts qp-corpus`, whose
  population and row ceiling are in [qp-topic.md](qp-topic.md)) and lands the
  measured per-case labels file
  (`data/qp-topics/qp-topics.json`) as a **reviewed** PR to `main` — fixed
  branch `qp-topics/refresh`, force-pushed, never auto-merged. It is the only
  mode that runs an agent, and therefore the only one **split across two jobs**,
  because `corpus-readonly` exports the assumed role's credentials job-wide:
  `qp-topic-extract` holds the read-only S3 role and writes the extract
  (`fedcourts qp-corpus`, under `$RUNNER_TEMP` — the command refuses an `--out`
  inside the checkout) to a one-day Actions artifact; `qp-topic-label` assumes
  no role at all, downloads that artifact, and runs the labeler with no cloud
  credential in its environment and no MCP config (the vocabulary is text-only,
  so the extract is the agent's entire evidentiary input). The labeler's
  turn-by-turn transcript is scanned and published as a second one-day
  artifact, `qp-label-transcript` — the thing to open when a run reports
  success but writes no labels (disclosure argued in
  [qp-topic.md](qp-topic.md)). It applies the same
  structural prohibition the cell workflows do — `data/qp-topics/` is moved out
  of the tree for the duration of the agent step, since reading the reference
  set would not improve the labels, only destroy the measurement — and restores
  it from the commit afterwards, then asserts the tree is otherwise untouched
  (the gate constants live in the checkout too). After the agent, the
  tested `fedcourts qp-topics` measures the labels against the hand reference
  set and enforces the agreement/coverage gate — below it, nothing is written,
  the measured block still reaches the step summary, and the job fails. The
  `label_model` dispatch input picks the labeler's model. See
  [qp-topic.md](qp-topic.md).

## `integration-test` — the infrastructure preflight

`integration-test` is the infrastructure preflight, also outside the cascade:
a strictly side-effect-free scenario runner — manual dispatch, plus one
scheduled canary — over the **corpus
read backends, the two sidecars, cascade cells, the engines' own invocation
blocks, the collect writer, and the
qp-topic measure path**,
against the real corpus remote for every scenario but collect and qp-topic —
the tested `fedcourts corpus-integration-check` read set, a
cell's-eye probe of the service sidecar, the tokenless CourtListener MCP
sidecar under the tested `mcp-integration-check` client, a stub
`local-cascade` cell, the `collect-run` composite over synthetic cell
artifacts (corpus-free and environment-free; every write surface stubbed or
diverted on the runner), the `qp-topic-measure` composite over canned labels
built from the committed reference set (token-free and credential-free), or
(the two token-spending scenarios) a single real-engine cell over the service
sidecar and a boot probe of each engine's own invocation block
— dispatched around changes to corpus access, the sidecars, engine
CLIs or engine actions, the collect contract, or the corpus-consuming
workflows and before
releases — from main, or via the `staging` deployment environment (collect
binds none; qp-topic binds one it never reads) from the `staging` branch, which
is the only branch that environment accepts (those runs are the promotion
gate's freshness evidence; see *Promotion: staging → main* below). The deployment environment resolves from
the dispatching branch by default — `main` gets `prod`, `staging` gets
`staging`, any other branch an empty environment holding no role variables
and no keys — and a `scenario=all` dispatch
fans the gate's whole required suite (every real scenario — collect rides the
run as its own environment-free job — with engine-smoke and
engine-actions-smoke once per engine each, so
three cells' token spend plus three boot probes) out of one run.
`scenario=all-offline` is that same
suite with all six token-spending engine legs dropped: token-free end to end,
and whole-suite evidence only for a pre-flight that skipped them (*The
engine-smoke skip* under *Promotion: staging → main* below).

The **daily canary** is the schedule: the three `engine-actions-smoke` legs
alone, at 11:53 UTC, catching a provider-side or action-side flip between
promotions rather than waiting for the next paid round. It runs from `main`,
binds `prod`, and titles itself so that it satisfies no freshness match — a
canary must never stand in for evidence a promotion has not paid for. GitHub
cron is best-effort, so a missed day is expected and tolerable; the gate, not
the canary, is the thing that blocks.

**How a red canary reaches anyone.** Through GitHub's own scheduled-workflow
failure notification and the workflow's run history — nothing else. It opens no
issue and posts no comment, because the workflow's side-effect-free invariant
is what lets it dispatch and run unattended at all, and an alarm that writes is
a write. So the canary is a *shortened discovery window*, not an alerting
system: what it guarantees is that the breakage is already in the run history
when someone next looks, rather than being discovered by a paid round. Check it
alongside the ops digest, and read a red one the way the run summary states it —
the leg names which engine's invocation was refused.
See *Infra-bound integration* in [testing.md](testing.md).

## `staging-corpus-refresh` — the staging corpus

`staging-corpus-refresh` builds what those staging-bound runs are meant to read:
the **staging corpus**, a lean slice of real cases in its own bucket/prefix
pair (`fedcourts corpus-seed-slice`), so orchestration and the read/write seams
get live end-to-end verification without anything gaining write access to the
production corpus. Its own workflow file on the risk-class rule below, like
every other corpus writer: it is the one reviewed asker of the staging
read-write role, whose trust names the `staging` environment itself — the
prod-fidelity call, so a wrongly-writing change fails visibly against the
disposable pair before promotion rather than first in production.
Dispatch-only, from the `staging` ref alone — the environment's branch policy is the gate, the
job's own first step refuses any other ref, and the promotion gate's
maintainer-run `contexts` stage reports whether that policy is actually set
(admin-read, advisory, not part of any automatic gate) — and **dry-run by
default**: the per-case census is the reading an apply is dispatched on, so the
procedure is two dispatches. What keeps it off production is IAM: the role is
read-only there. The seeder's own rail is the second line, refusing any
destination that is, or sits inside the bucket of, either store of its pinned
source — dedicated production-source variables the staging repoint never
touches. **One repointing is still outstanding**: a consumer resolves the committed
`corpus/corpus.db.ref` — whose digest names the production blob — unless the
out-of-band pointer override names the staging blob instead (*Developer
access* in [data-pipeline.md](data-pipeline.md)), and the scenarios read
production's pair until the staging environment's store variables — the
URLs and that pointer — are repointed. Provisioning the stores, the environment, and the role — and
that repointing — is the maintainer runbook in [security.md](security.md).

## `run-seed`, `run-pull` and `run-repair` — the corpus writers

**run-seed** runs the **historical Term walker** (supremecourt.gov, budget-free),
accumulating resolved outcomes reverse-chronologically by Term for the statpack's
per-Term base rates and the cert back-test set. It is a corpus writer split out
of run-pull so the backfill runs on a denser schedule (four dead-zone windows a
day); it shares the `corpus-write` concurrency group, so it still serializes with
run-pull's forward writers. **run-pull**'s **pull** job does targeted
CourtListener enrichment from the rate-limited **REST API** (the live job owns
SCOTUS freshness for free). One other consumer shares that REST budget:
**run-pull**'s dispatch-only **enrich** job (`mode=enrich-opinions`, sized by
the `max_cases` input) walks granted SCOTUS rows to their published opinion
cluster and lands the reporter citations and opinion body
(`fedcourts enrich-opinions`; scope and arithmetic in
[data-pipeline.md](data-pipeline.md)). It is the pass's only production lane —
never scheduled, and dispatched into a dead zone between pull windows so it
neither queues on the corpus-write lock nor stacks API spend onto a pull
window's. run-seed also runs seven
maintenance sweeps, each gated to one window a day and each converging rather
than one-shot — a re-run over an unchanged corpus does nothing. In order: the
**live-duplicate dedupe** (`fedcourts dedupe-live-rows`), which merges and drops
any SCOTUS petition carrying both a CourtListener-keyed row and a live-minted
reserved-range row — the pair shape a docket-number spelling leaves when it
defeats the channels' identity join — moving a minted event's committed
`event.yaml` with its re-keyed row, staged in the one pointer commit; the
**predict-scope reconcile**
(`fedcourts reconcile-scope`), which latches out-of-scope cases (the
shared exclusion rules — era, staleness, docket form, date consistency, and the
snapshot-aware bare opinion-import profile) in the corpus so they leave the
predictable set at the source; the **application-baseline relabel**
(`fedcourts relabel-application-events`), which converges application dockets
whose baseline event predates the motion/interim minting rule; the
**merits-judgment backfill** (`fedcourts backfill-merits-judgments`), which
parses each merits-bound grant's stored snapshot for the judgment entered,
feeding the statpack's merits section; the **merits-event backfill**
(`fedcourts backfill-merits-events`, preceded in the same step by the
moment-column stamp `fedcourts backfill-event-moments`), which mints the open
merits forecast events — corpus rows plus their ledger `event.yaml` files,
staged in the one pointer commit — onto granted, undecided dockets the live
mint never opened; and the **attribution repairs** (`fedcourts
remove-unmintable-events` then `fedcourts reopen-misattributed-outcomes`),
which converge the misattribution shape an earlier single-open-event
attribution shortcut wrote and its cause — removal first, clearing the
entry-pinned case of the reopen sweep's baseline-pair triage in the same
window, each bounded by a per-run blast-radius cap; and, last, the
**bulk-cluster scrub** (`fedcourts scrub-bulk-cluster-fields`), which
converges the stored circuit slice onto the ingest projection's carve-out —
the bulk export's misjoined cluster fields are withheld from a re-served
bulk row, and the scrub drops them from the rows nothing re-serves, keyed
on the fields no channel could have written to a non-SCOTUS row (the only
other writer, the opinion enrichment, is SCOTUS-scoped) and bounded by its
own blast-radius cap. The dedupe runs first so the
latch pass weighs deduped rows, and the event mint runs immediately after the
judgment backfill so pendency is judged on judgment columns as latched as the
stored snapshots allow; each then pushes the blob and commits the pointer like
any other corpus write.

Two further writer steps sit **ahead of the loop** on a dispatch-only footing —
the `refresh_terms` cursor reset and the `refresh_dockets` targeted re-serve —
where they precede the walk they change. With `refresh_streams` beside them,
those three are run-seed's whole dispatch surface; the maintenance passes live
on **run-repair**.

**run-repair** is the maintainer's repair bench — `workflow_dispatch` only, no
schedule and no `run:*` label, one pass per dispatch, dry-run by default, and
joined to the same `corpus-write` lock so a pass can never interleave with a
window's corpus push. It carries a generic selector: `repair` names the pass,
`repair_mode` is `dry-run` or `apply`, `repair_bound` carries the blast-radius
count, `repair_target` the pass's named subject, and `repair_options` its closed
vocabulary of switches. `dry-run` means the selected pass writes nothing — the
prerequisites each pass is gated on still apply, so a dry-run dispatch can move
the corpus pointer by a convergence a scheduled window would have made anyway.
[data-pipeline.md](data-pipeline.md#maintenance-passes) is the contract — what
each pass accepts, every refusal, the `dedupe-live-rows` prerequisite each
corpus pass is gated on, and the dispatch commands.

It is a separate workflow because its failure posture is the opposite of the
walker's. A standing sweep fails by *not converging*, and the next window
retries for free, which is what earns it `continue-on-error`. A pass fails by
*refusing* — an apply without its bound, a malformed cell id, a stamp the
command declines — and a refusal is the answer the dispatch asked for, so it
reddens the run rather than being absorbed. Splitting them also keeps the
bench's growth off the walker: a pass added here costs run-seed neither a
dispatch input nor a `LOOP_BUDGET_SECONDS` conjunct. There is no `guard` job on
run-repair, unlike run-seed, because every run was started by hand a moment
earlier by the person waiting to read its ledger.

What each pass is for:

`unlatch-overselected` clears the pre-resize `salience_selected` overhang a
capacity change leaves behind (`docs/salience.md`) — the latch's one `1 → 0`
writer, a deliberate act rather than a converging sweep. It brings the
predict-scope reconcile along with the dedupe prerequisite, because it
recomputes each pending cohort's selection and must recompute over an in-scope
corpus.

`qp-backfill` re-derives the stored questions-presented rows under the current
extractor. A `dry-run` prints the reason-class triage ledger to the run summary
and writes nothing; an `apply` rewrites the safe classes, verifies its own
convergence by re-running the dry-run — under the corpus split the durable write
is the content store's, so the pointer alone cannot witness it — and pushes. The
refusal guard holds either way: a stored full-length question the extractor can
no longer derive is reported, never emptied.

`rederive-distribution-parse` re-derives the corpus `distribution_count` column
under the registered parse named in `repair_target` — the first of the three
pieces of work that activate a new parse (`docs/salience.md`). Its write is a
direct `UPDATE` that bypasses the column's max latch, because the upsert path
would reject a narrower reading's every row and report success; a row whose
latest live-shaped snapshot discloses no proceedings entries is counted and left
untouched instead, which is as much of the latch's guard as a single pass can
carry. The rest is procedure: the **first** dispatch names the *incumbent* parse
and must report `changed = 0`, since anything the incumbent reading moves is
stored-column drift rather than a parse effect and would otherwise be folded
into the candidate's count. One pass in either mode — the plan the dry run
prints is exactly the write set, and a separate dry run ahead of an apply would
only repeat a full-population read of the content store — so the two-dispatch
procedure is a maintainer's reading of the first run, not a re-scan. The label
is refused up front and again in the step unless it is a lowercase parse label;
whether the label is *registered* is the command's own refusal. Its blast-radius
bound is fixed in code rather than dispatched, so the pass refuses a
`repair_bound` rather than ignoring one.

`normalize-docket-markings` converges stored docket numbers on their
marking-free spelling, draining the population the
`docket_numbers_carry_no_capital_marking` corpus check reports: the ingest write
site strips the Court's capital-case marking and raises `capital_case` beside
it, so a row outside the live slice converges only under a re-read aimed at it,
and this is the sweep that needs none. It can neither create nor resolve a
duplicate pair, since both channels reconcile identity on a key that already
strips the marking by shape; and having no ledger surface — its write is a
direct `UPDATE` of the index — it commits the pointer alone.

`response-backfill` re-derives the dated interim/merits signals from each row's
newest stored live-shaped snapshot, which under the corpus split lives in the
content store rather than the blob; it therefore reads through the job's
split-mode env like the merits-judgment sweep, counts a row with no stored
snapshot rather than failing on it, and writes a direct `UPDATE` of the index,
so the pointer is its own witness. Its bound counts the rows actually filled,
not the `candidates` denominator beside them, which rises with every new cert
grant that has not yet drawn a respondent brief — so a rise there is the
ordinary docket rather than a widened predicate.

`ocr-recovery` reads the scanned petitions off their page images. A petition
filed on paper reaches the corpus with no text layer, so nothing was extracted
for it and every cell minted over that case reads an empty petition — for as
long as the docket serves the same URL, since the poller and the Term walker
re-fetch a kind only when its link changes. It is the only pass that installs a
binary dependency, in its own gated step (`tesseract` and poppler's `pdftoppm`,
from the runner image's own archive), and one of the two whose bound is a
**slice size** rather than a refusal threshold: each case costs a re-fetch and a
page-by-page recognition, and runner minutes are the whole cost. That makes the
bound a *spend* cap, so the step hands the pass a wall-clock deadline as well —
sized under the step's own cap by everything that must still fit there once the
pass stops taking work — and the pass stops taking new candidates once what is
left will not hold the next one's estimated cost, which it reads off the stored
page count. A recovered
petition leaves the class, so successive dispatches drain it — but only the
recovered ones leave, and what a slice could not recover, or never started,
stays at its head to be retried first, which the ledger names case by case. Its `dry-run`
carries a second reading beside the class count — a small sample of the
population re-fetched through the writer's own fetch path, reporting what
supremecourt.gov serves a *writer* rather than what a cell's retrieval reported.
The apply writes documents, which under the corpus split live in the content
store rather than the blob, so the pointer cannot witness it: the step re-reads
the class afterwards and requires exactly what the apply's ledger said it would
leave behind.

`document-backfill` provisions the queued cases that hold no primary document.
A case reaches prediction with the filing that opens it — the petition on a
cert-form docket, the application on an interim one — because provisioning runs
at the transition that queues it; a case whose provisioning ran before the
selector had an arm for its filing type kept nothing, and no lane repairs that,
since the poller re-fetches a kind only when its link changes and a kind never
stored has no link to change. It re-keys each candidate off its stored docket
number and fetches that docket's JSON **fresh** rather than reading the stored
snapshot, because the question is whether the link is served now, then runs the
same selection and fetch the live poller runs — so a recovered case is
provisioned on exactly the terms a case provisioned at its trigger was, opposition
briefs and derived questions-presented row included. Its population is
**form-keyed** and scoped to rows that can still mint a cell, not to the wide
distributed stock, which is overwhelmingly legacy rows carrying no document
links at all. It is the second slice-bounded pass, and the one whose `dry-run`
is bounded too: that dry run fetches each candidate's docket JSON, which is the
whole diagnostic — it is what separates a case with a link waiting for it from
one at a floor — and it is a paced round trip per candidate. Two floors are
reported apart from the failures, because neither drains and reading them as
failures reports a converged class as a permanent defect: a docket carrying the
opening entry with no PDF behind it, and one carrying no such entry at all. The
second on a *modern* docket is not a floor but a selector regression, and those
cases are named rather than counted. Like the OCR recovery it writes documents,
which under the corpus split live in the content store, so the step re-walks the
class afterwards — an empty slice, which costs no round trip — and requires
exactly what the apply's ledger said it would leave behind.

`arrival-backfill` re-derives the interim baseline's arrival stamp — the day an
application was submitted to a Justice, which is the moment that event declares
and the day provisioning cuts on. What it repairs is a stamp rule **correlated
with the outcome**: the live poller serves the unresolved slice, so a decided
application has left the rotation and is never re-polled, and an event last
polled before the arrival read existed keeps the docketing date or nothing at
all. Resolution status therefore decides which reading a row carries, and any
retrospective interim population drawn from these events inherits that
conditioning. A forward cell is unaffected *once its row has been re-polled* —
not by construction: a queued row that has not been polled since the arrival read
shipped still carries the docketing stamp, and closing that gap is part of what
this pass is for. It is deliberately *not* predicated on resolution — repairing
only the decided half would condition the class all over again. Route and shape
are the response back-fill's: re-parse each row's newest stored live-shaped
snapshot with the same pure parsers ingest uses, with no upstream fetch, and
write a direct `UPDATE` of the index, so the pointer is its own witness. Direction is the
safety property. The cut keeps everything filed strictly before the day after
the stamp, so an earlier stamp admits less docket and a later one admits more,
and docketing is systematically the later of the two readings — the pass
therefore only ever moves a stamp earlier or supplies a missing one, and a parse
that would move one later is refused and named. Its ledger states how many stamps
moved and by how much, as a day-delta histogram — but that is the *window*, an
upper bound on what could have been admitted rather than what was, so beside it
the ledger counts the **entries** the pre-repair cut admitted and names the rows
whose own **disposition** fell inside that band. A one-day move on a docket
disposed of that day admits the outcome; a month over a quiet docket admits
nothing, and only the second reading tells them apart. It also splits the class,
the repairs and the residue by **resolution**, because what it removes is the
correlation on the slice carrying a readable snapshot: every other arm keeps the
pre-repair stamp, and a residue that is entirely decided rows is a correlation
shrunk rather than removed. It writes events rather
than a `cases` column, so unlike the response back-fill it re-mirrors the
touched cases — provisioning reads events back through the content store, and a
stale mirror would hand a cell the very stamp the pass replaced.

`merits-phantom-removal` drops open merits events whose docket carries no cert
grant — the shape a live re-poll leaves when it stops reading a grant out of the
proceedings and overwrites the stored date with NULL. Nothing re-mints one and
nothing ever closes it, so it parks permanently on the listed-unforecastable
triage surface. It is the one pass with a ledger half: the corpus row and the
committed event directory under `data/` are staged in the step's one pointer
commit, the attribution repairs' shape, because an uncommitted ledger half
strands a directory under an id the corpus no longer carries. It needs no
ordering against run-seed's merits-event mint — the mint writes only where the
grant column is non-NULL and this removes only where it is NULL, so neither can
touch the other's population. The `include-failed-attempts` option widens it
onto phantoms whose only committed output is `attempt.json` cell-failure
records, deleting those records with the event; it is off by default because it
is a trade rather than a cleanup — those records document real spend on an event
the docket never supported — and it rides the dry-run and the apply together so
the ledger read and the removal cover one population. Unlike `include-scored` it
does not also demand a bound in `dry-run`: it takes on no re-grade backlog, and
what it widens is the removal set the apply's bound already sizes.

`disposition-convergence` converges stored disposition labels onto the current
classifier, writing `outcome.json` under `data/` alongside the pointer in the
step's one commit. Its ledger names **which of its two arms** each relabel came
from, and the reading a maintainer owes them differs: `gvr` sharpens a label
whose grant binary does not move, while `disowned-grant` withdraws a grant the
classifier no longer reads at all — moving `actual_granted` 1 → 0 and re-dating
the resolution — so that count is the one that shifts realized grant rates and
every figure keyed on a resolution date (`docs/cli.md` carries each arm's
warrant). By default it converges the population carrying **no committed predict
or evaluate output**: rewriting the label under a cell that has already been
graded would move what a published standing was computed from while the standing
sat still, so any event whose directory holds agent output is reported in the
dry-run ledger rather than rewritten. Closing that backlog is a maintainer's
decision, and the `include-scored` option is where it is taken: it passes
`--include-scored` to both the dry-run and the apply, so the ledger read and the
rewrite cover the same population, and it demands `repair_bound` in `dry-run` as
much as in `apply`, unlike the bare bound, because what the number states there
is a decision to take on a re-grade backlog rather than a write bound. The two
readings are different: the plain dry-run's held-back lines size the *decision to
widen* (they are candidates the sweep never parsed, so most will not be
relabeled — only a candidate one of the two arms claims writes), while the bound
an `apply` is checked against is the widened dry-run's own relabel count, which
spans the scored and unscored confirmations together. On `apply` the step still
runs the dry-run into the step summary first, as a receipt of what the rewrite
acted on.

`sampled-frame-weight-repair` restores the derived sampling weight on the legacy
denial-sampling frame's latched-down rows: grid denials genuinely inside sampled
ranges that a channel writing with certainty min-latched to 1, leaving the nine
petitions each stands for represented by nobody. Where the other passes move
which bucket a row falls in, this one moves the weights themselves, so every
weighted denominator that admits IFP rows moves with it — the statpack's and
docket pack's weighted sections, the ops digest's always-deny floor, and one
committed prose figure in
[outcome-decomposition.md](outcome-decomposition.md). Its population, direction
and expected magnitudes are therefore pre-registered in
[freeze-record.md](freeze-record.md), and its dry-run ledger is read against that
entry. Every conjunct of the membership predicate is the guard's own rule — the
grid test, the walker's cursor, and the density guard's neighbourhood reading —
so the pass and the ingest seam that has to keep its result cannot drift apart;
the scope is the entry's, narrower than the rule, and a row the rule reaches
outside the registered cells is reported in the ledger and left alone rather than
repaired. The write is a direct `UPDATE` bypassing the column's **min** latch:
the stored weight only ever latches downward, an inclusion probability only ever
learned toward certainty, so the same value through the upsert path would be
discarded silently. Convergence is witnessed inside the command rather than by a
grep in the step: the apply re-runs its own selection and exits non-zero if
anything remains, which stops the job before the blob is pushed. No ledger
surface, so a pointer-only commit. **No scored number moves**: every
scored-segment cut is gated on a paid serial and this population is IFP, so
`metrics/leaderboard.json`, `metrics/claim-scores.json` and the back-tests are
unchanged. **The apply is not finished when the blob is pushed.** The weekly
metrics refresh regenerates the statpack; `metrics/docket.{json,md}` is on
demand (`fedcourts docket`) and the whole-slice IFP-inclusive figure in
[outcome-decomposition.md](outcome-decomposition.md) is hand-written, so neither
heals on a schedule and a stale copy of either carries no marker saying so. The
apply's own output names them.

A scored relabel is half a repair: the labels move there, and the grades taken
under the old label catch up through `regrade-stale`, which recomputes an
evaluator cell's graded fields under the cell's original stamp and rewrites
`evaluation.json`. It exists because the bench's passes rewrite and reopen
outcomes without consulting who has already graded them, so a cell's committed
outcome can move under a committed grade. The write is ledger-only — no blob
push, no pointer move — which is why it runs in its own job holding neither the
corpus role nor the content-store env: a pass that cannot reach the corpus
should not hold the credentials that reach it. What the scoring surfaces make of
the result is the command's contract, not the workflow's: per
[metrics/README.md](../metrics/README.md), a standing moves honestly only
through a grading the supersede-collapse counts, and a bare re-stamp of an
existing `evaluation.json` moves it with a trace only in the ledger's own
revision history. The cells are named in `repair_target`, one
`court/docket/event/run_id/actor` per
line (whitespace-separated, so spaces work as well as newlines), one invocation
per line — a cell three judges graded is three lines, since which judge's
evaluation is rewritten is not a thing to infer. A `dry-run` echoes each command
without invoking it. Every line is matched against the id grammar before
anything runs and a single malformed line refuses the whole list — the input is
maintainer-typed text entering a shell, and a half-applied list is harder to
reason about than a refused one; an empty list is refused too, in `dry-run` as
much as in `apply`. Because one pass runs per dispatch, the follow-through is a
second dispatch rather than a silent second step — which is the point: the
backlog a relabel owes is a maintainer's to schedule.

The full
design — sources, budget boundary, the
corpus/ledger storage split, and the historical corpus — is in
[data-pipeline.md](data-pipeline.md).

A Term walked to its frontier is invisible to every later run, so run-seed's
**manual dispatch** carries `refresh_terms` (blank by default, and blank on every
scheduled window) to re-open past Terms when the pipeline learns to read
something the walk did not capture. It runs `fedcourts refresh-historical
--apply` after the pull and before the loop, so the reset and the re-walk it
implies are one serialized operation under the `corpus-write` lock rather than a
local corpus edit racing a cron window. The reset reaches the remote only through
the loop's checkpoint push, so a failure before the first checkpoint leaves the
upstream cursors untouched. `refresh_streams` picks the numbering sequence: IFP
is ~70% of the probe cost and feeds no scored segment, so the paid stream is the
default.

`refresh_dockets` is the targeted instrument beside it, for when the rows
needing a fresh read are known and enumerated: Term-form docket numbers, one
per line or space-separated (`22-451 23-1234`), re-served and re-ingested
through the walk's own path by `fedcourts refresh-dockets --apply`. Re-opening
a Term to reach a handful of dockets pays for its entire serial range at
~1 req/s; this pays for what was named. It runs in the same slot as the Term
re-open, after the pull and before the loop under the `corpus-write` lock.
**No cursor moves** — a targeted
re-read is not a rewind — so the two inputs are independent and dispatching both
together is coherent: they write the same rows through the same latches, and
neither can undo the other. The numbers are grammar-checked all-or-nothing
before anything runs and the list is capped at 50 — the workflow's own cap,
tighter than the command's `historical.max_probes_per_run`, and sized well
inside what the step's 15-minute bound can serve at that rate, so an oversized
list is refused loudly rather than cancelling the run on a timeout; a list that
large wants `refresh_terms` instead. Like every other writer step here it
pushes its own blob and commits its own pointer, rather than leaving rows it
paid upstream requests for to a walk chunk that may fail before its first
checkpoint.

## Cascade

```
daily ×4 → run-seed → walk Terms newest-first, ingest every decided petition
                              └─ checkpointed: corpus-push + pointer commit per chunk
   daily ×4 / run:pull → run-pull (pull job) → push fresh facts to the corpus
                                 ├─ refresh active cases (oldest-first, budget-capped)
                                 ├─ detect resolution → write outcome.json when the
                                 │  disposition is machine-readable (git ledger);
                                 │  else queue an unrecorded outcome, surfaced
                                 │  per-case on the pipeline-runs dashboard
                                 ├─ derive the evaluate backlog (owed gradings,
                                 │  beside this cycle's fresh resolutions; the pair is
                                 │  reported as a count — no issue is filed for it)
                                 └─ create issues  ← APP TOKEN
                                    └─ run:predict    (changed case with open forecastable events,
                                                       unless the docket already looks
                                                       decided — skipped + surfaced;
                                                       held if PREDICT_HANDOFF_ENABLED=0)
   daily ×4 → run-pull (live job) → push fresh facts to the corpus
                                 ├─ probe supremecourt.gov docket-number frontier
                                 │  → onboard new petitions + applications
                                 │    (per-(Term, stream) cursors)
                                 ├─ re-poll the live cert watchlist (recent Terms first)
                                 ├─ re-poll unresolved interim applications (capped;
                                 │    substantive + changed + in scope → predict handoff)
                                 ├─ detect resolution from the proceedings text
                                 │  → write outcome.json (git ledger); else queue an
                                 │    unrecorded outcome, surfaced per-case on the
                                 │    pipeline-runs dashboard
                                 ├─ derive the evaluate backlog (as above)
                                 └─ create run:predict issues  ← APP TOKEN
                                    (held by PREDICT_HANDOFF_ENABLED)
       run:predict → plan (build matrix, post the plan report)
                                 → approval (the review hold: required
                                 │           reviewers release the spend)
                                 → predict[matrix] (artifact per cell)
                                 └─ collect → one auto-merged PR per run (+ a draft for partials;
                                              a facts-only PR when a run lands nothing)
       daily / run:evaluate → run-evaluate
                                 → plan (derive the backlog — or read the trigger
                                 │       issue's cases — then build the matrix and
                                 │       render the plan report)
                                 → approval (the same review hold)
                                 → evaluate[matrix] (artifact per cell)
                                 └─ collect → one auto-merged PR per run (+ a draft for partials;
                                              a facts-only PR when a run lands nothing)
```

Run logging creates nothing on the happy path. Every `run-pull` window (pull
and live, success or failure) that reaches checkout lands its row on the single
long-lived **Pipeline runs** dashboard issue — label `run-log-dashboard`,
non-triggering and never declared in an issue form's `labels:` (the same
discipline as every operational label here), edited in place like the Ops
dashboard, its state carried as a fenced JSON block in its own body
(`.github/actions/run-log-dashboard`): a rolling 14 days of window × outcome ×
handoff counts, plus the per-case unrecorded-outcome triage list. A window that
fails or is stopped mid-run (timeout or a human's cancel — the shared lock
never cancels an in-flight run; a stopped window gets only the alarm, no
dashboard row) opens (or reuses, for the same day) a `pull-log` / `live-log`
issue and leaves it open for a human — so an open run-log issue means exactly
"a window broke": the issue list is the alarm surface, the dashboard the
reference view, and neither depends on a later window firing to stay honest.

To run the predict → evaluate → validate cascade for one case **locally** — off
Actions, over the fixture corpus, offline by default — use `fedcourts
local-cascade` (see [cli.md](cli.md)). It reuses the same engine-runner seam and
registries, so a green local run mirrors a green CI run.

## ⚠️ The handoff token gotcha

Events created with the default `GITHUB_TOKEN` **do not trigger other workflows**
(GitHub's loop-prevention). So every cross-workflow handoff (e.g. run-pull creating
a `run:predict` issue) and every PR that must trigger CI is made with a **GitHub
App installation token** (`actions/create-github-app-token`), not `GITHUB_TOKEN`.
See `docs/security.md` for the one-time App setup.

## Authoring or changing a workflow

**Prefer a job or mode on an existing surface over a new workflow file.** GitHub
scopes permissions, secrets, and minted tokens per **job**, so a new job on an
existing workflow is exactly as least-privilege as a new file — a new file adds
surface area without adding isolation. A task earns its own workflow only when it
needs a different *trigger class* (the `run:*` issue-label cascade vs
schedule/dispatch) or a different *risk class* (the agentic fan-outs, the corpus
writers). Everything else — a new analysis, a new derived
artifact, a new maintenance sweep — should land as a mode/job on `run-analytics`
(or the closest existing surface), reusing the shared composite actions
(`setup-python-env`, `corpus-readonly`, `corpus-ranged`, `corpus-sidecar`,
`mcp-sidecar`, `configure-git-identity`).

**A `workflow_dispatch` may declare at most 10 inputs, and the "Run workflow"
form is where the limit bites** — inputs past it are reachable by API but the
UI silently stops rendering them, so a maintainer dispatching by hand cannot
set them at all and a documented input becomes undispatchable with no error
anywhere. Budget the slots: give a family of related operations **one generic
selector** (a choice naming the operation, plus a small number of shared
parameter fields) rather than a bespoke input per operation, which is the shape
`run-repair` carries for the maintenance passes. Validate the combinations up
front and refuse a field the selected operation does not take, so consolidating
costs no strictness. `test_no_workflow_declares_more_dispatch_inputs_than_the_ui_can_render`
pins the cap repo-wide.

**On a workflow that has a `schedule:`, an input gate must be false when the
`inputs` context is empty.** A schedule supplies no inputs, and GitHub compares
the resulting null numerically: `inputs.mode != 'none'` is **TRUE** on every
scheduled window (both sides coerce to `NaN`, and `NaN != NaN`), so a
dispatch-only step gated that way fires on the schedule it was meant to skip.
Two shapes are safe — conjoin `github.event_name == 'workflow_dispatch'`, or
compare against `''`, which null equals under the same coercion. Prefer naming
the value affirmatively (`inputs.mode == 'x'`, or an allow-list membership
test), which is false under an empty context by construction; that also matters
at *job* level, where the gate is what grants the job's credentials.
`test_every_input_gated_step_on_a_scheduled_workflow_is_fail_closed` pins it.

When you add a new `run:*` workflow or edit one, the existing workflows are the
canonical reference — each handles these cross-cutting traps inline, so copy the
pattern rather than rediscovering it:

- **Concurrency is evaluated before the job `if`.** An `issues: labeled` event
  fans out to *every* workflow that listens for it, and the job-level label filter
  runs only after the concurrency group is assigned. A label-reachable corpus
  writer job (pull, live, historical — the dispatch-only enrich job never sees
  a label)
  must therefore join the shared `corpus-write` group **only** when its own label
  matched — otherwise an unrelated label cancels a real writer. See the
  `concurrency:` expression in `run-pull.yml`. To dispatch one of
  these reliably, prefer `workflow_dispatch` over labeling.
- **The event payload is frozen; the checkout is live.** A `pull_request` job
  checks out the merge ref — the PR merged into the base's *current* tip —
  while `github.event.pull_request.base.sha` stays pinned at PR creation, so
  diffing the two attributes every commit the base gained since to the PR.
  Diff `origin/<base ref>...HEAD` instead (the `paths` / `cleanup-paths` jobs
  in `ci.yml`); the promotion gate reads its label from the API at check time
  for the same frozen-payload reason.
- **`git add data/` aborts when `data/` is absent.** No `outcome.json` is written
  on most runs, so `data/` often does not exist; under `set -euo pipefail` the add
  fails the step before the no-op guard. Stage the always-present pointer
  unconditionally and guard the rest with `if [ -d data ]; then git add data/; fi`
  (see `run-pull.yml`). The same shape lives in run-predict/evaluate.
- **Long-running jobs outlive their credentials.** A GitHub App installation token
  has a hard 1h life and an AWS OIDC session defaults to 1h. A corpus-writer loop
  must therefore stay within that hour, or re-mint the App token before it ages
  out and raise `role-duration-seconds` to cover the run. `run-seed`'s walk takes
  the first path: each window is a bounded chunk (≤40 min; the daily sweep window walks 25
  to fund its trailing sweeps) under one token, so it
  needs no re-mint — a deliberate simplification over a longer walk that would.
- **The runner is ephemeral, so fixed per-run costs are re-paid every run.** Build
  expensive shared state once per job and reuse it across a loop's chunks rather
  than per chunk.
- **A step that calls a cloud provider can hang far longer than it can fail.**
  `aws-actions/configure-aws-credentials` retries a failed AssumeRole 12 times by
  default, and an unreachable STS endpoint fails each attempt on a multi-minute
  TCP connect timeout rather than promptly — so the default policy outlasts every
  job budget here and the job is killed mid-retry instead of returning an error.
  A window is then spent entirely on hanging, and a `cancelled` result gets
  attributed to whatever the job was *supposed* to be doing. Every call site
  passes `action-timeout-s`; note that a composite action cannot put
  `timeout-minutes` on its own steps, so the action's own timeout input is the
  only bound available inside one. The same question is worth asking of any step
  that talks to an external service: what is its worst case, and is it shorter
  than the job budget?
- **The CI uv pin and the lockfile format are coupled.** `setup-python-env`
  installs with `uv sync --locked`, which refuses a lock it cannot read as
  current — so a lock written by a *newer* uv than the action's pin fails every
  job that installs dependencies, including the scheduled data runs, and the
  trigger is a local tooling upgrade rather than any dependency edit. The
  devcontainer's uv is not pinned to the same version, so relock with the pinned
  uv, or bump the pin in the same change. `scripts/gate.sh lock` catches the
  drift half of this locally; the version half only shows up in CI.
- **A branch built during a long job must be based on a freshly fetched remote
  tip, not the job's own checkout.** The deterministic writers commit to `main`
  throughout, so a matrix that runs for an hour finishes holding a stale local
  `main`; a branch cut from it carries commits that are no longer on the remote —
  including any merged `.github/workflows/*` change — into the push pack, and a
  token without `workflows` permission has the whole push rejected. `collect-run`
  carries the worked reasoning and the fetch-then-branch shape; copy it in any
  job that pushes a branch it built while other jobs were writing.
- **That branch switch also swaps the source the job is running.** `git checkout
  -B <branch> origin/main` rewrites every tracked file in the working tree,
  `src/fedcourtsai/` included, and `uv sync` installs the project *editable*
  against that tree — so every `uv run fedcourts` after that line executes
  `origin/main`'s CLI, not the ref the workflow was dispatched at. On `main` the
  two are the same file and nothing shows. Off it they are not, and the failure
  is silent in the worse direction: a step passing a flag its own CLI defines
  dies against an older `main`, and the integration scenario that exists to
  catch that reports `main`'s behavior instead — so a `staging` change to the
  contract can never go green, and the promotion freshness gate wants exactly
  that scenario green. Any job that runs the CLI after switching branches must
  pin it first: `collect-run`'s `Pin the CLI to this checkout` step copies
  `pyproject.toml`, `uv.lock`, `README.md`, and `src/` to `$RUNNER_TEMP`, syncs
  there, and exports the absolute path the rest of the step calls. A shape test
  fails on a bare `uv run fedcourts` reappearing in that composite.
- **A GitHub API call has no retry unless you give it one.** Two classes of
  call route through `gh_retry`. The steps that keep the run *record* — the ops
  and pipeline-runs dashboards, the data-validation escalation, the per-day
  `pull-log` / `live-log` alarms, the seed guard, run-backtest's result
  comment — are bookkeeping about a run rather than the work. The **handoff writes** are the work: `open-run-handoff`'s predict
  trigger-issue create, and the trigger-issue closes in run-predict /
  run-evaluate. Outside
  those two lists a bare call is fine and a repo-wide rule would be one nobody
  could keep — the collect jobs' own PR plumbing and ci.yml's label read are
  not on this surface. A transient 5xx costs something the run never earned,
  and what it costs depends on the site, so read yours: on the run-ops steps
  and the guard's clear-the-incident path a blip reddens a run that did its
  work; on the dashboard (`continue-on-error`), the alarms (which only fire on
  an already-failed window), and the back-test comment (`continue-on-error`
  too) nothing turns red and the *record* is what goes missing; at
  `open-run-handoff` a blip costs the whole predict round, and a lost
  trigger-issue close leaves an issue that run-ops reads as a stalled fan-out.
  `gh` also sets no client-side request timeout, so a stalled connect hangs to
  the job's kill with nothing written.
  Wrap each call in `gh_retry` (`scripts/gh_retry.sh`, sourced where a checkout
  exists and no agent has run in it; copied inline — a test pins the copies
  identical — wherever sourcing is unavailable or unsafe: the steps that must
  fire even when the checkout failed, the `rejected` jobs that are *given* no
  checkout because one is another way to strand the issue they exist to close,
  and the back-test's report step, whose workspace its own agent cells could
  have rewritten), and give the step a `timeout-minutes` that admits
  the retries — three attempts at `timeout 30` plus backoff is 105s per call.
  A call that routes through `agent_feedback.py`'s runner carries the bound
  already: that module's default `GhRunner` applies the same three attempts at
  the same 30s cap to every `gh` call it makes, so the `post-issue-comment`,
  `post-agent-feedback`, `daily-digest --post`, and `post-weekly-digest`
  commands — the plan report each non-empty
  predict/evaluate round posts before the review hold, the collect job's stall
  and secret-scan reports, the flag roll-up latch itself, and both digests'
  issue creates — are covered at
  the seam, and a new caller of it inherits the bound rather than adding a copy.
  `authz.py`'s collaborator-permission lookup — behind the `authorize-trigger`
  gate every label-triggered `run:*` workflow (the fan-outs and run-pull) runs
  before privileged work — carries the same bound in its own default lookup,
  because its fail-closed posture makes an unretried call worse than a lost
  record: a blip at check time reads as `"none"` and refuses a legitimate
  actor's round, and an unbounded stall hangs the gate itself. That is
  the seams' coverage, not Python's: a `gh` call made anywhere else in the
  package is as bare as an unwrapped shell one. Budget for it the same way —
  105s per call, against whatever cap the calling step or job carries.
  Retrying never changes what a failure *means*: exhaustion returns non-zero
  (raises, on the Python side; at the authorization lookup, the fail-closed
  `"none"` any error yields, on which the command still exits non-zero — a
  sustained outage still refuses), so a handoff write that never lands still
  fails its run loudly, exactly as an unretried call would. What the retry
  buys is that a blip does not decide it.
- **Shape a retried lookup so its failure cannot read as an empty result.**
  Most of these lookups feed a find-or-create, so an empty `num` reads as "no
  issue yet" and opens a duplicate or restarts a dashboard's rolling state.
  (The back-test's PR lookup feeds none — an empty result there costs only the
  review-PR back-link — but it takes the same shape, so the rule has no
  exception to remember.) Never let
  a retried call be a non-final element of a pipeline: filter with `gh`'s own
  `--jq` inside the same command, or assign the output and filter the variable.
  Either way `set -e` stops the step on the command itself. Note the limit of
  that — it narrows the dependence from errexit *and* pipefail to errexit
  alone; with `set -e` off the empty result still reaches the branch.

Validate any `.github/` change locally with the linters CI enforces (see the
local gate in [AGENTS.md](../AGENTS.md)), and run the **`workflow-reviewer`**
subagent (`.claude/agents/workflow-reviewer.md`) on the diff before pushing — it
runs those linters and reviews for what they miss (the security model and the
logic-in-tested-Python convention above).

## Promotion: staging → main

Code and config land on `staging`; `main` is the official pre-registration
record and takes code only in reviewed **promotion batches**. Data never waits
on promotion: the deterministic writers (pull, seed, live) and the data-run
collect PRs land on `main` directly.

Why the indirection: two classes of bug are invisible to per-PR CI but caught
by an integration pass over real infrastructure — a workflow that is never
invoked, and a workflow-file change that reaches `main` mid-matrix and changes
what a running fan-out's later jobs execute (the collect-recovery section
below describes the damage). The promotion gates target exactly those two.

The mechanics:

- **Feature PRs target `staging`** (AGENTS.md), and the routing is enforced:
  `main`'s required checks are exactly `gate`, `paths`, `promotion-gate`, and
  **`main-base`**. `main-base` is the merge-routing jail — it runs, and fails,
  only on a PR to `main` whose head is not `staging` or a reviewed non-feature
  lane (the collect run branches, the maintainer's cleanup sweep, the
  metrics-refresh, cert-backtest, and salience-replay PRs, and the qp-topic
  labeling run's `qp-topics/refresh` PR); on those
  legitimate lanes it reports `skipped`, which satisfies the requirement. Its
  definition lives in `main`'s own ci.yml, so the context reports on every
  lane into `main` (docs/security.md inventories this).
  Rulesets cannot constrain a PR's source branch, which is why the routing
  lives as a check at all, and why the check deters mistakes while the human
  merge is what catches sabotage: a PR that edits ci.yml runs the edited
  definition. Dependabot targets `staging` for the same reason. The `staging`
  ruleset itself requires a pull request plus the status checks that can report
  on a staging-targeted PR — `gate` and `paths`; `main`'s other two,
  `promotion-gate` and `main-base`, key on a base of `main` and are always
  `skipped` here — with the **repository admin
  role as its sole bypass actor** — a
  required-checks rule blocks direct pushes of commits that carry no passing
  check runs, so the admin role is the only identity that can land the sync
  merge below — the role an interactive agent session borrows, which is why
  `AGENTS.md` carries the discipline rule against using it. Neither GitHub App *bypasses* `staging`: the scheduled
  `sync-staging` workflow holds a write token to it but opens an ordinary PR
  that must satisfy the same required checks, and `promote` itself performs no
  write at all.
- **Scheduled sync.** `staging` never owns data, so it falls behind `main`
  as the writers and bot lanes commit there. The `sync-staging` workflow
  merges `main` into `staging` daily by opening a PR that auto-merges once
  the staging ruleset's checks pass — gated like any other change, not
  bypassed. Syncing on a schedule rather than at batch time is what keeps the
  cost off the promotion path: the same merge done at promotion moves
  `staging`'s head, and integration freshness is per-SHA, so every scenario
  would have to be re-dispatched for a merge whose content is
  already-gated main history joined with already-gated staging history.
  `promote` still checks the ancestry, and still prints the manual
  merge-and-push commands for the maintainer's admin bypass — the escape
  hatch for a conflicting sync the schedule could not land on its own. The
  sync defers itself while a promotion PR is open, so it never moves the head
  a batch in flight is being tested against. **Ordering:** `schedule` and
  `workflow_dispatch` both read the file from `main`, and the `prod`
  environment is `main`-only, so an edit to `sync-staging` takes effect only
  once it promotes.
- **Two gates, one definition.** `scripts/promotion-gate.sh` checks
  *quiescence* (no `run:predict` / `run:evaluate` / `run:backtest` fan-out in
  flight — no open trigger issue, no unfinished run) and *freshness* (every
  required integration scenario green at exactly the staging head being
  promoted — one green `scenario=all` run, which succeeds only when every
  matrix leg and its collect job does, satisfies all twelve required runs at
  once, engine-smoke and engine-actions-smoke counted once per engine each).
  The `promote` dispatch runs
  it as pre-flight; ci.yml's `promotion-gate` job runs it as a required
  check on the promotion PR.
  Re-run that check right before merging — quiescence is point-in-time.
- **The engine-smoke skip, and how far it reaches.** Waiving the six
  token-spending engine runs costs every piece of evidence that real engines
  still run at the sha being promoted: that a cell completes in the production
  posture (engine-smoke), and that each engine's own invocation block is still
  accepted by the surface receiving it (engine-actions-smoke) — the second
  being the class an action version bump breaks, silently, on the very
  promotion that carries the bump. Both families leave together, and must: the
  whole-suite acceptance the skip unlocks is decided before the required set is
  read, so keeping one family required while accepting an `all-offline` run —
  which ran neither — would satisfy that requirement without exercising it.
  Unsound, not stricter. Whether that evidence
  is worth its tokens for a given batch is the maintainer's risk call; the
  default at every surface is the full suite, and a batch that cannot affect a
  cell — docs, analytics, non-cell code — is the clear case for waiving.
  It takes **two separate acts**, because a pre-flight and a merge are
  different decisions:
  - `promote`'s **`skip_engine_smoke` input** drops all six from that
    dispatch's freshness check and accepts a token-free `scenario=all-offline`
    run as whole-suite evidence. It buys a cheap answer to *is anything else
    missing* before paying for them, and decides nothing about the merge.
  - the **`promote:skip-engine-smoke` label** on the promotion PR drops them
    from ci.yml's `promotion-gate` job — the required check — for that batch
    only. `main`'s ruleset still has no bypass for the check itself (the data
    App's deterministic writers are its only bypass actor), so the label is
    the whole of the discretion: every other gate stays strict, and the next
    promotion starts strict again.

  The label is read from the API when the check runs, not from the event
  payload, so the documented practice — re-run `promotion-gate` immediately
  before merging — picks it up without `labeled`/`unlabeled` on ci.yml's
  trigger, which would re-run the whole suite on every label edit to every PR.
  A waived run says so three ways: the gate script names the dropped entries
  in its log, and the check annotates the PR and writes what was traded away
  into its run summary — so a batch that merged without real-engine evidence
  is legible as such from the promotion's own record.
- **The loop.** Dispatch `promote`; it gates and prints exactly what is still
  needed — the sync commands when staging is behind, the scenario dispatch
  commands when freshness is unmet, or, when green, the `gh pr create` command
  for the promotion PR. The workflow performs no write itself: a PR created with a
  workflow's own token triggers no `pull_request` checks, so the maintainer
  creating it is what makes the required checks real. Merge promotions with a
  **merge commit**, never squash — `staging` and `main` must share history or
  every later sync re-merges rewritten commits.

The full path of a change, operator's view:

1. Branch off `staging`, work, run the relevant gate stages and reviewers,
   open the PR against `staging`; review and merge. The change is now staged
   but **not live** — production jobs execute from `main`.
2. When a batch is worth promoting: dispatch `promote`; if it asks, run the
   sync — dispatch `sync-staging` and let its PR land, or, if that PR
   conflicts, run the printed commands (your admin-bypass push) — then
   re-dispatch.
3. Dispatch the required integration scenarios at staging's post-sync head —
   one `scenario=all` dispatch covers the whole suite, or per-scenario runs
   add up to it (the summary prints both forms) — then re-dispatch `promote`.
   Name the case: a staging dispatch adds `-f court=scotus -f
   docket=<seeded-slice member>`, because the run-time case resolver reads a
   candidate window out of the blob's snapshot index and the seeded staging
   slice, written split-on, carries none — so a dispatch that leaves `docket`
   empty refuses in the plan job. The staging-corpus runbook in
   [security.md](security.md) says which cases the slice holds.
   On a cell-inert batch, `promote -f skip_engine_smoke=true` first: it prints
   the `all-offline` form and tells you whether anything *else* is missing
   before you pay for the engine legs, which step 4 still needs.
4. Green promote hands you the `gh pr create` for the staging→main PR; its
   `promotion-gate` check re-verifies quiescence + freshness. Add the batch's
   **stated effect check** to that PR body — what should be true once it is
   live and the command that shows it, collected from the feature PRs'
   handover notes (AGENTS.md asks each for one); the workflow's own body is
   fixed, so this is a hand edit. Re-run the
   check right before merging, and merge with a **merge commit**; tag the
   merge commit `promotion/<YYYY-MM-DD>` (annotated preferred, lightweight
   acceptable; `-2` for a same-day second batch — the *Tags* subsection
   below). Live on the next workflow run.
5. Run that stated effect check and record what it printed. A promotion
   changes code, not state, so until something executes the check a batch that
   changed nothing is indistinguishable from one that worked. Mind the timing:
   an effect visible only in produced output cannot be checked until the next
   run of the job that produces it, so a check that comes back empty before
   then reads *not yet*, not *didn't work* — say which you saw.

One-time setup (maintainer): create the branch from main (`git push origin
main:staging`); add the `staging` ruleset — require a pull request plus the
checks that can report on a staging-targeted PR (`gate` and `paths`),
**repository admin role as the only bypass actor** (docs/security.md
inventories it); and add `promotion-gate` — and, once the *Adding a required
status check* procedure below clears it, `main-base` — to `main`'s required
checks alongside `gate` and `paths`. Each reports `skipped`, which satisfies
the requirement, on every PR it does not gate; requiring a context before its
producing job reaches `main` strands every collect auto-merge PR, which is
what the procedure's ordering prevents.

The `staging` *deployment environment* the freshness runs deploy to
(deployment branches restricted to `staging`, the read-only and staging
read-write role trusts, per-environment engine keys) is separate wiring,
described in docs/security.md.

### Tags

Tags on `main` record the project's public reference points, in three
namespaces. What makes the record trustworthy is the ruleset's
update/deletion block on these namespaces, not the tag's object type — so
for `promotion/` and `results/` an annotated tag is preferred (for the
message and date it carries) and a lightweight one is acceptable. A
`prereg/` tag is annotated, and not merely by preference: the freeze
procedure writes the pre-registration record into the tag message
(docs/process-version.md), so the message is load-bearing there.

- **`prereg/<label>`** — a pre-registration freeze commit, e.g.
  `prereg/proc-v1` on the commit that fills `FROZEN_PROCESS_DIGESTS` and sets
  `FROZEN_SINCE` (docs/process-version.md carries the freeze procedure).
  One tag deviates: `prereg/proc-v4` sits on the promotion merge that
  carried its freeze commit rather than on the freeze commit itself — the
  namespace blocks moving it, and the freeze record in docs/freeze-record.md
  states the placement and its consequence.
- **`promotion/<YYYY-MM-DD>`** — a staging→main promotion merge commit; a
  `-2` suffix distinguishes a same-day second batch.
- **`results/<term>-<milestone>`** — the commit carrying a published metrics
  refresh, e.g. `results/ot2026-longconf`.

One-time setup (maintainer): before the first tag is minted, add a tag
ruleset blocking update and deletion on all three namespaces — a movable
pre-registration marker defeats its purpose. Creating a tag is likewise a
maintainer step, like the promotion merge it usually accompanies.

### Adding a required status check

The ordering is forced, and getting it wrong stops data production rather than
failing loudly: a context nothing on `main` produces leaves every PR into
`main` pending forever, and the auto-merging collect PRs hang first.

```bash
scripts/promotion-gate.sh contexts <candidate>   # the context you want to require
```

It reads `main: require PR`'s live required contexts and `main`'s own workflow
files, fails if anything already required has no producing job, and reports each
candidate as ready or not-yet. It is **not** part of `all`: reading a ruleset
needs repository-administration read, which `GITHUB_TOKEN` cannot hold at all,
so automating it would mean handing a CI job the repo's most powerful scope to
report an advisory fact. Run it with your own token.

1. Land the job on `staging` and let it promote to `main` in an ordinary batch.
2. `scripts/promotion-gate.sh contexts <candidate>` — proceed only on *ready to
   require*.
3. Confirm a real PR of the kind you are gating reports the context. For a
   context that must report on the bot lanes, that means watching one of their
   PRs, since those auto-merge and are what a mistake strands.
4. Add the context to the ruleset. Re-run step 2 afterwards: it now checks the
   context you just added.
5. Update the surfaces that record the required set — the pinned list in
   `tests/test_required_checks.py`, which is the only part of this that runs
   unattended, plus the inventories in docs/security.md and the promotion
   section above. If the pinned list lags the ruleset, a later promotion that
   renames the newly-required job hangs collect PRs with nothing red to show
   for it.

The same ordering applies to `staging`'s ruleset, which gates the unattended
`main`→`staging` sync PR. The stage above reads `main`'s; check `staging` by
hand until there is a reason to parameterize it.

## The predict/evaluate matrix

`plan` runs `fedcourts predict-matrix` / `evaluate-matrix`, which expands the
**registry × cases × events** into a GitHub Actions matrix. Where the cases come
from depends on the round: from the issue body's ` ```json ``` ` case block for
`run:predict` and for a labelled `run:evaluate`, and — for a scheduled or
dispatched `run:evaluate`, which has no issue — from the evaluate backlog the
matrix command derives itself. `predict-matrix` self-derives in the same shape
when given no input, from the predict backlog
(`pipeline.pull.derive_predict_backlog`, described in [cli.md](cli.md)); today
`run-predict` always passes an issue body, so the capability exists ahead of a
caller for it. When prediction scope is gated
(`predict.scope=scotus_docket`) the builder reads each case's corpus row (only a
SCOTUS docket is in scope, minus the shared exclusion reasons), so `plan` first
pulls the corpus; with the gate on
and no corpus on disk the build fails loud rather than emit an empty matrix.
`fedcourts predict-plan` / `evaluate-plan` are the read-only rehearsal of this
same builder — every step below, reported as a JSON document with its per-step
drop counts and nothing minted; with `--approval-report` it writes only that one
report file, the bounded markdown a hold gate posts ([cli.md](cli.md)). Each
matrix cell routes to Claude Code, Codex, or Gemini by the entry's `engine`. The
agent writes files only. The workflow's `strategy.max-parallel` throttles the
whole fan-out, however many cases it spans. After scope filtering the builder
also applies a **salience-independent volume cap**
(`predict.max_predict_cells_per_run`, default 240): a hard backstop on the number
of cells queued into one matrix, below GitHub's 256-job ceiling, that holds even
if salience selection fails open. Overflow cases are deferred **whole** (never
splitting a case's engines) in a deterministic case-id order, with the deferred
count surfaced as a `::warning::` and in the plan's step summary; a deferred case
stays in the predict queue and re-runs next cycle, so the cap defers rather than
drops. This is the numeric backstop, distinct from the coarse
`PREDICT_HANDOFF_ENABLED` on/off pause below — and distinct again from the
**review hold**, the per-run gate between plan and spend on both fan-outs:
each plan job renders its report to the run's step summary — and posts it to
the trigger issue where there is one — and the matrix waits on
a required reviewer approving the `review` deployment in the Actions UI —
one environment serves both holds, so the reviewer approves in the same
place whichever channel is asking, though the evaluate report's spend line
carries the weaker basis its plan states: a scaled pre-freeze anchor until an
evaluate fan-out under the currently blessed grading digests measures the
cert stage. A scheduled evaluate round has no trigger issue, so its report
lives only on that summary — the page the pending deployment review links to,
which is where the approver reads it. An issue-triggered held run also shows
on `run-ops`'s open-trigger list as a stalled fan-out — do
not follow that list's re-fire advice while the hold is still *Waiting*, or
the re-label mints a second plan behind the first. A run sitting in
*Waiting* is a request for that decision, not a stall; a hold that
does not release (rejected, cancelled, or expired) closes its trigger issue
with the plan report as the record, and re-labelling re-queues with a fresh
plan. A declined scheduled round has no issue to close and needs no re-queue:
the backlog it declined is re-derived on the next tick.
Approve one held run at a time, and treat a hold older than a day as a
stale plan to reject and re-queue rather than release: the plan-time gates —
predict's already-predicted gate and stranded-run guard, evaluate's
predictionless and already-graded drops — were all evaluated when the plan
was minted, so a long
hold un-anchors them — two simultaneously held plans over overlapping
events were each minted before the other spent, and releasing both
double-spends the overlap. The two plan reports make the overlap visible
before either release — on the trigger issue where the round has one, on the
run's step summary otherwise; a mechanical post-release re-check
belongs to the auto-release follow-up, where no human reads the reports. A
rejected hold is an unsatisfied-gate report, not an incident — but unlike
`promote`, whose failures the ops dashboard annotates as gate reports, the
dashboard cannot distinguish a rejected hold from a real fan-out failure,
so a depressed run-predict or run-evaluate success rate during shakedown
reads against this note rather than against the fleet.

A predict cell refuses to run for two reasons, both landing on the same gate in
`run-predict` (`refused=true`, which skips the event materialization, the MCP
sidecar, the comment-token mint, and every engine step). One is the
**provisioning gate**: `provision-snapshot --refuse-terminal` exits 3 when the
record or the snapshot shows the event is not open, or when the snapshot is
older than the forward staleness bound. The other is an **unprovisioned
record**: provisioning wrote nothing (exit 1 — usually a corpus with no
snapshot for the case, but a failed corpus read lands there too), or
`assert-cell-record` finds the provisioning write did not land complete — no
`record/context.json`, one that does not parse, or no readable snapshot at the
date that context names. That last check parses the snapshot rather than
counting its bytes: the provisioning write is not atomic, so a half-landed one
leaves a truncated file a size check would pass.
The provisioned snapshot is every predictor's guaranteed-common input, so a cell
that ran without one would forecast from base rates alone while its output
claimed the shared baseline, and no reader of the ledger could tell the two
apart. Refusing costs a cell; running one costs the comparison. Which cause
fired is a `::warning::` annotation on the refusing step, so a fleet of skipped
cells is attributable from the Actions UI — and the unprovisioned arm ends its
step red under `continue-on-error` on purpose, since it is an anomaly worth a
visible mark where the forward gate's refusal is a designed outcome.

The predict prompt still tells a forward cell it may find itself without a
provisioned snapshot and should then predict from priors and base rates with a
`flags.json` note. That branch is unreachable — the workflow refuses such a cell
before any engine step — and the sentence stands until the next re-blessing,
because the prompt's bytes are a `process_version` digest input
([process-version.md](process-version.md)): editing it would partition the
frozen headline across a line no cell can reach.

One interaction to know: a refused cell produces no output either way, so
collect records a failure fact that counts toward
`predict.max_attempts_per_cell`. For a record-gate refusal that terminal state
is right — a decided event must never re-queue (and the plan-time
forecastability re-check drops it anyway). For a *staleness* or *unprovisioned*
refusal it means a stalled poller, or a case the corpus never carried, quietly
retires those cells after five predict cycles; the recovery is to fix the
upstream gap and re-queue with a fresh `run:predict` issue, or clear the
committed attempt facts in a reviewed PR where the cap itself was the problem.
Distinguishing refusal kinds in the failure fact so a non-terminal refusal never
burns the cap is open follow-up work.

On `run:predict`, `plan` also refuses to re-mint a cell that already ran. A cell
spends its tokens before `collect`, the run's single durability step, so a
failed collect leaves every prediction in a cell artifact and nothing in the
ledger the already-predicted gate reads — and the next live cycle re-derives the
same events and re-spends the whole run. Before building the matrix, `plan`
lists the cell artifacts of this workflow's completed runs from the last 48
hours whose `collect` did not conclude success, and **withholds** any cell
already sitting in one, naming the stranded run and `gh run rerun <id> --failed`
per cell: the remedy is to recover that run, not to re-run this one (the
collect-recovery section below carries the order). The match is per predictor ×
case × event and keys on the artifact's *existence*, not on whether that cell
produced anything — a cell that spent its tokens and delivered nothing is
withheld too, because collecting the run is how anyone learns which of the two
it was, and the event re-queues normally once the ledger is honest. A cell with
no artifact — never queued, or dead before upload — still runs. The census step
fetches and filters only: every decision is in `fedcourts predict-matrix`
(`--stranded-file`), and it degrades open at two grains rather than blocking a
legitimate run, since the failure this guard prevents is expensive rather than
dangerous — a run it cannot read after three attempts drops out of the census
with a `::warning::`, and a failure leaving nothing usable empties it
altogether. The guard also releases itself: a run leaves the census once its
`collect` concludes success on the latest attempt, and ages out of the window
regardless. A maintainer who wants a fresh run *sooner* makes that an explicit
act rather than a new trigger — delete the stranded run's cell artifacts (`gh
api -X DELETE repos/<owner>/<repo>/actions/artifacts/<artifact_id>`), then
re-queue.

If the matrix comes back **empty** — every queued case was out of scope (or already
predicted) — the `predict`/`evaluate` and `collect` jobs are skipped, so nothing
would otherwise close the trigger issue; the `plan` job closes it with a note
instead of leaving it orphaned open. (Pull avoids filing such all-out-of-scope
runs in the first place, so for `run:predict` this is the backstop for a
manually-filed or partial one. A scheduled `run:evaluate` has no issue to close
and reports the empty matrix on its step summary instead — for it a drained
backlog is the ordinary resting state, not an exception.) Note
the volume cap above can also empty the matrix (when it defers *every* case);
so can the ex-post spend backstop (`spend.ceiling_usd` in `config/tracking.yaml`
— armed, see [budget.md](budget.md)) when the trailing window's measured spend
reaches the ceiling; and so can the plan-time forecastability re-check, when no
event the trigger listed is still forecastable — each has resolved since the
issue was queued, or is a merits moment on a grant gone stale unparsed. The close
step cannot tell any of those from scope-empty, so it closes with the
out-of-scope note in all four cases. On `run:predict` the stranded-run guard is
the one exception: when it withholds *every* cell, `predict-matrix` writes the
close note itself (`--stranded-note-file`) and the step posts that instead, so a
fully-superseded run says recover the uncollected run rather than reporting
nothing was in scope. Each surfaces its own escalated `::error::` for correct
attribution, and the close is safe in each case for its own reason: a cap- or
spend-deferred case stays in its queue and re-queues next cycle, an
unforecastable event needs something other than a re-queue (a grade for a
resolved one, a corpus fix for a stale grant), and a withheld event
re-queues on a later cycle for as long as no prediction is committed for it. A
spend-breach deferral clears on its own when the window rolls past the burst
that tripped it (or when the maintainer raises `spend.ceiling_usd`). A breach
driven by a sustained *rate* rather than a burst — a capacity knob left
non-binding, which at the current planning rate runs above the ceiling
([budget.md](budget.md)) — does not clear that way: it re-trips each cycle, and
the fix is the capacity knob or the ceiling, not waiting.

### The evaluate cell grades blind

An evaluate cell brackets its agent with two deterministic harness steps
(`fedcourtsai.blinding`, and *Semantic claims* in
[outcome-decomposition.md](outcome-decomposition.md)): `fedcourts
provision-blinded-predictions` stages each predictor's latest prediction under an
opaque alias with its identity masked, and `fedcourts unblind-evaluations`
renames the evaluator's alias-keyed output back onto the real predictor ids. The
staging area lives under the case's gitignored `record/`, so it rides the cell
artifact and never reaches the ledger.

A second pair of steps keeps the aliases worth having. The committed `predictions/` and
`evaluations/` trees name every predictor one directory above the staging area,
so a routine `ls` de-blinds a judge before it has read the contract that forbids
that tree; `fedcourts hide-cell-record` moves both out of the working tree after
the staging step and `fedcourts restore-cell-record` moves them back the moment
the agent stops, ahead of every step that reads them. It narrows the accidental
route only — the checkout carries full history — and nothing a cell hides or
fails to restore can reach the run PR as a deletion: the collect job unions each
cell's `data/` onto a freshly fetched clean `origin/main` checkout, and
`assert-paths` rejects any non-addition.

**The un-aliasing runs before the stamp, and the ordering is load-bearing.**
`stamp-cell --role evaluator` joins each evaluation to the prediction it scored
on the `predictor_id` field; under an alias the join misses and the cell's
`claim_scores` block is *silently* absent rather than wrong (so is
`base_rate_salience_version`, unless the evaluation records a `risk_set` basis,
which fails the stamp instead, and so is an interim cell's harness-stamped
`segment_base_rate`, which reads the application Term off that same
prediction). `validate`'s
evaluation-target check resolves the same join and does fail loudly, so it is the
backstop rather than the detector. The cell's order is therefore: blind → hide
the committed trees → agent → restore them → capture usage → capture retrieval
log → **un-alias** → stamp → validate.
Wiring the un-aliasing and the stamp anywhere else in that sequence produces a
run that looks green and quietly drops a scoring block.

How a cell's output becomes a PR is the same across **`run:predict`** and
**`run:evaluate`**: each cell validates its own output and
uploads it (plus a status file) as an artifact rather than opening a PR, and a
final **`collect`** job unions the run's artifacts into **one PR** — auto-merged
once `gate` + `paths` are green, and closing the triggering issue on merge — with
any salvageable partial output split into a single companion **draft** PR. So a
fan-out of dozens of cells yields one (or two) PRs for the run, not one per cell.
The append-only `data/` path jail (`fedcourts assert-paths`) is enforced in
`collect` before the commit and again as the required `paths` check, so an
auto-merged PR can only add artifacts under `data/`; a schema re-validation and a
secret scan (`fedcourts scan-diff-for-secrets`) run beside it producer-side —
a validation failure downgrades the PR to a draft, while a secret-scan hit
**withholds the branch entirely** (nothing pushed; a redacted report lands on
the trigger issue) since the push itself would publish the secret (see
[security.md](security.md)).

For `run:predict` and `run:evaluate`, `collect` also rolls up any
agent feedback (`flags.json`) the run surfaced and posts it three ways — each
gated on the run's secret scan, since flag messages are agent free text — the run PR
body, the Actions summary, and one long-lived **agent-feedback** tracking issue (the
single latched-issue pattern of `ops-dashboard` / `data-validation` / `pipeline-health`) — so a note
reaches a durable, centralized home even when a fully-failed run opens no PR.
It also reads the run's own harness-captured `retrieval_log.json` files and, if
any cell's manifest-tool results came back rate-limited, warns in the same PR
body that the shared upstream quota starved this run's retrieval — how many
legible results were throttled, across how many cells, and how many further
cells captured nothing and could not be observed either way. Where *no* cell
could have shown a throttle it says that instead, because capture-blind and
throttle-free must not read alike; a genuinely clean run prints nothing. The
note is harness-rendered from the logs rather than agent free text, so it rides
even the facts-only PR of a wholesale-failed run, where starvation is a live
candidate cause. It is the only per-run record there is: the 429 payload itself
is digested away at capture, so without the marker a starved run and a well-fed
one look identical afterwards.

The same walk asks the corpus-side version of that question and writes a second
harness-rendered note beside it: which cells ran a `fedcourts` corpus query
(`query` / `open-events`) and reported not having used the corpus. A query that
times out against the corpus index fails no cell — it finishes and predicts from
whatever else it had — so without a run-level count the only trace is one line
in one cell's report. What the note prints is a **disagreement between two
channels, not a diagnosis**: the *attempt* is harness-captured (a row in the
cell's own log that a command could have been run from — a shell call, or one
lifted out of a code-mode program's source — screened so a `--help` or a `grep`
of the CLI's name is not read as a query, since declining to use a tool is not
the tool failing), while the *service* is the cell's own `tooling.json` line. A
failed query leaves that shape and is the reason it is worth printing, but so
does a cell that queried, got rows, and answered the field on another reading —
and on a code-mode cell so does a call site in a branch the program never took,
since the attempt there is read out of program *text* rather than observed
running. The rows separate none of them, so the note names its cells
(`case/event/actor`, walk order) for a reader to check rather than asserting a
cause. Its denominator
is the cells whose attempt was **legible**, printed against the run's legible
cell logs, because what capture can read of a cell's commands differs by engine
— a code-mode cell's are visible only as far as the lift matched its program —
which is also why the counts are not comparable across engines, nor across runs
whenever capture itself has moved between them. Like the throttle note that
warning stays silent where every attempt was served, and rides whichever PR the
run opens. A cell whose answer cannot be read at all gets its own line rather
than the warning's, because unknown and starved are different claims.

A **capture tripwire** prints beside those two — and, unlike them, *also on a
fully-served run*, since it reports on what could be seen rather than on what
happened, and an unseen attempt is least suspected exactly where nothing looks
wrong. It carries its own denominator: cells that called the freeform `exec`
builtin with no **manifest** calls lifted out of its source, over the cells that
called it at all. Three readings, none separable from the rows — the program
called no manifest tool worth a row, the lift no longer matches the engine's
manifest calling idiom, or the call was an ordinary shell call spelled the same
way (the parser tells those apart by the transcript item's type, which no row
records). It watches the manifest half because capture lifts two idioms out of a
program and each fails on its own: builtin call sites outnumber manifest ones
several times over, so a tripwire that counted them would go quiet exactly where
the manifest spelling drifted. The attempt counts above do read such a cell,
through the other half: a command run from inside a program is lifted into a
row naming the *builtin*, and a lifted row counts where it carries the lift
marker (`call_source` in
[predicted-artifacts.md](predicted-artifacts.md)) **and** names one of the two
builtins that run a command — the patch and plan builtins are lifted too, and
their argument text is prose the program wrote, so a plan step naming the
command would otherwise be counted as the invocation it describes. That path is
additional to the shell one, not a replacement: the code-mode parent row is
itself shell-classed, so a command inside its truncated head slice still counts
on its own. The two halves therefore watch different idioms, which is why the
tripwire is **correlated with** the attempt counts' coverage rather than a bound
on it — a drift on the builtin side would empty those counts for every code-mode
cell while this ratio stayed silent, and only the capture rate climbing back
toward 1.0 would show it. The ratio is there because this is a standing
condition rather than a per-run event.

The `run-seed` historical walker has its own instance of the latched-issue
pattern: a `guard`
job raises one long-lived **pipeline-health** issue if the checkpointed walk is
ever cancelled or fails (e.g. a chunk overran the job's hard timeout), and clears
it when a later walk finishes clean — so a silent, PR-less writer failure still
reaches a durable home.
Separately, every cell may also write a `tooling.json` self-report on its
environment/tooling, committed with the cell's output; only its
`used_corpus_query` line is read per run (it is the served side of the
prior-availability note above), while the report as a whole is scanned across
runs by the `run-ops` dashboard into a tooling-feedback digest. See the
`flags.json` and `tooling.json` channels in
[data-pipeline.md](data-pipeline.md).

To trigger prediction/evaluation for **one** case, open an issue whose body
contains a single object and apply `run:predict` (or `run:evaluate`). For
evaluate this is the manual path — a deliberate one-off over cases you picked;
the lane's normal round is the schedule, which names no cases because it derives
them:

    ```json
    {"court": "ca9", "docket": 64512345, "events": ["evt-motion-stay"]}
    ```

To trigger **many** cases from one issue (e.g. a whole SCOTUS long-conference
list of petitions), use a JSON array of the same objects:

    ```json
    [
      {"court": "scotus", "docket": 24001, "events": ["evt-petition-cert"]},
      {"court": "scotus", "docket": 24002, "events": ["evt-petition-cert"]}
    ]
    ```

`events` is optional per case: omit it (or pass `[]`) to target the case's
default events — its **open** events for `run:predict`, its **resolved** events
for `run:evaluate`, so already-resolved events are skipped. Every listed case is
multiplied by the registry and its events to produce one matrix cell per
predictor/evaluator × case × event — which `run:predict` and `run:evaluate`
collect into one PR for the run.

`predictors` is also optional per case and narrows the `run:predict` fan-out to
the named registry ids:

    ```json
    {"court": "scotus", "docket": 24001, "predictors": ["codex-baseline"]}
    ```

This is the **engine backfill** path: when one engine's cells failed (a quota
or provider outage) while the others delivered, it names the engines a re-fire
targets. It is not what stops the healthy engines re-running — the plan's
already-predicted gate is per `(predictor, event)` in its own right
(`event_has_predictions(predictor_id=...)` in `matrix.py`, the same grain the
live channel's selection sweep uses), so a re-fire of the full registry drops
every engine that already committed a prediction for the event and mints only
the missing ones. `predictors` **narrows** the fan-out; it does not deduplicate
it — what it buys a backfill is a plan (and a cost) confined to the engines
asked for. Naming an id that is not an enabled predictor fails the plan job
rather than silently skipping the engine. `run:evaluate` ignores the field: an
evaluator always scores every committed prediction for its event.

## Unrecorded outcomes: what pull's outcome detection leaves behind

`run-pull` records `outcome.json` itself only when a decided docket is
unambiguous (a machine-readable disposition, a decision date, and a single open
event). Everything else — an unreadable/absent disposition, no decision date, or
a case-level disposition that cannot be attributed across several open events —
becomes an **unrecorded outcome** (it does not guess): the case lands on the
runner-local unrecorded queue (`unrecorded-queue.json`, the `UnrecordedOutcome`
detection in the library) instead of the git ledger. No issue is filed for
these. Both the pull and live jobs surface each one per-case on the pipeline-runs
dashboard's triage list ("court/docket — reason"), with the count on
the Actions step summary, for maintainer triage — recording nothing beats a
guess.

## A corrected outcome: re-grading the event's evaluations

Correcting a committed `outcome.json` — a disposition relabelled, a judgment
fixed — leaves every evaluation that graded against the old one carrying a
stale `correct`, claim block, and skill record, and `correct` is the
leaderboard's first rank key. The remedy is `fedcourts stamp-cell --regrade`
over **every evaluator on the event**: it recomputes exactly the harness-owned
fields and preserves each record's existing process stamp, because a correction
changes the record's inputs and not the process that judged it. Read
[process-version.md](process-version.md) before running it; the trade (no
`superseded_gradings` trace, so `data/`'s git history is the only record that
the numbers moved) is in [metrics/README.md](../metrics/README.md).

This is a *recompute*, not the re-grade the leaderboard's collapse counts. A
changed rubric or prompt wants the other route — a fresh evaluator run minting
a second `evaluation.json`, which is what `evaluate-matrix --force` re-mints —
and that route is wrong for a corrected outcome, which produced no second
judgment to record.

**Who runs it.** The edited files land under `data/`, so the same ownership as
every other data mutation applies: a dev checkout can run the command and read
the resulting working-tree diff, but nothing it writes can reach `main` — the
commit credentials live only in the writer lane's jobs, and a re-grade is not a
promotion-batch change. That route is `run-repair`'s `regrade-stale` pass, which
executes the command for each named cell and commits the changed
`evaluation.json` files. An agent that finds the correction composes the
dispatch and leaves it where the maintainer will see it (`gh workflow run` is
refused for a session token) — one line per judge in `repair_target`:

```bash
gh workflow run run-repair.yml --ref main \
  -f repair=regrade-stale -f repair_mode=dry-run \
  -f repair_target='scotus/1119228/evt-petition-certiorari/20260624T103000Z/claude-judge
scotus/1119228/evt-petition-certiorari/20260624T103000Z/codex-judge'
```

The `dry-run` echoes each `stamp-cell` command it would run; re-dispatch with
`repair_mode=apply` to write. Two disciplines the runbook
carries rather than the code: re-grade the whole event, or `validate`'s
`evaluation_correct_agrees` fails the ledger on the half-corrected state; and
re-grade a whole cohort against one committed statpack, since the recomputed
pools are read at re-grade time.

## Recovering a run whose `collect` failed

`collect` is the single writer for a run's agent output, so an all-or-nothing
failure would discard the whole run — one transient artifact download can carry
dozens of successful cells with it. It therefore degrades per artifact, and
what it could not collect is named rather than silently dropped. Three gaps,
three remedies:

| the PR body / run log says | what happened | fix |
|---|---|---|
| *artifact did not transfer* | the cell likely succeeded; its output still exists | **re-run the `collect` job** |
| *no cell output at all* | the cell died before it could report | **re-queue** — no rerun helps |
| *secret scan did not pass; withholding &lt;branch&gt;* (log), with a redacted report on the trigger issue — or on the run's step summary, for a round that has no issue | that branch was withheld — its cells' output sits only in the run's cell artifacts | **review the flagged content, then salvage by hand or accept a re-spend** — see below |

A secret-scan withhold starts with a judgment call the other two rows do not
need. Locate the flagged content first: the scan runs per PR kind, so a hit
withholds only the branch it fired on (the ready branch can merge while the
draft is withheld, or the reverse), and its report names file and line but
never the match. A finding in a cell's file is reviewable in that cell's
artifact; a finding in the rendered `pr-body.md` or `run-flags.md` points
back at the cells' `flags.json` free text, which the roll-up quotes; and the
*misconfigured-scan* report is its own case — nothing was judged, so repair
the configuration rather than reviewing content. Read the reported line
*locally, without quoting it anywhere*. A real secret means the output must
not be collected: delete the run's cell artifacts (`gh api -X DELETE
repos/<owner>/<repo>/actions/artifacts/<artifact_id>`) and rotate whatever
leaked. A false positive cannot be released by re-running `collect`: a re-run
executes the ref the run was dispatched at — the scanner it ran included —
so it re-trips the same rule regardless of what has landed since. The
remedies are to **salvage by hand** — extract each withheld cell's run-scoped
output from the artifacts into a data PR before the artifacts' 7-day
retention lapses (the maintainer merges it, like every non-collect merge to
`main`), then close the trigger issue yourself, since only a merged collect
PR auto-closes it — or to **re-queue and accept the re-spend**. No
stranded-run guard covers a withheld run in either role: the withhold leaves
`collect` concluding success, which the predict census reads as collected,
so a re-applied label re-spends every cell the withheld run already paid for.

The first two gaps keep the trigger issue open, so an issue-triggered run never
auto-merges presenting itself as complete while omitting cells; a withheld ready
branch keeps it open the same way, while a hit confined to the draft or the flag
roll-up leaves the ready PR to merge and close it — check the run log before
trusting a closed issue as evidence the whole run landed. A scheduled evaluate
round has no issue to hold open, and needs none: its omitted cells are still
ungraded, so the next derivation finds them again. That is the property to lean
on there — not a closed issue, which for that lane never existed.

A **wholesale-failed run** — every cell died, so no ready or partial PR opens —
still records one `attempt.json` fact per failed cell via a small auto-merging
**facts-only PR** (`<role>/run-<run_id>-facts`, no `Closes #`, so the trigger
stays open for the re-queue). That is what lets the per-cell attempt cap advance
for a persistently-failing cell even when the run itself produced nothing.

**Re-running collect is safe and repeatable.** `gh run rerun --failed`
re-executes only the failed job; the artifact listing is per-run, so it re-lists
and re-fetches the original attempt's uploads. The loop force-pushes its
run-scoped branch, finds-or-updates the PR (reconciling draft state), and
marker-dedupes the trigger-issue reports, so nothing stacks or aborts on a
second pass. A kind whose PR already merged is skipped.

Three caveats:

- **Cell artifacts are retained 7 days.** After that a transfer-lost cell is
  gone and only a re-queue recovers it.
- **`--failed` also re-runs failed *cells*,** and `upload-artifact` rejects a
  duplicate artifact name within a run, so those re-run cells fail at upload.
  `--failed` is the recovery for a *collect-only* failure; when cells failed
  too, land `collect` first and let the re-queue pick the rest up.
- **On `run:predict`, collect first — a re-queue will not stand in for it.**
  The stranded-run guard above withholds every cell that uploaded an artifact to
  an uncollected run, so re-applying `run:predict` inside its 48-hour window
  queues nothing and closes the new trigger issue saying so. Rerun `collect`,
  which commits what the cells produced; the guard then releases that run, and
  any event still holding no prediction — including a cell that ran and
  delivered nothing — re-queues on a later cycle. That costs one round trip
  where re-queueing first would cost a whole fan-out's tokens to reach the same
  ledger.

A rerun discards hand-edits to an unmerged draft branch — it is rebuilt from the
artifacts. Finish a draft by merging it, not by editing and then re-running.

## Graceful degradation on limits

Agent steps (predict, evaluate) are bounded by a step-level
`timeout-minutes` set below the job's, so a run that overruns trips the *step* —
not the job. A step timeout (or a max-turns stop) fails only that step and leaves
the runner alive, so the salvage step still runs (`if: !cancelled()`) and the
agent's partial work survives instead of being discarded with the cancelled job.

What salvage looks like is uniform across **`run:predict`** and
**`run:evaluate`**: each cell records its status and uploads its output
(`if: !cancelled()`); the `collect` job then routes a cell that did not finish
cleanly — or whose output failed schema validation — into the run's **draft** PR
(never the auto-merging ready one), and a cell that produced nothing is warned
about rather than committed. A run that finished cleanly is
unaffected: the draft path only triggers when the agent stopped early.

## Pausing the tournament without pausing ingestion

`seed`/`pull`/`live` (cheap, API-budgeted) and `predict`/`evaluate` (the model
spend) can be run independently. The two fan-outs are held by different levers,
because only one of them has a handoff seam to hold:

| Channel | Lever | Effect |
|---|---|---|
| `run:predict` | `PREDICT_HANDOFF_ENABLED` = `0`/`false` | the pull window files no `run:predict` issue |
| `run:evaluate` | disable the `run-evaluate` workflow | every trigger stops — schedule, dispatch and label alike; no round is planned |

Set the variable in the `prod` environment (a repository-level variable of the
same name works identically, unless an environment-level one shadows it). It
defaults to filing, so an unset or mistyped variable keeps the tournament
running: the failure that costs coverage is the quiet one. Ingestion is
untouched — the corpus keeps refreshing and outcomes keep being recorded, so a
pause costs prediction/grading coverage for that window, never data. A full
tournament pause needs both levers, and neither implies the other.

Evaluate has no handoff variable because it takes no handoff: nothing files it a
trigger issue, so there is nothing to withhold. What stands in for one is the
disable — and, per-round, the `review` hold, which can decline a planned round
without stopping the lane. Both are lossless for the same reason the predict
pause is: the backlog is a condition on committed state, re-derived from scratch
on the next cycle.

**Holding predict is lossless, and resuming needs no backfill.** The predict
queue lives in the corpus, not in the issue — the issue is only a trigger
carrying a snapshot of it. A **selected** case stays queueable for as long as any
enabled predictor still *owes* an open event, and the live channel's selection
sweep re-polls that set each cycle — plus the cohort-completion candidates
below (`pipeline/live.py`, gated per
`(predictor, event)` on `event_has_predictions(predictor_id=...)` from
`matrix.py`), debounced to daily by `predict_queued_at`. Owed is per cell, so a
case where two of three engines committed a prediction and one quota-failed is
still swept for the missing engine — the same grain the `predict-matrix` plan
gate uses to re-mint only the not-yet-predicted engines. So a held window never
needs its issue re-filed or re-opened.

The drain is paced, not instant: the sweep is capped at
`salience.sweep_cases_per_cycle` (25 in `config/tracking.yaml`) and works stalest
first, so a backlog larger than the cap spreads over the following cycles — the
same behaviour [salience.md](salience.md) describes. A case **latched out of
scope** (`predict_excluded`) is never re-queued at all. A case that is merely
**unselected** re-enters the sweep on two grounds — the merits bypass (the Court
granted it, so the cert funding question no longer applies) and **cohort
completion**: an event of it already carries a committed prediction, that cohort
is one a claimable board will count once the event resolves and is graded, and some enabled engine is missing from it, so
the sweep re-admits the case and queues *only those events*. Selection decides
which petitions earn a forecast, and a case selected when its run fired can drift
below the line before every engine landed, leaving a partial cohort with no path
back — the distribution transition has already passed and the funding gate
refuses it. Finishing that cohort buys the missing engines on a case the project
already paid to predict. The narrowing carries two bounds on that ground: queueing
the case's *other* open events would buy new cells on a case the gate declined,
and completing an event whose cohort sits wholly outside the frozen process scope
would hand the board an event scored on the completing engine alone. A deferred
case the ledger holds nothing for is not even a candidate. What a number off a
completed cohort does and does not support is in
[salience.md](salience.md). The per-cell owed check also
honors `predict.max_attempts_per_cell` via the ledger-derived failure facts
(described below for evaluate), so one `(predictor, event)` cell that fails every
attempt cannot re-queue forever while a sibling engine still owed the same event
is swept normally.

Held windows are marked **held** on the pipeline-runs dashboard row, the run
log, and the step summary rather than reported as dispatched, so a growing
backlog is legible as a paused channel and not misread as a stalled fan-out.

### The evaluate queue is level-triggered too

Resolution latches closed: `upsert_events` never re-emits an event a poll already
reported as resolved. So an evaluate round that fails, is declined, or never runs
cannot be recovered by waiting for the resolution to come round again — the corpus
push and the outcome commit both landed already, and the outcomes and predictions
would sit there with nothing left to grade them.

The **evaluate backlog deriver** (`pipeline.pull.derive_evaluate_backlog`) is what
makes that impossible. It asks a question about committed state — which resolved
events have a prediction and are missing at least one enabled evaluator's
evaluation — so the answer reconstructs itself from the ledger every time it is
asked, and a lost round is simply re-derived.

Two callers ask it, with different authority (see [cli.md](cli.md) for the
command-level contract):

- **`run-evaluate`'s own schedule**, at plan time, is what the fan-out actually
  runs on: `evaluate-matrix` with no `--body-file` derives the backlog and fans
  out over it. It reads only — the corpus of record is writable from the writer
  jobs alone — so it writes no `evaluate_queued_at` stamp and needs none. The
  plan's already-graded gate is the idempotency: re-deriving an unchanged backlog
  re-mints nothing once the gradings are committed, while a cell that was *not*
  graded is work still owed and should re-mint.
- **Each `pull-all` / `live-poll` cycle**, whose `pipeline.pull.evaluate_backlog`
  appends the derived cases to the same evaluate queue the fresh-resolution path
  feeds and reports the queue's size on the run log. It files no trigger issue
  and writes no `evaluate_queued_at` stamp: the scheduled lane holds off a case
  stamped today, and it is the only actor that grades what this scan finds, so
  a pull-window stamp (five of the eight daily windows precede the evaluate
  slot) would rotate owed gradings away from the one lane that can clear them.

It mirrors the predict selection sweep, with one deliberate difference and one
deliberate similarity:

- **Different:** it is purely local (git ledger + corpus, no network), so its
  `evaluate.backlog_cases_per_cycle` cap bounds model spend and PR volume, not
  request rate. On the scheduled lane that cap and the cron's cadence are the
  whole of the pacing.
- **Same:** the `evaluate_queued_at` corpus column keeps the sweep's ordering
  semantics — stalest stamp first, a case stamped today held to tomorrow. No
  standing lane writes it: the scheduled lane is read-only and the pull lane
  deliberately leaves it alone, so the hold is vacuous in practice and the
  deriver orders on a key it never advances (rows never stamped sort by case
  id). The trade is deliberate: above the per-cycle cap the ordering no longer
  rotates, so a stuck head — planned but never graded, recording no failure
  fact — is cleared only by a grading landing or the per-cell attempt cap,
  where the retired stamp would have rotated past it (and, worse, past every
  owed case daily). That column is scheduling metadata — the backlog itself is
  re-derivable from git — so losing it costs at most a duplicate round, never a
  grading.

Because the gate reads *committed* state, it cannot see a round whose collect PR
has not merged. What keeps a second derivation out of that window is
`run-evaluate`'s concurrency group, which serializes every round of the workflow
regardless of trigger — not the gate.

The cron's cadence and `backlog_cases_per_cycle` pace re-queuing but have no
ceiling, so a cell that fails *every* attempt (a persistent quota wall, a
malformed record) would re-queue forever. The **ledger-derived failure facts** are the backstop: the corpus-blind
`collect` job writes one committed `attempt.json` per failed cell into the git
ledger, and the deriver counts them (`matrix.cell_failure_count`). Once a cell
reaches the `evaluate.max_attempts_per_cell` cap the deriver stops re-deriving it.
The count keys on **cell identity** (actor + event at a seam), not process
version, so a cell retried under a newer version still counts against the same
cap; and it is keyed per (evaluator, event), so one exhausted cell never
suppresses a sibling evaluator still owed the same event. The facts live in the
git ledger, not the corpus, so ingestion never touches them; a wholesale run
failure that opens no PR commits no facts (that tail is left to the loud stall
comment) — losing a would-be fact costs at most a duplicate trigger, never a
grading.

Re-queueing costs nothing but latency: the scoring surfaces count one grading per
(case, event, predictor, evaluator) — newest by harness clock — so a re-queued
grading supersedes rather than double-counts (a fresh `evaluation.json` the
collapse counts, not the in-place recompute a `regrade-stale` repair dispatches), and the
`evaluate-matrix` plan gate drops a
cell whose judge has already graded the event (per evaluator) so a re-derivation
spends model tokens only on the *missing* judges. The gate works at (evaluator,
event) grain, which carries one accepted limitation: a prediction committed
*after* a judge graded the event is not re-scored by that judge. What the coarse
grain buys is the spend, and what it costs is a coverage gap that falls
differentially — an engine whose cells backfill late accumulates fewer scored
events than one that ran on time. The leaderboard publishes that gap rather than
leaving it to a ledger scan: every entry carries its own `events_scored` against
the board's union, and `fedcourts leaderboard` warns when they are unequal
(`metrics/README.md`).

Pausing evaluate costs latency alone, for the same reason: a cycle that never
ran re-derives on the next tick rather than being lost. Its lever is the
workflow disable rather than a handoff variable (see *Pausing the tournament*
above), and a full pause of both channels needs each channel's own.

### Disabling the workflow is not the same as holding the handoff

For **predict**, disabling `run-predict` in the GitHub UI stops the *runs* but
not the *issues*. The issues keep arriving and sit unconsumed — and `run-ops`
lists every still-open `run:*` issue as a **stalled fan-out**, so a
workflow-disabled-only pause steadily reddens the ops dashboard with what looks
like broken runs. Holding the handoff avoids that; for a full pause, hold the
handoff *and* disable the workflow.

For **evaluate** the pipeline files no issue, so disabling `run-evaluate` leaves
its scheduled rounds nothing to strand — the disable is the pause, and the
backlog waits. The label path is the exception that survives: a hand-labelled
`run:evaluate` issue filed against the disabled workflow does sit unconsumed, and
`run-ops` still lists `run:evaluate` among its trigger labels, so it reads as a
stalled fan-out exactly as a predict issue would. Do not file one while the
workflow is disabled.

### Recovering from a manual disable

A workflow paused with a disable (`disabled_manually` in `gh workflow list
--all` — the bare listing hides disabled workflows, and the ops dashboard
gives the state no distinct marker, so the `--all` listing is the one
surface that shows it) comes back in a fixed order, because the label
step's mechanics are silent about what they drop:

1. **Re-enable first — the maintainer's act.** `gh workflow enable
   <workflow>` (or the Actions UI); an interactive session's token is refused
   on it, like every workflow-administration call, so an agent session
   composes the command and continues with what does not depend on it. An
   enabled workflow with the handoff still held creates nothing, so this
   order has no window in which events fire into a disabled workflow.
2. **Then restore the handoff, if it was held** — variable administration,
   on the same maintainer-only list. Predict only: a full predict pause holds
   the handoff *and* disables the workflow (above), and restoring the handoff
   while the workflow is still disabled would file trigger issues whose label
   events are dropped, manufacturing exactly the re-label work of the next
   step. Evaluate has no handoff to restore, and step 3 does not apply to it
   either — its next scheduled tick resumes the lane on its own, and
   `workflow_dispatch` runs one immediately if the wait is too long.
3. **Re-apply the `run:*` label on each trigger issue that should now run.**
   Label events fired while the workflow was disabled were dropped, and an
   already-applied label fires no event (both GitHub's own event mechanics,
   like the handoff-token gotcha above), so re-enabling alone resumes
   nothing: remove the label where it is still applied, then re-apply it —
   the re-apply is the trigger, and a run still queued or held from before
   the pause serializes ahead of it under the per-issue concurrency group.
   Three outcomes of the re-label are the machinery working, not the
   recovery failing: with cells sitting in an uncollected run's artifacts,
   the stranded-run guard withholds them for its 48-hour window and the
   re-label closes the trigger issue saying so (*Recovering a run whose
   `collect` failed*, above); a label re-applied after a secret-scan
   withhold re-spends every cell the withheld run already paid for (same
   section); and a queued event that resolved during the pause closes as
   out of scope — the forecastability re-check working across the gap.
4. **The hold, not the enable, is still the spend gate.** A re-applied label —
   or an evaluate round resuming on its schedule — starts at the plan job,
   which renders a fresh plan report, and the matrix waits behind the approval
   job on the `review` environment's required reviewers. So a recovery cannot
   leak spend past the hold, and the fresh plan re-anchors the already-predicted
   gate and the stranded-run guard exactly as the review-hold rules above
   require of a re-queue.

## Snapshot sequencing

`run-pull` pushes factual snapshots **to the corpus** — the per-case content
store plus the `corpus-push` of the index — before it queues `run:predict`, so
`run-predict` — a read-only corpus consumer (its plan job reads the index in
place over the ranged backend; its cells provision from the content store and
query the index through the credential-holding corpus sidecar) — sees the
snapshot it must predict from. Raw facts never go through PRs (they are
CourtListener data, not agent output); agent outputs (predictions, evaluations)
always do.
