# Metrics

Pipeline metrics, registered in [`dvc.yaml`](../dvc.yaml) so `dvc metrics show`
and `dvc metrics diff` can track them over time:

- `backtest.json` — results of replaying current predictors against historical
  *resolved* events in the corpus (outcome hidden at predict time, scored against
  the known `disposition`).
- `leaderboard.json` — per-predictor standings (accuracy, Brier, vote accuracy)
  aggregated from the evaluation ledger under `data/`.

Both start empty (`{}`) and are populated by the back-test / leaderboard
workflows. They are small and worth reading in a diff, so they are git-tracked
rather than pushed to the DVC remote like the corpus blob.
