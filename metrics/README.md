# Metrics

Pipeline metrics, registered in [`dvc.yaml`](../dvc.yaml) so `dvc metrics show`
and `dvc metrics diff` can track them over time:

- `backtest.json` — results of replaying current predictors against historical
  *resolved* events in the corpus (outcome hidden at predict time, scored against
  the known `disposition`).
- `leaderboard.json` — predictors ranked best-first from the evaluations ledger
  under `data/`: per predictor, accuracy, mean Brier score, mean vote accuracy, a
  mean reasoning-quality summary, and counts (events scored, evaluations,
  evaluators). The `leaderboard` DVC stage produces it by running
  `fedcourts leaderboard`, a deterministic, offline roll-up — empty (`{}` plus the
  zero counts) until the first evaluation lands.

`backtest.json` is still produced out of band by the back-test harness and starts
empty (`{}`). Both files are small and worth reading in a diff, so they are
git-tracked rather than pushed to the DVC remote like the corpus blob.
