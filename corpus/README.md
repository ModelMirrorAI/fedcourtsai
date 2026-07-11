# Corpus — the unified raw-fact store

All *raw facts* live here in one packed, queryable store: dockets, dated
snapshots, judges, case metadata and tracking state, and event definitions.
There is **one** corpus for the whole pipeline, written identically by every
ingestion channel (the CourtListener REST API and the supremecourt.gov live +
historical channels) through the shared ingestion
seam in [`fedcourtsai.corpus`](../src/fedcourtsai/corpus.py). Derived judgments
(outcomes, predictions, evaluations, reasoning) do **not** live here — they are
the git ledger under [`data/`](../data). See
[docs/data-model.md](../docs/data-model.md) and
[docs/data-pipeline.md](../docs/data-pipeline.md).

## Format and tracking

The packed store is a single **SQLite** database, `corpus/corpus.db`, versioned
with **DVC**: the blob lives in the DVC remote (a private S3 bucket) and only the
small `corpus.db.dvc` pointer is committed to git. The blob and its sidecar
files are gitignored (see `.gitignore`); the pointer is created on first ingest
(`dvc add corpus/corpus.db`) by the run-pull writer jobs and updated as the
corpus grows.

SQLite (over Parquet shards) keeps the corpus a single artifact — one DVC
pointer rather than a sharded tree — queryable with plain SQL for retrieval and
needing no extra runtime dependency. The format is internal; the stable contract
is the **row schema** below, whose identifiers and `Disposition` vocabulary are
shared with the ledger models in `fedcourtsai.schemas`.

## Row schema (`cases`)

Each row is a normalized, **labeled** record. It carries the realized
`disposition`, so the corpus doubles as a back-testing set and a retrieval
source.

| Column                | Type            | Notes                                        |
|-----------------------|-----------------|----------------------------------------------|
| `case_id`             | text (PK)       | `<court_id>/<docket_id>`                      |
| `court`               | text            | CourtListener court id                        |
| `docket_number`       | text            |                                              |
| `case_name`           | text            | case caption, e.g. `Doe v. Roe` (both ingestion paths) |
| `date_filed`          | date            |                                              |
| `date_decided`        | date            |                                              |
| `disposition`         | text            | realized outcome label; null while unresolved |
| `judges`              | json array      | judge names (flat retrieval key)             |
| `panel`               | json array      | structured panel: `{name, seniority}` per judge |
| `parties`             | json array      | party names on the docket                     |
| `attorneys`           | json array      | attorney names of record                      |
| `topic`               | text            | nature of suit / subject-matter topic         |
| `citations`           | json array      |                                              |
| `citation_count`      | integer         | times the decision has been cited            |
| `precedential_status` | text            | Published / Unpublished / Errata             |
| `opinion_text`        | text            | full opinion text                            |
| `summary`             | text            | short form for retrieval                     |
| `last_pulled`         | date            | tracking state: when `pull` last refreshed it |
| `predict_eligible`    | integer (0/1)   | prediction-scope latch (SCOTUS-touched); see below |
| `originating_court`        | text       | lower court this docket came from (`appeal_from`) |
| `originating_docket_number`| text       | docket number in the originating court (REST-only) |

`judges` and `panel` describe the same bench from different angles: `judges` is the
flat name list retrieval matches on (overlap with a `PriorQuery`), while `panel`
carries the structured detail — each judge's authoritative `name` and `seniority`,
resolved against the `people-db-people` directory during the staged join. The
multi-valued sibling facts (`panel`, `parties`, `attorneys`) come from bulk files
joined on `docket_id`; see the staged join in
[docs/data-pipeline.md](../docs/data-pipeline.md).

`last_pulled` is per-case **tracking state**, not a docket fact: `pull` stamps it
on every refresh and the budget governor rotates the oldest-`last_pulled`-first
slice of the unresolved set within the API budget (see
[docs/data-pipeline.md](../docs/data-pipeline.md)). `embedding[]` (semantic
retrieval) is a later upgrade and is not stored yet.

