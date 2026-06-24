# Corpus — the unified raw-fact store

All *raw facts* live here in one packed, queryable store: dockets, dated
snapshots, judges, case metadata and tracking state, and event definitions.
There is **one** corpus for the whole pipeline, written identically by `seed`
(CourtListener bulk data) and `pull` (the REST API) through the shared ingestion
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
(`dvc add corpus/corpus.db`) by the seed/pull workflows and updated as the corpus
grows.

SQLite (over Parquet shards) keeps the corpus a single artifact — one DVC
pointer rather than a sharded tree — queryable with plain SQL for retrieval and
needing no extra runtime dependency. The format is internal; the stable contract
is the **row schema** below, whose identifiers and `Disposition` vocabulary are
shared with the ledger models in `fedcourtsai.schemas`.

## Row schema (`cases`)

Each row is a normalized, **labeled** record. It carries the realized
`disposition`, so the corpus doubles as a back-testing set and a retrieval
source.

| Column          | Type            | Notes                                        |
|-----------------|-----------------|----------------------------------------------|
| `case_id`       | text (PK)       | `<court_id>/<docket_id>`                      |
| `court`         | text            | CourtListener court id                        |
| `docket_number` | text            |                                              |
| `date_filed`    | date            |                                              |
| `date_decided`  | date            |                                              |
| `disposition`   | text            | realized outcome label; null while unresolved |
| `judges`        | json array      | judge names                                  |
| `topic`         | text            | nature of suit / subject-matter topic         |
| `citations`     | json array      |                                              |
| `opinion_text`  | text            | full opinion text                            |
| `summary`       | text            | short form for retrieval                     |

`embedding[]` (semantic retrieval) is a later upgrade and is not stored yet.

## Working with it locally

```bash
dvc remote modify --local storage url "<your bucket url>"   # one-time, see SECURITY.md
dvc pull                 # fetch corpus.db from the remote
fedcourts corpus-info    # show the location and row count
```
