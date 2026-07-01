# Data pipeline: seed & pull

How case data enters and stays current in `fedcourtsai`. This is the design
contract for the **seed** (historical backfill) and **pull** (forward freshness)
phases. For the label/workflow mechanics see [pipeline.md](pipeline.md); for the
on-disk shapes see [data-model.md](data-model.md).

## Scope

Two different scopes apply, and keeping them apart is what bounds the bill:

- **Ingestion scope — the full set.** Seed and pull assemble the **Supreme Court
  and all 13 federal courts of appeals**:

  ```
  scotus  ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11  cadc  cafc
  ```

  District courts are intentionally **out of scope** for now. Ingestion is
  deterministic script work — bulk seed spends no API budget, pull is bounded by the
  CourtListener throttle — so it is cheap relative to the agentic stages. The whole
  corpus is assembled precisely so predict/evaluate can **query the full history**
  for retrieval and back-testing, even for cases they never predict.
- **Prediction scope — the SCOTUS-interaction gate (pilot).** The agentic
  predict/evaluate stages cost one to two orders of magnitude more than ingestion
  (see [budget.md](budget.md)), so in the pilot they run on a deliberate subset: a
  case becomes **in-scope for prediction the first time it interacts with the Supreme
  Court** — a petition for certiorari is the canonical trigger — and **stays in-scope
  for the remainder of its lifecycle**. So a gated case's later merits events, and any
  remand activity back in the courts of appeals, are predicted, while the ~42K/yr
  appeals cases that never reach SCOTUS are ingested but not predicted. The gate
  latches once and never clears; widening it beyond SCOTUS-touched cases is a later,
  cost-data-driven decision ([milestones.md](milestones.md)). One narrowing rides on
  top of the latch: a **pre-1925 mandatory-jurisdiction matter** (detected by its
  bare, non-Term-prefixed docket number, e.g. `801`) is dropped from the
  predict/evaluate set — its `evt-petition-disposition` carries a merits, not a
  discretionary-cert, meaning, so the modern event model does not fit it
  (`corpus.is_historical_mandatory`). Ingestion still covers it; only prediction
  is gated. Three sibling narrowings drop other cases the modern cert model cannot
  score: a **stale, still-open petition** from a long-past October Term
  (`corpus.is_stale_unresolvable`); one whose only outcome signal is a **published
  opinion with no machine-readable disposition** — decided, but the outcome lives
  only in the opinion text and is a merits, not a cert, label
  (`corpus.is_published_opinion_unresolvable`); and a court-agnostic guard for a case
  with **internally inconsistent dates** (`corpus.is_date_inconsistent`). Each gates
  prediction only, never ingestion, and the two-directional scope reconcile releases
  any case that later gains a real disposition.

  Because the corpus keys a case by `<court>/<docket>`, the *same real-world case's*
  SCOTUS docket and originating court-of-appeals docket are **separate rows**. Both
  belong in scope, so when a SCOTUS docket is ingested carrying a lower-court link
  (CourtListener `appeal_from` + `originating_court_information.docket_number`, stored
  as the `originating_court` / `originating_docket_number` corpus columns), the
  ingestion seam latches the matching *tracked* CoA docket eligible too — joining on
  court id + normalized docket-number string. The REST (pull) path carries that docket
  number; the bulk (seed) path does not (CourtListener publishes no
  originating-court-information bulk table), so it fills only the originating court and
  the precise latch is pull-driven. The match is a conservative exact one — an
  unlinked or untracked SCOTUS docket is a harmless no-op — and, like the SCOTUS latch
  itself, forward-only.

## The binding constraint: the CourtListener API budget

CourtListener's authenticated REST throttle is **5 requests/minute, 50/hour,
125/day** — concurrent limits, most-restrictive-wins (enforced locally by
`courtlistener/ratelimit.py`). Higher limits require Free Law Project membership
or a commercial agreement. At roughly **3 requests per docket** (1 docket + ~2
pages of entries) the token can touch **~30 dockets/day**.