`predict_eligible` is the **prediction-scope latch**: it turns on the first time a
case interacts with SCOTUS and never clears, gating only the agentic
predict/evaluate stages (ingestion stays full-coverage). A SCOTUS docket sets it on
itself; it also propagates to the case's originating court-of-appeals docket via the
lower-court link — `originating_court` (CourtListener `appeal_from`) plus
`originating_docket_number` (`originating_court_information.docket_number`, populated
only on the REST path) — joined on court id + normalized docket number. See the
prediction scope in [docs/data-pipeline.md](../docs/data-pipeline.md).

## Predictable events (`events`)

The things the pipeline predicts about a case — e.g. the disposition of an
appeal — are raw facts too, so they live in the corpus, not as per-case
`event.yaml` files. The deterministic event-definition stage
(`fedcourtsai.pipeline.events`) records one or more events for a docket by
classifying its docket entries; see
[docs/data-pipeline.md](../docs/data-pipeline.md).

| Column            | Type        | Notes                                       |
|-------------------|-------------|---------------------------------------------|
| `case_id`         | text (PK)   | `<court_id>/<docket_id>`                     |
| `event_id`        | text (PK)   | `evt-<kind>-<slug>`; unique within a case    |
| `court`           | text        | CourtListener court id                       |
| `kind`            | text        | motion / petition / appeal / order          |
| `title`           | text        |                                             |
| `description`     | text        |                                             |
| `docket_entry_id` | integer     | docket entry the event is pinned to; null for case-level |
| `decision_target` | text        | what is predicted (default `disposition`)   |
| `opened_at`       | date        | when the event became predictable           |
| `resolved`        | integer     | 0 while open, 1 once resolved               |

## Forward-discovery watermark (`discovery_watermarks`)

Per-court **tracking state**: the newest
`date_filed` `pull` has discovered for a court. Discovery fetches dockets filed
on or after this date, then advances it, so each run resumes where the last left
off without rescanning the court.

| Column       | Type      | Notes                                          |
|--------------|-----------|------------------------------------------------|
| `court`      | text (PK) | CourtListener court id                          |
| `last_filed` | date      | newest `date_filed` discovered so far          |

## Dated snapshots (`snapshots`)

Each `pull` stores the full point-in-time docket JSON (docket + entries) it
fetched — the raw fact a normalized `cases` row cannot fully capture. `pull`
diffs the latest stored snapshot against the fresh fetch to decide whether a case
*changed* (the `run:predict` trigger), and the predict/evaluate/reconcile
workflows provision a case's latest snapshot from here for the agent to predict
from (`fedcourts provision-snapshot`).

| Column          | Type      | Notes                                          |
|-----------------|-----------|------------------------------------------------|
| `case_id`       | text (PK) | `<court_id>/<docket_id>`                        |
| `snapshot_date` | text (PK) | pull date; one snapshot per case per day        |
| `payload`       | text      | full-docket JSON (sorted keys for stable bytes) |

## Working with it locally

```bash
dvc remote modify --local storage url "<your bucket url>"   # one-time, see SECURITY.md
dvc pull                 # fetch corpus.db from the remote
fedcourts corpus-info    # show the location and row count
```

Without remote access, build a tiny **synthetic** corpus instead — a handful of
cases across several courts, a mix of resolved and open, with their events and
snapshots — so the read commands (`provision-snapshot`, `query`, `open-events`)
work offline. It is deterministic and never a substitute for the real corpus:

```bash
fedcourts make-fixture-corpus    # writes the synthetic corpus to corpus/corpus.db
```

## Precedent retrieval

At prediction time a model pulls a handful of *relevant* priors rather than the
bulk set. `fedcourts query` (and the `corpus.retrieve_priors` library API) takes
structured filters — exact match on `--court` / `--topic` / `--disposition`,
overlap match on repeatable `--judge` / `--citation` — and prints the priors as
ranked JSON lines, most relevant first, decided cases only unless
`--include-open`:

```bash
fedcourts query --court ca9 --topic "civil rights" --judge smith --citation "410 U.S. 113"
```

Each given filter must match (the filters AND together); judges/citations rank
the survivors by how much they share. `opinion_text` is omitted unless `--full`.
Semantic / embedding similarity is a later upgrade on the same query seam.
