# Metrics

Pipeline metrics, registered in [`dvc.yaml`](../dvc.yaml) so `dvc metrics show`
and `dvc metrics diff` can track them over time:

- `backtest.json` — results of replaying predictors against historical *resolved*
  events in the corpus (outcome hidden at predict time, scored against the known
  `disposition`): per predictor, disposition accuracy, binary granted accuracy,
  and the mean Brier score of P(granted). The `backtest` DVC stage produces it by
  running `fedcourts backtest`, a deterministic, offline replay over the corpus —
  empty (zero counts) until a corpus with outcome labels is present. **Labeled
  retrospective by construction** (see the stratification note below): every
  replayed event resolved long before any modern model's training cutoff, so the
  figures measure recall and calibration over known history, never foresight.
- `leaderboard.json` — predictors ranked best-first from the evaluations ledger
  under `data/`: per predictor, accuracy, mean Brier score, mean vote accuracy, a
  mean reasoning-quality summary, and counts (events scored, evaluations,
  evaluators), each reported **per pre-registration stratum** — `forward` and
  `retrospective` blocks, never blended into one number. The `leaderboard` DVC
  stage produces it by running `fedcourts leaderboard`, a deterministic, offline
  roll-up — empty (`{}` plus the zero counts) until the first evaluation lands.

**Forward vs retrospective.** Snapshotting controls what a predictor can *read*,
but not what its model already *knows*: a prediction over an event that resolved
before the model's training cutoff has the outcome inside the model's weights —
the caption alone can retrieve it — so scoring it measures recall plus
calibration, not ex-ante forecasting skill. The clean structural separator is the
pre-registration standard: a cell is **forward** when the event was still
unresolved at the prediction's commit and **retrospective** when it had already
resolved (same-day ties count as retrospective, the conservative reading). The
split is deterministic and offline — the prediction's `created_at` against the
outcome's `resolved_at`, both committed artifacts (`classify_stratum` in
`fedcourtsai.leaderboard` is the single definition). Retrospective cells remain
valuable — they measure calibration and label-mapping fit — but only the forward
stratum is evidence of forecasting skill, so no headline metric may mix them.
- `statpack.json` / `statpack.md` — a corpus base-rate **statpack** (an independent
  published artifact): headline case counts and the overall disposition base rate,
  plus curated breakdowns — cases by court; SCOTUS petitions by Term, by
  nature-of-suit topic, by originating circuit, and by decade era; and the
  **modern discretionary-cert cut** (Term-prefixed cert dockets only — the
  calibration anchor for cert predictions, undiluted by merits-era labels). The `statpack` DVC stage produces both the machine JSON and a
  rendered Markdown document by running `fedcourts statpack`, a deterministic, offline
  roll-up of the corpus — empty (zero counts, empty sections) until a corpus is present.

These files are deterministic, offline roll-ups that start empty (zero counts)
until their input lands — the evaluations ledger for the leaderboard, a corpus
with outcome labels for the back-test and statpack. All are small and worth reading
in a diff, so they are git-tracked rather than pushed to the DVC remote like the
corpus blob.