That cap makes one thing non-negotiable: **the REST API cannot load history.**
The backlog is millions of dockets across 13 circuits; at ~30/day that is
decades. So the two phases use two different sources:

| Phase    | Source                              | Spends API budget? |
|----------|-------------------------------------|--------------------|
| **seed** | CourtListener **bulk data** (S3 CSV) | No (~0)            |
| **pull** | CourtListener **REST API**           | Yes — owns it      |

CourtListener publishes **free quarterly bulk-data snapshots** (dockets, opinion
clusters, opinions, citations, courts) to a public S3 bucket, regenerated on the
last day of March/June/September/December. That is the right source for the
historical mass, and it bypasses the throttle entirely.

## Two processes, one shared core

Seed and pull are **separate workflows** because they differ on every axis that
matters — source, lifecycle, budget ownership, reporting, and steady-state
cadence:

| Axis            | seed (backfill)                         | pull (forward)                    |
|-----------------|-----------------------------------------|-----------------------------------|
| Source          | bulk S3 CSV                             | REST API                          |
| Lifecycle       | finite — chunked **until complete**     | perpetual — runs daily forever    |
| Budget          | ~0 API                                  | owns the 125/day budget           |
| Reporting       | long-lived `run:seed` issue, closed by a completion PR | short-lived `pull-log` issue per run |
| Steady state    | drops to **quarterly** reconciliation   | stays **daily**                   |

They share an **ingestion core** (`fedcourtsai.pipeline.ingest`: a normalization
layer where an API docket JSON and a bulk CSV row both become the same normalized
row, then upsert into the packed corpus in `fedcourtsai.corpus`), shared
dedup/cursor utilities, and shared PR plumbing. **Unify the
library and the data, not the job.** Both ends write the same corpus, in the same
format, through the same APIs; keeping the jobs separate only keeps the budget
boundary crisp (pull owns the token; seed never touches it) and operational status
legible.

```
                shared core (pipeline ingest + store + serialize)
   API docket JSON ─┐
   bulk CSV row    ─┴─►  one normalized corpus row
   ┌───────────────────────┐
   │ SEED (weekly→quarterly)│ bulk S3 ─► packed corpus (DVC) ─► back-testing, retrieval
   │  no agent, no budget   │ cursor + run:seed tracking issue
   └───────────────────────┘
   ┌───────────────────────┐
   │ PULL (daily, forever)  │ REST API (per-tier daily governor)
   │  refresh + discover    │ ─► same packed corpus (DVC): fresh facts + snapshots
   │  + outcome detect      │ ─► outcome.json + run:predict handoff in the git ledger
   └───────────────────────┘
```

## Storage: one corpus, one ledger

Raw facts and derived judgments have different shapes and lifetimes, so they live
in different stores — but the split is by **kind**, not by phase. Both seed and
pull write the *same* corpus through the *same* ingestion core:

1. **Raw facts → the corpus.** Dockets, snapshots, judges, case metadata and
   tracking state, and event definitions go into a **packed, queryable store** —
   a single **SQLite** database, `corpus/corpus.db` — versioned with **DVC** (the
   blob in the DVC remote, the `corpus.db.dvc` pointer + load cursor in git). One
   format, written identically whether a row comes from bulk CSV (seed) or the
   REST API (pull) through the shared ingestion seam in `fedcourtsai.corpus`. DVC
   also versions pipeline **metrics** (`metrics/`, registered in `dvc.yaml`):
   back-test results and leaderboards.
2. **Derived judgments → git.** Outcomes, predictions, evaluations, and their
   reasoning are tiny, critical, and worth reading in a diff, so they stay in
   plain git under `data/`, where the schema/`validate`/PR-review machinery
   applies. See [data-model.md](data-model.md).

The rule is **pack, don't proliferate**: millions of per-case files would choke
`git` even under LFS (one tree entry per pointer), so all facts — historical and
fresh alike — go into a handful of large artifacts in one shared format. Keeping
both ends of the pipeline on the same structures, schema, and APIs is the point:
seed and pull differ on *source* and *budget*, not on how a fact is shaped or
stored. The reasoning stays readable text in git because that diff is the
explainability trail a reviewer actually reads.

