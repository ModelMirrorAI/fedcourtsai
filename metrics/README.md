# Metrics

Pipeline metrics, registered in [`dvc.yaml`](../dvc.yaml) so `dvc metrics show`
and `dvc metrics diff` can track them over time:

- `backtest.json` — results of replaying predictors against historical *resolved*
  events in the corpus (outcome hidden at predict time, scored against the known
  `disposition`): per predictor, disposition accuracy, binary granted accuracy,
  and the mean Brier score of P(granted). The `backtest` DVC stage produces it by
  running `fedcourts backtest`, a deterministic, offline replay over the corpus —
  empty (zero counts) until a corpus with outcome labels is present.
- `leaderboard.json` — predictors ranked best-first from the evaluations ledger
  under `data/`: per predictor, accuracy, mean Brier score, mean vote accuracy, a
  mean reasoning-quality summary, and counts (events scored, evaluations,
  evaluators). The `leaderboard` DVC stage produces it by running
  `fedcourts leaderboard`, a deterministic, offline roll-up — empty (`{}` plus the
  zero counts) until the first evaluation lands.
- `statpack.json` / `statpack.md` — a corpus base-rate **statpack** (an independent
  published artifact): headline case counts and the overall disposition base rate,
  plus curated breakdowns — cases by court, and SCOTUS petitions by Term and by
  nature-of-suit topic. The `statpack` DVC stage produces both the machine JSON and a
  rendered Markdown document by running `fedcourts statpack`, a deterministic, offline
  roll-up of the corpus — empty (zero counts, empty sections) until a corpus is present.

These files are deterministic, offline roll-ups that start empty (zero counts)
until their input lands — the evaluations ledger for the leaderboard, a corpus
with outcome labels for the back-test and statpack. All are small and worth reading
in a diff, so they are git-tracked rather than pushed to the DVC remote like the
corpus blob.
