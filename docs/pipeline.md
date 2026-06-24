# Pipeline & labels

Work is represented as GitHub issues; applying a `run:*` label triggers the
matching workflow. A stage hands off by creating/labeling an issue for the next
stage.

| Label          | Workflow         | Trigger(s)                          | Engine(s)            |
|----------------|------------------|-------------------------------------|----------------------|
| `run:dev`      | `run-dev`        | issue labeled                       | Claude Code          |
| `run:seed`     | `run-seed`       | issue labeled                       | Claude Code + script |
| `run:pull`     | `run-pull`       | daily schedule, label, manual       | script               |
| `run:predict`  | `run-predict`    | issue labeled (created by run-pull) | Claude Code + Codex  |
| `run:evaluate` | `run-evaluate`   | issue labeled                       | Claude Code + Codex  |

## Cascade

```
run:seed → seed dockets (PR) ─merge→
   daily / run:pull → run-pull → commit snapshots to main
                                 └─ for each changed case with open events:
                                    create issue (run:predict)  ← APP TOKEN
       run:predict → plan (build matrix) → predict[matrix] → PR per predictor×event
   (outcome.json lands via a later pull / seed-style update)
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

`run-pull` commits factual snapshots **directly to main** (they are CourtListener
data, not agent output) so that `run-predict`, triggered immediately after, reads
them from main. Agent outputs (predictions, evaluations) always go through PRs.
