# Pipeline & labels

Work is represented as GitHub issues; applying a `run:*` label triggers the
matching workflow. A stage hands off by creating/labeling an issue for the next
stage.

| Label          | Workflow         | Trigger(s)                          | Engine(s)            |
|----------------|------------------|-------------------------------------|----------------------|
| `run:dev`      | `run-dev`        | issue labeled                       | Claude Code          |
| `run:seed`     | `run-seed`       | tracking issue + daily schedule     | script (bulk data)   |
| `run:pull`     | `run-pull`       | daily schedule, label, manual       | script + agent       |
| `run:predict`  | `run-predict`    | issue labeled (created by run-pull) | Claude Code + Codex  |
| `run:evaluate` | `run-evaluate`   | issue labeled                       | Claude Code + Codex  |

**seed** loads the historical backlog from CourtListener **bulk data** and runs
daily until complete (then quarterly); **pull** keeps the active set current from
the rate-limited **REST API** and owns the 125/day budget. The full design —
sources, budget boundary, the corpus/ledger storage split, and the historical
corpus — is in [data-pipeline.md](data-pipeline.md).

## Cascade

```
run:seed (daily until done) → backfill bulk corpus chunk → commit + progress comment
   daily / run:pull → run-pull → push fresh facts + snapshots to the corpus
                                 ├─ refresh active cases (oldest-first, budget-capped)
                                 ├─ discover new filings → onboard + define events
                                 ├─ detect resolution → write outcome.json when the
                                 │  disposition is machine-readable (git ledger)
                                 └─ create issues  ← APP TOKEN
                                    ├─ run:predict   (changed case with open events)
                                    ├─ run:evaluate  (case that gained an outcome)
                                    └─ run:pull      (decided but not machine-readable
                                                      → agent reconciles by hand)
       run:predict → plan (build matrix) → predict[matrix] → PR per predictor×event
       run:evaluate → plan → evaluate[matrix] → PR per evaluator×event
```

## ⚠️ The handoff token gotcha

Events created with the default `GITHUB_TOKEN` **do not trigger other workflows**
(GitHub's loop-prevention). So every cross-workflow handoff (e.g. run-pull creating
a `run:predict` issue) and every PR that must trigger CI is made with a **GitHub
App installation token** (`actions/create-github-app-token`), not `GITHUB_TOKEN`.
See `docs/security.md` for the one-time App setup.

## The predict/evaluate matrix

`plan` parses the issue body's ` ```json {court,docket,events} ``` ` block and runs
`fedcourts predict-matrix` / `evaluate-matrix`, which expands the **registry ×
events** into a GitHub Actions matrix. Each matrix cell routes to Claude Code or
Codex by the entry's `engine`. The agent writes files only; a uniform step
validates, commits to a branch, and opens one PR.

To trigger prediction/evaluation manually, open an issue whose body contains:

    ```json
    {"court": "ca9", "docket": 64512345, "events": ["evt-motion-stay"]}
    ```

and apply `run:predict` (or `run:evaluate`).

## Snapshot sequencing

`run-pull` pushes factual snapshots **to the corpus** (`dvc push`) before it
queues `run:predict`, so `run-predict` — a read-only corpus consumer (`dvc pull`)
— sees the snapshot it must predict from. Raw facts never go through PRs (they are
CourtListener data, not agent output); agent outputs (predictions, evaluations)
always do.