### Credentials for the DVC remote

The DVC remote is a **private S3 bucket** the maintainer provisions out of band —
distinct from the *public* CourtListener bulk-data S3 that **seed** reads from.
Workflows authenticate with **GitHub OIDC**, not static keys: each job that
touches the remote runs `aws-actions/configure-aws-credentials` (pinned to a
commit SHA) to assume an IAM role, reading the role ARN and region from the
`runner` environment. The committed `.dvc/config` holds **no credentials and no
bucket URL** — it only names the default remote (`storage`); the URL is supplied
out of band into the gitignored `.dvc/config.local` (`dvc remote add --local -d
storage …`) before any push/pull. See [SECURITY.md](../SECURITY.md).

Access mirrors each workflow's role in the pipeline:

| Workflow                                  | Role / access | Why                              |
|-------------------------------------------|---------------|----------------------------------|
| `run-seed`, `run-pull`                    | read-write    | corpus writers (`dvc push`)      |
| `run-predict`, `run-evaluate`, `run-reconcile` | read-only | retrieval consumers (`dvc pull`) |
| `ci`                                      | none          | gate stays offline/fast          |

The gate has no remote, so it cannot diff the corpus blob against S3; it runs the
offline half instead. `fedcourts dvc-status` checks that the committed DVC
bookkeeping is internally coherent — every DVC-tracked data output (the
`corpus/corpus.db.dvc` pointer, any cached stage output) is a well-formed pointer
that is gitignored and absent from git, so the corpus blob can never slip into the
repo, and every `cache: false` pipeline output (the `metrics/` roll-ups) is
committed. The online `dvc status` against the remote stays with the corpus-writer
workflows that hold the credentials.

**Two IAM roles, split by access.** Corpus writers (`AWS_ROLE_TO_ASSUME`) assume a
**read-write** role; retrieval consumers (`AWS_ROLE_TO_ASSUME_READONLY`) assume a
**read-only** role, so a compromised predict/evaluate/reconcile runner cannot write
or poison the corpus. The write role is **append-only** — get/put/list but **no
delete** — and the bucket has **versioning** on, so no run can wipe corpus objects
(no run garbage-collects the *remote* — `run-seed` prunes only its local runner
cache with `dvc gc --workspace`, never `--cloud`; remote pushes only ever add).
Both roles' OIDC trust is scoped to this repo's `runner` environment, so only
`runner`-environment jobs — never an arbitrary PR-branch job — can assume them. The
OIDC wiring (`permissions: id-token: write` + the credentials step) grants each job
its access without any long-lived key.

### Corpus-writer coordination

`corpus/corpus.db` is one mutable SQLite blob behind one DVC pointer
(`corpus/corpus.db.dvc`), and **two** workflows write it — `run-seed` (backfill /
reconcile) and `run-pull` (forward refresh + discovery). A blob has no merge, so
the pointer is last-writer-wins: if the two ran concurrently, or built on
divergent bases, the second commit would silently drop the other's rows. Two rules
prevent that:

- **One lock.** Both workflows share the `corpus-write` concurrency group
  (`cancel-in-progress: false`), so corpus writers never run simultaneously — a
  second run queues until the first finishes.
- **Both commit straight to the default branch.** Each run does `dvc pull → mutate
  → dvc add → dvc push → commit the pointer (+ cursor / outcomes)` and pushes
  directly. Serialized by the lock, every run pulls the latest committed pointer
  before mutating, so it always builds on its predecessor's writes. Neither writer
  goes through a long-lived PR whose stale base could revert the other on merge.
  If the default branch advanced for an unrelated reason between checkout and push
  (e.g. a `run:predict` / `run:evaluate` PR merged), the commit is rebased onto the
  new tip and the push retried — the lock means the pointer itself never conflicts,
  so this is a clean fast-forward, not a corpus merge.

