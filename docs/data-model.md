# Data model

All state is versioned files under `data/`, validated by the pydantic models in
`fedcourtsai.schemas` (exported to `schemas/*.schema.json`). A complete, valid
example lives under `examples/cases/` and is checked by CI.

## Layout (case-centric)

```
data/cases/<court_id>/<docket_id>/
  case.yaml                       # TrackedCase: metadata + tracking status
  record/
    docket.json                   # canonical current docket (CourtListener)
    snapshots/<YYYY-MM-DD>.json    # immutable point-in-time prediction inputs
  events/<event_id>/
    event.yaml                    # PredictableEvent: what we predict
    outcome.json                  # Outcome: ground truth, once resolved
    predictions/<predictor_id>/<run_id>/
      prediction.json             # Prediction: granted 1/0, P(granted), votes
      reasoning.md                # predicted reasoning (qualitative)
    evaluations/<evaluator_id>/<predictor_id>/<run_id>/
      evaluation.json             # Evaluation: correctness, Brier, vote acc, quality
      evaluation.md               # qualitative critique
```

## Identifiers

- **case_id** = `<court_id>/<docket_id>` using the CourtListener court id and the
  stable integer docket id (e.g. `ca9/64512345`).
- **event_id** = `evt-<kind>-<slug>` (e.g. `evt-motion-stay`).
- **run_id** = UTC timestamp (`YYYYMMDDThhmmssZ`) namespacing one agent run.

Always derive these via `fedcourtsai.ids`/`fedcourtsai.paths`; never hand-build.

## Why case-centric (and the alternative)

Everything about one predictable event — the snapshot it was predicted from, every
predictor's prediction, the realized outcome, and every evaluation — lives under
one `events/<event_id>/` directory. Benefits:

- **Evaluation context is local.** An evaluator reads one directory to see all
  predictors' outputs plus the outcome.
- **Diffs are local.** A new prediction touches only its own run directory.
- **Agent context loading is simple.** "Everything about this case" is one subtree.

**Predictions from different predictors live together** under
`events/<event_id>/predictions/<predictor_id>/`, rather than in a separate
per-predictor top-level tree. The alternative — a parallel `predictions/` tree
keyed by predictor — makes cross-predictor leaderboards a flat scan but scatters a
single event's story across the repo and complicates evaluation. We chose
co-location; cross-cutting leaderboards are produced by globbing/indexing instead
(cheap, and a natural future `fedcourts report` command).

## Two-tier storage (active set + historical corpus)

The layout above is the **active tier**: a small, curated set of cases we are
actively predicting on, kept as human-viewable files in plain git so diffs are
reviewable and the `validate` gate applies. The **pull** phase maintains it.

The historical backlog (all of SCOTUS + the 13 circuits) is far too large to hold
as per-case files — millions of YAML files would choke `git` even under LFS. It
lives in a second, **packed tier**: a normalized, **labeled**, queryable corpus
(Parquet shards or SQLite) versioned with **DVC** (data in the DVC remote, a
pointer + load cursor in git). The **seed** phase builds it from CourtListener
bulk data. Each corpus row carries the realized `disposition`, so the corpus
doubles as a back-testing set and as a retrieval source for prediction context.
See [data-pipeline.md](data-pipeline.md) for the corpus schema and how seed/pull
produce each tier.

## Storage evolution

Files-in-git is the right call for the **active tier** (history, review,
simplicity). The packed historical tier follows the same candidates this doc has
always anticipated: a derived **SQLite or Parquet index** for analytics, and
**DVC/Git-LFS** for large blobs while keeping JSON/YAML metadata in git. The
pydantic models stay the contract regardless.
