# Pipeline metrics (DVC-tracked)

Aggregate, versioned metrics for the pipeline — **back-test results** and
predictor **leaderboards** — wired through `dvc metrics`. These are small,
human-readable JSON files committed to git (the readable scoring trail a reviewer
follows); `dvc metrics show` / `dvc metrics diff` read them so results can be
compared across commits. The bulk historical *facts* live in the DVC remote (see
[../corpus/README.md](../corpus/README.md)); these aggregate *judgements* stay in
git.

The files are registered under the top-level `metrics:` key of
[../dvc.yaml](../dvc.yaml):

| File              | Produced by   | Shape                                                  |
|-------------------|---------------|--------------------------------------------------------|
| `backtest.json`   | back-testing  | replay predictors over resolved corpus events vs. label |
| `leaderboard.json`| back-testing  | per-predictor accuracy / Brier, ranked                 |

Both ship as **empty initial state** (`n_events: 0`, no predictors) and are
populated by the future back-test workflow. Inspect with:

```bash
uv sync --extra dvc
dvc metrics show
dvc metrics diff            # compare against a previous commit
```