### Corpus schema

Each corpus row is a normalized, **labeled** record so it serves both consumers:

```
case_id, court, docket_number, date_filed, date_decided,
disposition (outcome label), judges[], topic (nature/subject),
citations[], opinion_text, summary
# embedding[] — later upgrade for semantic retrieval
```

Carrying `disposition` makes the corpus a ready-made **back-testing** set, and
the structured columns make it **queryable** for retrieval. The schema is
defined and enforced in [`fedcourtsai.corpus`](../src/fedcourtsai/corpus.py)
(`CorpusRow` + the `cases` table); see [corpus/README.md](../corpus/README.md)
for the column reference. The SQLite format is internal — the stable contract
is the row schema, whose ids and `Disposition` vocabulary are shared with the
ledger models in `fedcourtsai.schemas`.

### Consumers of the historical corpus

- **Back-testing** — replay predictors against historical *resolved* events
  (outcome hidden at predict time), score against the known disposition. Run by
  `fedcourts backtest` (the `backtest` DVC stage), a deterministic offline replay
  that writes `metrics/backtest.json`; see [`fedcourtsai.backtest`](../src/fedcourtsai/backtest.py).
- **Retrieval** — at prediction time a model pulls a handful of *relevant*
  priors instead of loading the bulk set into context. Structured retrieval is
  implemented today as `fedcourts query` (and the `corpus.retrieve_priors`
  library API): exact-match filters on court / topic / disposition plus
  overlap filters on judges and citations, ranked by how much each prior shares
  and defaulting to resolved (labeled) cases. Procedural **posture** is not a
  case-level column — it is carried by a case's predictable-event `kind` — so it
  is not yet a query filter; semantic / embedding similarity lands on the same
  query seam once embeddings are stored.

The back-test harness scores each predictor on disposition accuracy, binary
granted accuracy, and the Brier score of P(granted). It runs over a
`Backtester` seam: two reference baselines (a constant floor and a
corpus-retrieval majority vote) run entirely offline so the metric is real
today, and the configured agentic predictors plug into the same seam and are
replayed out of band, exactly as `run-predict` runs them live.

The live predict/evaluate cells have the same shape of seam. A cell hands its
inputs — court, docket, event, the acting predictor/evaluator id, the run id,
the role, the prompt, and the output root — to a `Runner`
(`fedcourtsai.pipeline.runner`) that writes the cell's artifacts at the canonical
`ids`/`paths` locations. The workflow's runner is the coding agent
(`claude-code-action` / the Codex equivalent); an offline `stub` backend writes
deterministic, schema-valid canned artifacts with no model call and no network,
so the cell mechanics — provisioning paths, schema conformance, the
`validate`/consume path — are exercised in pytest without spending tokens or
running Actions. Wiring the live workflow onto the seam is separate; the stub is
the offline reference, mirroring the `Backtester` baselines above.

Those offline reference *engines* still read a corpus, which on a laptop would
need a `dvc pull` of the S3 remote behind OIDC. `fedcourts make-fixture-corpus`
removes that dependency: it builds a tiny, deterministic **synthetic** corpus
([`fedcourtsai.fixture`](../src/fedcourtsai/fixture.py)) — a handful of cases
across several courts, a mix of resolved and open, with their predictable events
and dated snapshots — so the read commands (`provision-snapshot`, `query`,
`open-events`) and the pytest suite run with no remote, token, or network. It is
the offline reference *data* under the engines above; it is never a substitute
for the real corpus the seed/pull workflows produce.

## Seed — historical backfill

- **Trigger:** a single long-lived `run:seed` tracking issue (a maintainer opens
  it and applies the `run:seed` label; see [seed-backfill.md](seed-backfill.md))
  plus a weekly schedule.
- **Each run** (deterministic, no agent, no API secret): read the committed
  **cursor** → process the next chunk of the bulk snapshot for the target courts
  → run the **event-definition stage** over each ingested docket so it carries its
  predictable event(s) (see below) → write/append the DVC corpus → commit the
  corpus pointer + cursor bump directly to the default branch (under the shared
  `corpus-write` lock — see Corpus-writer coordination) → **comment progress on the
  tracking issue** (per-court % and remaining).
