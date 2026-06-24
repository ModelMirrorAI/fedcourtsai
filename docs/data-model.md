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

## Storage evolution

Files-in-git is the right call now (history, review, simplicity). If/when the
dataset outgrows it, candidates without changing the logical model: keep raw
snapshots as the source of truth but add a derived **SQLite or Parquet index**
(built in CI) for analytics; or move large blobs to **DVC/Git-LFS** while keeping
JSON/YAML metadata in git. The pydantic models stay the contract regardless.
