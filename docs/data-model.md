# Data model

The project's state lives in two stores, split by **kind of data**:

- **The corpus** — all *raw facts*: dockets, point-in-time snapshots, judges,
  case metadata and tracking state, and event definitions. A packed, queryable
  store — a single **SQLite** database (`corpus/corpus.db`) — versioned with
  **DVC** (the blob in the DVC remote, a pointer + load cursor in git). Both
  `seed` and `pull` write it, in one shared format through one shared ingestion
  core (`fedcourtsai.corpus`).
- **The ledger** — the small, *derived* artifacts under `data/`: outcomes,
  predictions, and evaluations, plus the reasoning that explains them. Plain git,
  validated by the pydantic models in `fedcourtsai.schemas` (exported to
  `schemas/*.schema.json`), reviewed in PRs, and checked by `fedcourts validate
  data` in CI. The layout below shows the shape of a single event's subtree.

The line is deliberate: raw facts are bulk and regenerable, so they live in the
packed corpus; derived judgments are tiny, critical, and worth reading in a diff,
so they live in git.

## The ledger layout (case-centric)

Everything in git is keyed by `case_id` / `event_id`, so a single event's story
sits in one subtree:

```
data/cases/<court_id>/<docket_id>/events/<event_id>/
  outcome.json                    # Outcome: realized ground truth, once resolved
  predictions/<predictor_id>/<run_id>/
    prediction.json               # Prediction: granted 1/0, P(granted), votes
    reasoning.md                  # predicted reasoning (qualitative)
    usage.json                    # ModelUsage: measured tokens + estimated cost
  evaluations/<evaluator_id>/<run_id>/
    usage.json                    # ModelUsage for the evaluator's run (all predictors)
  evaluations/<evaluator_id>/<predictor_id>/<run_id>/
    evaluation.json               # Evaluation: correctness, Brier, vote acc, quality
    evaluation.md                 # qualitative critique
```

Each `usage.json` records one matrix cell's token usage and an estimated USD cost
(rates in `fedcourtsai.pricing`, kept in sync with [budget.md](budget.md)). The
workflow captures it from the engine's own run log — never the agent's word — so a
maintainer can roll it up (`fedcourts usage-summary`) into a measured \$/run.

The raw facts an event is predicted from — its docket, the snapshot, the event
definition itself — live in the corpus, not here. Predictors and evaluators read
them from the corpus, provisioned read-only for their run.

## Identifiers

- **case_id** = `<court_id>/<docket_id>` using the CourtListener court id and the
  stable integer docket id (e.g. `ca9/64512345`).
- **event_id** = `evt-<kind>-<slug>` (e.g. `evt-motion-stay`).
- **run_id** = UTC timestamp (`YYYYMMDDThhmmssZ`) namespacing one agent run.

Always derive these via `fedcourtsai.ids`/`fedcourtsai.paths`; never hand-build.

## Why case-centric

Everything derived about one event — every predictor's prediction, the realized
outcome, and every evaluation — lives under one `events/<event_id>/` directory:

- **Evaluation context is local.** An evaluator reads one directory to see all
  predictors' outputs plus the outcome.
- **Diffs are local.** A new prediction touches only its own run directory.
- **Context loading is simple.** "Everything we've concluded about this event" is
  one subtree.

Predictions from different predictors live together under
`events/<event_id>/predictions/<predictor_id>/` rather than in a separate
per-predictor tree. Co-locating keeps one event's story in one place; the cost is
that a cross-predictor leaderboard is a glob/index rather than a flat scan — a
cheap trade, served by a `fedcourts report` command.

## The corpus (raw facts)

The historical backlog (all of SCOTUS + the 13 circuits) and the fresh facts
`pull` fetches are far too large to hold as per-case files — millions of YAML
files would choke `git` even under LFS. They land instead in one packed,
normalized, **labeled** corpus, written identically by `seed` (from CourtListener
bulk data) and `pull` (from the REST API). Each row carries the realized
`disposition`, so the corpus doubles as a back-testing set and a retrieval source
for prediction context.

The pydantic models are the contract for the ledger; the corpus is governed by
its own normalized schema (`CorpusRow` in `fedcourtsai.corpus`). The packed store
is a SQLite DB under DVC, but the format is internal — the references the ledger
relies on (ids, dispositions) stay stable regardless. See
[data-pipeline.md](data-pipeline.md) and [corpus/README.md](../corpus/README.md)
for the corpus schema and how seed and pull produce it.