- **Multi-table staged join:** each fact a corpus row carries lives in a different
  bulk file — the docket spine in `dockets`; the realized `disposition`, opinion
  `summary`, `judges`, `precedential_status`, and `citation_count` in
  `opinion-clusters`; the party and attorney names in `parties` / `attorneys`; and
  the panel's judge names and seniority in `people-db-people` — and each file is
  sorted by its own primary key, not the join key, so they cannot be co-iterated.
  The bulk source resolves this in two phases behind the `BulkSource` seam, so the
  cursor, driver, and report are unchanged. *Phase A* (heavy, only when the snapshot
  changes) streams `dockets` filtered to the tracked courts into a local staging
  SQLite, then streams each sibling table keeping only rows whose `docket_id` is in
  that set: `opinion-clusters` (latest cluster per docket wins, its panel ids
  resolved against the `people-db-people` directory to names + seniority) and the
  many-per-docket `parties` / `attorneys` name rows. *Phase B* (cheap, per run)
  serves each chunk as one indexed `LEFT JOIN`, aliasing the cluster columns and
  aggregating the party/attorney names to the field names the ingestion core reads.
  Pointing the staging path at a cached location lets successive runs reuse the staged
  DB instead of re-streaming the GB-scale files.
- **Extending the join:** the sibling tables are the seam for **bringing in more
  bulk data**. Adding a field is local and additive — a column (or staging table)
  in `CourtListenerBulkSource`, a stage step keyed on `docket_id`, a projection in
  the Phase-B query, and the matching field on the corpus row (`ingest.CorpusRow` →
  `corpus.CorpusRow`, plus its SQLite column) — with **no change** to the cursor,
  chunk driver, `SeedReport`, or the `BulkSource` protocol. A sibling whose bulk file
  a snapshot does not publish is simply skipped, so the docket spine always loads and
  the new fields stay blank until the data is present.
- **Resumability:** the cursor (e.g. `config/seed-progress.yaml`) records what is
  loaded per court, so a chunked catch-up resumes cleanly across runs and the
  backfill is rebuildable after a fresh clone.
- **Completion:** on the run that exhausts every court, the workflow opens a
  one-time **completion PR** that flips the cursor's `completed` sign-off flag.
  Merging that PR is the maintainer's acknowledgement and **closes the tracking
  issue** (`Closes #…`); the PR carries no corpus (the blob already streamed to the
  default branch chunk-by-chunk, so parking it on a branch would reintroduce the
  lost-update the `corpus-write` lock removed). Afterwards the workflow no-ops until
  the next quarterly bulk snapshot, which resets `completed` and starts a
  **reconciliation** pass.

## Pull — forward freshness

- **Trigger:** an intraday cron that fires several windows a day (staggered from
  other jobs), `workflow_dispatch`, or a maintainer-applied `run:pull` label for an
  on-demand refresh (which re-runs the full `pull-all`, not a single case).
  Recording a decided event's outcome is split off to `run:reconcile` (see *Detect
  resolution* below), so it is **no longer** the deterministic pull's job.
- **Per-window tracking:** the day's windows share one short-lived `pull-log`
  issue — the first window opens it, each posts a summary (handoffs opened, whether
  snapshots were committed), and the final daily window closes it on success — left
  open as a record if a window fails. The `pull-log` label is deliberately not a
  `run:*` trigger label, so the tracking issue never re-fires pull.
