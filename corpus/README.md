# Corpus — the unified raw-fact store

All *raw facts* live in the corpus: dockets, dated snapshots, judges, case
metadata and tracking state, and event definitions — written identically by
every ingestion channel through the shared seam in
[`fedcourtsai.corpus`](../src/fedcourtsai/corpus.py). Derived judgments live in
the git ledger under [`data/`](../data), not here (see the *Data model* section
of the [README](../README.md); pipeline design:
[docs/data-pipeline.md](../docs/data-pipeline.md)). This page is the store
internals and developer access.

## Format and tracking

The corpus has two halves:

- **The index** — a single **SQLite** database, `corpus/corpus.db`, versioned
  with **DVC**: the blob lives in the DVC remote (a private S3 bucket) and only
  the small `corpus.db.dvc` pointer is committed to git (the blob and its
  sidecars are gitignored). In production (the corpus-split mode,
  `FEDCOURTS_CORPUS_SPLIT=1` on the runner environment) the writers keep it
  **payload-free**: the `snapshots`/`documents` tables stay empty and
  `cases.opinion_text` stays NULL (a `has_opinion` presence bit is retained),
  so the blob stays a small metadata index and its per-run `dvc push` does not
  grow with the bulk. With the mode off (the default — dev environments, the
  fixture loop, offline tests) the same schema holds the payloads inline in a
  single self-contained blob.
- **The per-case content store** ([`fedcourtsai.casestore`](../src/fedcourtsai/casestore.py))
  — a browsable, write-once, access-gated S3 store holding the bulk payloads,
  keyed to mirror the ledger's `data/cases/<court>/<docket>/` shape:

  ```
  <court>/<docket_id>/
    case.json                                    # the CorpusRow
    events.json                                  # the case's events
    snapshots/<YYYY-MM-DD>.json                  # dated point-in-time docket payload
    documents/documents.json                     # manifest: kind -> current text leaf
    documents/<kind>/<YYYY-MM-DD>-<digest>.txt   # extracted text (content-addressed)
  ```

  Document text leaves are content-addressed and dated snapshots immutable per
  day, so bulk content is never overwritten in place; the small manifests are
  versioned by the bucket rather than deleted. Its location comes from
  `FEDCOURTS_CASESTORE_URL`.

SQLite keeps the index a single artifact — one DVC pointer, queryable with
plain SQL. The format is internal; the stable contract is the **row schema**
below, whose identifiers and `Disposition` vocabulary are shared with the
ledger models in `fedcourtsai.schemas`.

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
| `opinion_text`        | text            | opinion body — NULL under the split mode (the content store holds it; `has_opinion` retains the presence signal) |
| `summary`             | text            | short form for retrieval                     |
| `last_pulled`         | date            | tracking state: when `pull` last refreshed it |
| `predict_eligible`    | integer (0/1)   | derived mirror of the prediction scope (`court == scotus`); see below |
| `predict_excluded`    | integer (0/1)   | out-of-scope latch, owned by the scope reconcile |
| `originating_court`        | text       | lower court this docket came from (`appeal_from`) |
| `originating_docket_number`| text       | docket number in the originating court (REST-only) |
| `date_cert_granted`   | date            | petition-stage cert grant date (SCOTUS)       |
| `date_cert_denied`    | date            | petition-stage cert denial date (SCOTUS)      |
| `last_live_polled`    | date            | tracking state: when the live channel last polled it |
| `distributed_for_conference` | date     | the conference this petition is currently distributed for (live-parsed) |
| `distribution_count`  | integer         | distinct conferences distributed for (relists = count − 1, floored at 0); null = never live-parsed, 0 = parsed, never distributed |
| `cvsg_date`           | date            | when the Court called for the views of the Solicitor General (live-parsed) |
| `originating_court_name` | text         | raw `LowerCourt` name — keeps state courts identifiable where `originating_court` is null |
| `sample_weight`       | integer         | inverse inclusion probability (1 = kept with certainty; the sampling interval for a walker-kept denial); null = no channel asserted a weight |

`judges` and `panel` describe the same bench from different angles: `judges` is the
flat name list retrieval matches on, while `panel` carries the structured detail.
The multi-valued sibling facts (`panel`, `parties`, `attorneys`) are filled by
whichever channel carries them; a bulk-shaped source supplies them through the
shared normalizer, `fedcourtsai.pipeline.ingest.from_bulk_row`.

`last_pulled` is per-case **tracking state**, not a docket fact: `pull` stamps it
on every refresh and the budget governor rotates the oldest-`last_pulled`-first
slice of the unresolved set within the API budget (see
[docs/data-pipeline.md](../docs/data-pipeline.md)). `embedding[]` (semantic
retrieval) is a later upgrade and is not stored yet.

The live-parsed signal family (`distributed_for_conference`,
`distribution_count`, `cvsg_date`, `originating_court_name`) is supplied only by
the supremecourt.gov channel; every other writer preserves the stored values
(fill-in latches, except `distribution_count`, which max-latches — proceedings
are append-only, so the count only grows). `distribution_count` doubles as the
family's parse-coverage sentinel: null means the proceedings were never
live-parsed, 0 asserts *parsed and never distributed*. `sample_weight` is
min-latched — an inclusion probability is only ever learned toward certainty —
so a weighted aggregate can multiply by it and count a walker-sampled denial at
full strength; null means no channel asserted a weight.

`predict_eligible` is a **derived convenience mirror** of the prediction scope
(`court == 'scotus'`): every scope seam reads the court predicate directly, so
the column is queryable but never the source of truth. Only the agentic
predict/evaluate stages are gated; ingestion stays full-coverage. The
lower-court link (`originating_court` / `originating_docket_number`) is
retrieval context, never a scope trigger. See the prediction scope in
[docs/data-pipeline.md](../docs/data-pipeline.md).

## Predictable events (`events`)

The things the pipeline predicts about a case are raw facts too, so they live
in the corpus, not as per-case files. The deterministic event-definition stage
(`fedcourtsai.pipeline.events`) records one or more events per docket by
classifying its entries; see [docs/data-pipeline.md](../docs/data-pipeline.md).

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

## Cursors and watermarks

Per-court discovery watermarks (`discovery_watermarks`: `court`, `last_filed`)
are dormant in production (`pull.discover_new_filings` is off — the live
channel onboards SCOTUS filings). The live channel's and the historical
walker's per-(Term, stream) cursors share one `live_discovery_cursors` table
with disjoint stream names and the same only-moves-forward semantics. Beside
each cursor's `last_serial` sits a nullable `frontier_serial` — where the
stream's end (consecutive 404s) was last observed; `frontier_serial =
last_serial` reads as *walk complete at the current cursor*, and the cursor
pair yields an exact per-Term filings census by fee class (paid serials number
from 1, IFP from 5001) without ingesting every serial.

## Dated snapshots (`snapshots`)

Each ingestion channel stores the full point-in-time docket payload it fetched
(the REST docket + entries, or the supremecourt.gov docket JSON) — the raw fact
a normalized `cases` row cannot fully capture. `pull` diffs the latest stored
snapshot against the fresh fetch to decide whether a case *changed* (the
`run:predict` trigger), and provisioning materializes a case's latest snapshot
for the agent to predict from (`fedcourts provision-snapshot`). In production
the payloads live as the content store's `snapshots/<date>.json` objects and
this table stays empty; with the split mode off they live inline:

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
