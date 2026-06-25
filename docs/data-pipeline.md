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
   │ SEED (daily→quarterly) │ bulk S3 ─► packed corpus (DVC) ─► back-testing, retrieval
   │  no agent, no budget   │ cursor + run:seed tracking issue
   └───────────────────────┘
   ┌───────────────────────┐
   │ PULL (daily, forever)  │ REST API (125/day governor)
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

| Workflow                   | Access     | Why                                  |
|----------------------------|------------|--------------------------------------|
| `run-seed`, `run-pull`     | read-write | corpus writers (`dvc push`)          |
| `run-predict`, `run-evaluate` | read-only | retrieval consumers (`dvc pull`)  |
| `ci`                       | none       | gate stays offline/fast              |

A single IAM role is provisioned, so every wired job assumes the same role and the
read-write/read-only distinction is enforced by the **role's IAM policy**, not the
workflow (a separate read-only principal can be added later). The OIDC wiring
(`permissions: id-token: write` + the credentials step) grants each job its access
without any long-lived key.

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
  → dvc add → dvc push → commit the pointer (+ cursor / snapshots)` and pushes
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

- **Back-testing** — replay current predictors against historical *resolved*
  events (outcome hidden at predict time), score against the known disposition.
- **Retrieval** — at prediction time a model pulls a handful of *relevant*
  priors instead of loading the bulk set into context. Structured retrieval is
  implemented today as `fedcourts query` (and the `corpus.retrieve_priors`
  library API): exact-match filters on court / topic / disposition plus
  overlap filters on judges and citations, ranked by how much each prior shares
  and defaulting to resolved (labeled) cases. Procedural **posture** is not a
  case-level column — it is carried by a case's predictable-event `kind` — so it
  is not yet a query filter; semantic / embedding similarity lands on the same
  query seam once embeddings are stored.

Back-testing is a **future** consumer; this doc only commits to producing a
corpus shaped to support it.

## Seed — historical backfill

- **Trigger:** a single long-lived `run:seed` tracking issue (see
  `.github/ISSUE_TEMPLATE/seed.yml`) plus a daily schedule.
- **Each run** (deterministic, no agent, no API secret): read the committed
  **cursor** → process the next chunk of the bulk snapshot for the target courts
  → write/append the DVC corpus → commit the corpus pointer + cursor bump directly
  to the default branch (under the shared `corpus-write` lock — see Corpus-writer
  coordination) → **comment progress on the tracking issue** (per-court % and
  remaining).
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
  ceiling) with **oldest-`last_pulled`-first rotation** and **skip closed/resolved**
  cases. As the active set grows past one run's capacity, each case is simply
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
     **event-definition stage** to record its predictable event(s).
  3. **Detect resolution** of tracked open events → write `outcome.json` to the
     git ledger deterministically when the disposition is machine-readable, else
     open an agent reconcile issue to confirm. This is what feeds `run:evaluate`.
- **Quarterly bulk reconciliation is seed's job** — the completeness backstop for
  anything daily pull could not reach within the budget.

## Event definition — deterministic, corpus-driven

Defining the **predictable events** of a docket is its own stage, decoupled from
ingestion (`fedcourtsai.pipeline.events`), so it runs once over an ingested docket
regardless of how the case entered (bulk `seed` or forward `pull`). It is
classification, not analysis: every event is pinned to a single docket entry with
a closed `kind` enum (`motion` / `petition` / `appeal` / `order`), so the stage
maps qualifying docket entries → event definitions (`kind`, `docket_entry_id`,
`opened_at`, `description`) and writes them as corpus rows.

- **Baseline.** Every docket carries the one thing always worth predicting — the
  disposition of the appeal, or the petition at SCOTUS — even when no entries are
  machine-readable.
- **Predictable / unresolved** = the request entry has no *later disposing order
  referencing it* (citing its docket-entry number). When a disposing order does
  reference it, the event is recorded `resolved`; with no citation the stage does
  not guess, so the event stays predictable.
- **Deterministic first, agent only if ambiguous.** An entry that reads like a
  request but matches more than one `kind` is surfaced for an agent reconcile
  issue (`.github/ISSUE_TEMPLATE/pull.yml`) rather than classified — the same
  deterministic-first / agent-fallback split resolution detection uses. The
  default path runs no agent.

## Steady state

Once backfill completes: history sits in the DVC corpus (refreshed quarterly from
bulk); pull keeps the live frontier current daily within the API budget. The
result is that, each day after pull runs, the tracked data is **complete as of
that day**.