- **Budget governor:** a per-run cap (`max_cases_per_run` dockets ≈ ~3 requests
  each) with **oldest-`last_pulled`-first rotation** and **skip closed/resolved**
  cases, sized so each window stays under the active CourtListener tier's hourly
  ceiling and the day's windows under its daily one. A slice of each run
  (`eligible_refresh_reserve`) is reserved for the stalest **predict-eligible**
  cases, so the SCOTUS-touched pilot set rotates ahead of the much larger active
  set and new docket activity is caught before a case resolves. As the active set
  grows past one run's capacity, each case is simply
  refreshed every few days. The rotation key `last_pulled` is **per-case tracking
  state in the corpus** — raw facts, tracking state included, live in the corpus,
  not git — so the governor adds and maintains that column (the old
  `TrackedCase.last_pulled` git field was removed when seed/pull moved their raw
  output into the corpus).
- **Three jobs over the shared core:**
  1. **Refresh** active known cases (`pull_case`), ingesting fresh facts into the
     corpus through the shared core and queuing `run:predict` for changed cases
     with open events.
  2. **Discover** newly-filed cases since the last run (CourtListener search by
     court + `date_filed`) → onboard into the corpus as a tracked case and run the
     **event-definition stage** to record its predictable event(s). Each court is
     searched from its **discovery watermark** (per-court tracking state in the
     corpus): the newest `date_filed` onboarded so far, seeded by `seed` to the
     bulk snapshot's date (see *Discovery frontier*). The watermark only moves
     forward, so a run that finds nothing still records the date it searched from
     and the next run resumes there — never resetting to the start default.
  3. **Detect resolution** of tracked open events → write `outcome.json` to the
     git ledger deterministically when the disposition is machine-readable (a
     concrete disposition, a decision date, and a single open event), and queue
     `run:evaluate` for it. Anything ambiguous is **not** guessed: pull files a
     `run:reconcile` issue and an agent (`run-reconcile`) confirms the outcome from
     the snapshot, opens a PR recording `outcome.json`, and — when that PR merges —
     queues `run:evaluate` for the settled events. The `run:reconcile` label routes
     to that agent workflow, not back to this deterministic pull, so filing one
     never re-runs a full refresh. Either path feeds `run:evaluate`.
- **Quarterly bulk reconciliation is seed's job** — the completeness backstop for
  anything daily pull could not reach within the budget.

## Event definition — deterministic, corpus-driven

Defining the **predictable events** of a docket is its own stage, decoupled from
ingestion (`fedcourtsai.pipeline.events`), so it runs once over an ingested docket
regardless of how the case entered (bulk `seed` or forward `pull`). Both entry
paths call the **same** `extract_events`, differing only in a normalization seam
(`from_bulk_row` for seed's CSV rows, `from_api_docket` for pull's REST objects),
so a seeded and a discovered docket yield identical event rows for the same input.
It is classification, not analysis: every event is pinned to a single docket entry
with a closed `kind` enum (`motion` / `petition` / `appeal` / `order`), so the
stage maps qualifying docket entries → event definitions (`kind`,
`docket_entry_id`, `opened_at`, `description`) and writes them as corpus rows.

- **Baseline.** Every docket carries the one thing always worth predicting — the
  disposition of the appeal, or the petition at SCOTUS — even when no entries are
  machine-readable.
- **Baseline-only when there are no entries.** Entry-pinned events
  (`motion` / `petition` / `order`) are produced only where the source actually
  carries the docket entries. Bulk seed rows often do not, so a seeded docket gets
  its baseline event alone; a later forward `pull` refresh, which fetches the full
  entries, enriches the case with the finer-grained events. The baseline always
  stands so no seeded docket is left with nothing to predict.
- **Predictable / unresolved** = the request entry has no *later disposing order
  referencing it* (citing its docket-entry number). When a disposing order does
  reference it, the event is recorded `resolved`; with no citation the stage does
  not guess, so the event stays predictable.
- **Deterministic first, agent only if ambiguous.** An entry that reads like a
  request but matches more than one `kind` is surfaced for an agent `run:reconcile`
  issue (filed automatically by `run-pull`; see [pipeline.md](pipeline.md)) rather
  than classified — the same deterministic-first / agent-fallback split resolution
  detection uses. The default path runs no agent.

## Discovery frontier — the seed → pull hand-off

