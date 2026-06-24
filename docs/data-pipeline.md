# Data pipeline: seed & pull

How case data enters and stays current in `fedcourtsai`. This is the design
contract for the **seed** (historical backfill) and **pull** (forward freshness)
phases. For the label/workflow mechanics see [pipeline.md](pipeline.md); for the
on-disk shapes see [data-model.md](data-model.md).

## Scope

We cover the **Supreme Court and all 13 federal courts of appeals**:

```
scotus  ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11  cadc  cafc
```

District courts are intentionally **out of scope** for now.

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
| Lifecycle       | finite — runs daily **until complete**  | perpetual — runs daily forever    |
| Budget          | ~0 API                                  | owns the 125/day budget           |
| Reporting       | comments on a `run:seed` tracking issue | headless cron                     |
| Steady state    | drops to **quarterly** reconciliation   | stays **daily**                   |

They share an **ingestion core** (a normalization layer where an API docket JSON
and a bulk CSV row both become the same `TrackedCase` / `docket.json` / corpus
row, reusing `serialize` and `store`), shared dedup/cursor utilities, and shared
PR plumbing. **Unify the library, not the job.** Keeping the jobs separate keeps
the budget boundary crisp (pull owns the token; seed never touches it) and keeps
operational status legible.

```
                shared core (pipeline ingest + store + serialize)
   API docket JSON ─┐
   bulk CSV row    ─┴─►  TrackedCase / docket.json / corpus row
   ┌───────────────────────┐
   │ SEED (daily→quarterly) │ bulk S3 ─► packed corpus (DVC) ─► back-testing, retrieval
   │  no agent, no budget   │ cursor + run:seed tracking issue
   └───────────────────────┘
   ┌───────────────────────┐
   │ PULL (daily, forever)  │ REST API (125/day governor)
   │  refresh + discover    │ ─► active cases in data/cases/ (plain git, PR-reviewed)
   │  + outcome detect      │ ─► queue run:predict ; onboard new filings ; outcome.json
   └───────────────────────┘
```

## Two-tier storage

The active set and the historical mass have different access patterns, so they
live in different stores:

1. **Active, curated prediction targets** → plain-git, human-viewable
   `data/cases/<court>/<docket>/{case.yaml, event.yaml, snapshots/…}`. A small
   set with reviewable diffs — exactly what the schema/`validate`/PR-review
   machinery is built for.
2. **Historical corpus** → a **packed, queryable store** (Parquet shards or a
   SQLite DB) versioned with **DVC** (data in the DVC remote, pointer + cursor in
   git). DVC also versions pipeline **metrics** (back-test results, leaderboards).

The rule is **pack, don't proliferate**: millions of per-case YAML files would
choke `git` even under LFS (one tree entry per pointer), so history is packed
into a handful of large artifacts instead. This is the evolution
[data-model.md](data-model.md) already anticipates.

### Corpus schema (sketch)

Each corpus row is a normalized, **labeled** record so it serves both consumers:

```
case_id, court, docket_number, date_filed, date_decided,
disposition (outcome label), judges[], nature/topic,
citations[], opinion_text/summary
# embedding[] — later upgrade for semantic retrieval
```

Carrying `disposition` makes the corpus a ready-made **back-testing** set, and
the structured columns make it **queryable** for retrieval.

### Consumers of the historical corpus

- **Back-testing** — replay current predictors against historical *resolved*
  events (outcome hidden at predict time), score against the known disposition.
- **Retrieval** — at prediction time a model queries for a handful of *relevant*
  priors (by court / judges / topic / posture / citation; semantic search once
  embeddings land) rather than loading the bulk set into context.

Both are **future** consumers; this doc only commits to producing a corpus shaped
to support them.

## Seed — historical backfill

- **Trigger:** a single long-lived `run:seed` tracking issue (see
  `.github/ISSUE_TEMPLATE/seed.yml`) plus a daily schedule.
- **Each run** (deterministic, no agent, no API secret): read the committed
  **cursor** → process the next chunk of the bulk snapshot for the target courts
  → write/append the DVC corpus → open a PR (corpus pointer + cursor bump) →
  **comment progress on the tracking issue** (per-court % and remaining).
- **Resumability:** the cursor (e.g. `config/seed-progress.yaml`) records what is
  loaded per court, so "daily until complete" resumes cleanly and the backfill is
  rebuildable after a fresh clone.
- **Completion:** when the cursor is complete the issue can close; the workflow
  then no-ops until the next quarterly bulk snapshot and performs a
  **reconciliation** pass.

## Pull — forward freshness

- **Trigger:** daily cron (staggered from other jobs), `workflow_dispatch`, or a
  `run:pull` issue for on-demand/reconcile work (see
  `.github/ISSUE_TEMPLATE/pull.yml`).
- **Budget governor:** a per-run cap (~15 dockets ≈ 45 requests, under the 50/hr
  ceiling) with **oldest-`last_pulled`-first rotation** (the field already exists
  on `TrackedCase`) and **skip closed/resolved** cases. As the active set grows
  past one run's capacity, each case is simply refreshed every few days.
- **Three jobs over the shared core:**
  1. **Refresh** active known cases (existing `pull_case`), writing fresh dated
     snapshots and queuing `run:predict` for changed cases with open events.
  2. **Discover** newly-filed cases since the last run (CourtListener search by
     court + `date_filed`) → onboard as an active `data/cases/` entry and define
     predictable `event.yaml`(s).
  3. **Detect resolution** of tracked open events → write `outcome.json`
     deterministically when the disposition is machine-readable, else open an
     agent reconcile issue to confirm. This is what feeds `run:evaluate`.
- **Quarterly bulk reconciliation is seed's job** — the completeness backstop for
  anything daily pull could not reach within the budget.

## Steady state

Once backfill completes: history sits in the DVC corpus (refreshed quarterly from
bulk); pull keeps the live frontier current daily within the API budget. The
result is that, each day after pull runs, the tracked data is **complete as of
that day**.