Forward discovery searches each court from a per-court **discovery watermark** held
in the corpus (tracking state, never git `data/`). For the hand-off from the bulk
backfill to the live frontier to be gap-free, three rules hold:

- **Seed establishes the frontier.** A bulk snapshot is "complete as of" the day
  CourtListener regenerated it (the last day of its quarter). So when a court's
  backfill completes, `seed` seeds that court's discovery watermark to the
  **snapshot's date** (derived from the quarter id, e.g. `2026-Q2` → `2026-06-30`).
  The first forward `pull` then discovers everything filed **since the snapshot**,
  not since today — closing the snapshot→today gap that would otherwise be onboarded
  by nothing.
- **The watermark only moves forward.** A write older than the stored value is
  ignored, so a later forward watermark always wins over seed's hand-off, and a
  re-run (or a quarterly reconciliation against the same snapshot) never rewinds it.
- **A no-results run still advances it.** A discovery pass that finds no new dockets
  records the date it searched from, so the next run resumes there instead of
  resetting to the start default. (It advances only to a date already searched, so
  it can never skip a real filing.) Without this a court that keeps finding nothing
  would restart from "today" every run — a steady-state hole, not a one-time miss.

A court should normally be **seeded** (or have `--since` passed to `discover`)
before its first forward discovery, so its frontier is meaningful. The `today`
default is only a last resort for a court with neither a watermark nor a completed
seed; on its own it discovers nothing useful.

## Steady state

Once backfill completes: history sits in the DVC corpus (refreshed quarterly from
bulk); pull keeps the live frontier current daily within the API budget. Because
seed hands off the snapshot date as the initial discovery watermark, the first
forward pull onboards everything filed since the snapshot, so there is no gap
between the backfill and the live frontier. The result is that, each day after pull
runs, the tracked data is **complete as of that day**.

## Full refresh — rebuild the forward state without losing history

A **full refresh** is the operator escape hatch for a *structural* change to how
data is produced: a new corpus column, a corrected normalization, or a
data-validity bug whose easiest fix is to rebuild every case from source. Refreshing
one case at a time within the daily budget could never catch up, so full refresh
resets the pipeline's **forward tracking state** in one deterministic step
(`fedcourts full-refresh`, run by `run-seed` on its `full_refresh` dispatch input)
so the whole tracked set re-seeds and re-pulls fresh:

- **Re-seed all bulk data.** The seed cursor (`config/seed-progress.yaml`) is reset
  so the next `seed-backfill` re-loads every court from the top — the same path
  seed's quarterly snapshot reconcile takes, triggered on demand rather than by a
  new snapshot. The ingestion upsert is idempotent, so unchanged cases overwrite in
  place and any newly-added column or corrected value is back-filled across the corpus.
- **Re-pull and re-discover every tracked case.** The corpus forward cursors are
  reset: each case's `last_pulled` is cleared so the budget governor treats the
  active set as stalest and re-pulls it, and each tracked court's discovery
  watermark is reset to the snapshot frontier so forward discovery re-walks the
  whole post-snapshot range. That re-walk re-ingests every case filed since the
  snapshot **whether open or closed** — which matters because pull's rotation
  skips closed cases to save budget, so without it a case that resolved after the
  snapshot would be refreshed by neither pull nor (being post-snapshot) the
  re-seed. The watermark is *force*-reset (not just dropped) so an interleaved pull
  cannot leave it advanced to today and skip the range. Re-ingestion never reopens
  an already-resolved event — the event upsert latches `resolved` — so prior
  outcomes are not disturbed. (Closed cases are refreshed at the docket level by
  re-seed and re-discovery; a per-docket re-pull, which `skip_closed` still elides,
  is not performed for them.)

What it deliberately leaves alone is what keeps the operation safe and reversible —
"version old data, keep it":

- **Corpus history is preserved.** Case rows, predictable-event rows, and dated
  snapshots are untouched; full refresh resets *tracking state*, never the facts, so
  the corpus stays append-only and its row count never drops (the
  `validate-corpus` invariant still holds). DVC content-addresses the corpus blob,
  so a refreshed corpus pushes under a new key while the pre-refresh blob remains in
  the remote (the read-write role grants no delete) and its `.dvc` pointer stays in
  git history — so the prior state is recoverable.
- **The git ledger is preserved.** Outcomes, predictions, and evaluations under
  `data/` are versioned by git itself and stay where they are — the historical
  record. "No current cases" follows from the reset rather than from deleting
  anything: the agentic stages are driven by `pull` re-queuing changed cases with
  open events, so after the reset `pull` re-pulls everyone and re-queues fresh, and
  new predictions accrue alongside the retained history.

Because it writes the corpus and the cursor, full refresh runs inside `run-seed`
(the corpus-writer that holds the shared `corpus-write` lock): the reset runs once
before the backfill loop, and the reset cursor + corpus blob are committed and
pushed by the loop's first checkpoint. `--dry-run` reports the blast radius — courts
to re-seed, cases to re-pull, watermarks to reset and the date to re-discover from —
without writing.

## Data validation

Two stores that must agree — the DVC corpus (raw facts) and the git ledger
(derived judgments) — plus an append-only corpus and a schema that is law give the
data a set of **invariants** worth asserting on their own, distinct from
`run-ops`'s run-health analytics. Run-health asks *did the runs succeed*;
validation asks *is the data correct and internally consistent*. The two meet at
**completeness**: validation produces a correctness verdict, the ops dashboard
([pipeline.md](pipeline.md)) presents it — separate tools, clean handoff.

The invariants fall in three layers:

- **Schema conformance** — every git-ledger artifact under `data/` validates
  against its model. `fedcourts validate` already enforces this in the local gate
  and PR CI; scheduling it on `run-ops` as well catches anything that reached the
  default branch without the gate, plus model/data bit-rot over time.
- **Corpus integrity** — the committed `corpus/corpus.db.dvc` pointer resolves
  against the remote, the corpus opens, its row count only ever **grows** (the
  append-only write role and bucket versioning make a drop a red flag), required
  columns are non-null, no point-in-time snapshot is future-dated and every case's
  filing/decision dates are ordered and not future-dated, coded columns hold values
  from their declared vocabulary (the `Disposition` and `EventKind` enums, the
  tracked-court set), and no case, event, snapshot, or whitespace-variant id is
  duplicated.
- **Referential integrity** — every `outcome.json` / `prediction.json` /
  `evaluation.json` references an event and case that exist in the corpus (no
  orphan judgments), every evaluation targets a real prediction, and the seed
  cursor reconciles against the corpus row counts per court.

The corpus-dependent layers land as a `fedcourts validate-corpus` command (sibling
to `validate`) that emits a **JSON verdict** — pass/fail plus per-check counts,
shaped like the other reports. Because `run-ops` is a corpus-free presenter (it
reads the git cursor, not the blob — see [pipeline.md](pipeline.md)), the verdict
is **produced where the corpus is already pulled**: the corpus-writer path
(`run-pull`, and `run-seed` on a reconciliation pass) runs the check as a
non-blocking trailing step and publishes the verdict, and `run-ops` then renders a
**data-health** section from it and, on failure, opens or updates a single
long-lived issue — loud, but never blocking the pipeline. The git-only referential
checks fold into `fedcourts validate` so they also run at PR time: a judgment whose
event has no `event.yaml` in the git tree, or whose declared ids disagree with its
path, is caught in review rather than a day later. Because forward discovery keeps
event definitions in the corpus, the predict/evaluate/reconcile workflows
materialize each event's `event.yaml` from the corpus into its ledger directory
(`fedcourts materialize-event`, beside the snapshot provisioning) so the judgment
PR carries it. The corpus checks need the
remote, so they stay on the schedule (the gate is deliberately offline) — at PR time
"the event exists" means it is defined in the git ledger; the schedule additionally
confirms it against the corpus. This automates, and extends across stores, the
manual corpus spot-check that backed the early backfill.
