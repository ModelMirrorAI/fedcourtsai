# Pipeline & labels

Work is represented as GitHub issues; applying a `run:*` label triggers the
matching workflow. A stage hands off by creating/labeling an issue for the next
stage.

| Label           | Workflow         | Trigger(s)                          | Engine(s)            |
|-----------------|------------------|-------------------------------------|----------------------|
| `run:dev`       | `run-dev`        | issue labeled                       | Claude Code          |
| `run:seed`      | `run-seed`       | tracking issue + weekly schedule    | script (bulk data)   |
| `run:pull`      | `run-pull`       | daily schedule, label, manual       | script (no agent)    |
| `run:reconcile` | `run-reconcile`  | issue labeled (created by run-pull) | Claude Code          |
| `run:predict`   | `run-predict`    | issue labeled (created by run-pull) | Claude Code + Codex  |
| `run:evaluate`  | `run-evaluate`   | issue labeled                       | Claude Code + Codex  |
| _(none)_        | `run-ops`        | daily schedule, manual              | script (no agent)    |

`run-ops` is not part of the issue cascade: it is a read-only daily roll-up of
operational analytics — pipeline health (the Actions run history), backfill
progress + rate/ETA (the seed cursor vs the previous snapshot), and spend (the
`usage.json` ledger + Actions minutes from run durations) — rendered by
`fedcourts ops-report`. It surfaces the current view in one long-lived "Ops
dashboard" issue and appends each JSON snapshot to a dedicated **`ops-metrics`
branch** (an orphan time-series that never merges to `main`, so the default branch
stays clean and the prior snapshot is available for the rate/ETA). It triggers
nothing and touches neither `main` nor the corpus.

It is also the **presenter** of the data-validation verdict (see *Data
validation* in [data-pipeline.md](data-pipeline.md)): the corpus-writer path
produces a correctness verdict where the corpus is already pulled, and `run-ops`
renders it as a **data-health** section and escalates a failing verdict to one
long-lived issue — so the dashboard surfaces both run-health and data-health while
staying a read-only presenter that never touches the corpus.

**seed** loads the historical backlog from CourtListener **bulk data** — chunked
catch-up while backfilling, then a weekly snapshot-id check that reconciles when a
new quarterly bulk snapshot drops; **pull** keeps the active set current from
the rate-limited **REST API** and owns the 125/day budget. The full design —
sources, budget boundary, the corpus/ledger storage split, and the historical
corpus — is in [data-pipeline.md](data-pipeline.md).

## Cascade

```
run:seed (weekly, chunked until done) → backfill bulk corpus chunk → commit + progress comment
                              └─ when complete: completion PR (flips `completed`) → closes tracker
   daily / run:pull → run-pull → open pull-log issue → push fresh facts + snapshots to the corpus
                                 ├─ refresh active cases (oldest-first, budget-capped)
                                 ├─ discover new filings → onboard + define events
                                 ├─ detect resolution → write outcome.json when the
                                 │  disposition is machine-readable (git ledger)
                                 └─ create issues  ← APP TOKEN
                                    ├─ run:predict    (changed case with open events)
                                    ├─ run:evaluate   (case that gained an outcome)
                                    └─ run:reconcile  (decided but not machine-readable
                                                       → agent reconciles by hand)
       run:reconcile → plan → reconcile[matrix] → agent records outcome.json → PR per case
                                 └─ on merge → run:evaluate  (the reconciled events)  ← APP TOKEN
       run:predict → plan (build matrix) → predict[matrix] → PR per predictor×event
       run:evaluate → plan → evaluate[matrix] → PR per evaluator×event
```

## ⚠️ The handoff token gotcha

Events created with the default `GITHUB_TOKEN` **do not trigger other workflows**
(GitHub's loop-prevention). So every cross-workflow handoff (e.g. run-pull creating
a `run:predict` issue) and every PR that must trigger CI is made with a **GitHub
App installation token** (`actions/create-github-app-token`), not `GITHUB_TOKEN`.
See `docs/security.md` for the one-time App setup.

## Authoring or changing a workflow

When you add a new `run:*` workflow or edit one, the existing workflows are the
canonical reference — each handles these cross-cutting traps inline, so copy the
pattern rather than rediscovering it:

- **Concurrency is evaluated before the job `if`.** An `issues: labeled` event
  fans out to *every* workflow that listens for it, and the job-level label filter
  runs only after the concurrency group is assigned. A corpus writer (seed, pull)
  must therefore join the shared `corpus-write` group **only** when its own label
  matched — otherwise an unrelated label cancels a real writer. See the
  `concurrency:` expression in `run-seed.yml` / `run-pull.yml`. To dispatch one of
  these reliably, prefer `workflow_dispatch` over labeling.
- **`git add data/` aborts when `data/` is absent.** No `outcome.json` is written
  on most runs, so `data/` often does not exist; under `set -euo pipefail` the add
  fails the step before the no-op guard. Stage the always-present pointer
  unconditionally and guard the rest with `if [ -d data ]; then git add data/; fi`
  (see `run-pull.yml`). The same shape lives in run-predict/evaluate/reconcile.
- **Long-running jobs outlive their credentials.** A GitHub App installation token
  has a hard 1h life and an AWS OIDC session defaults to 1h. A loop that runs for
  hours (seed backfill) must re-mint the App token before it ages out and raise
  `role-duration-seconds` to cover the run; see the self-refreshing token helper
  and the `configure-aws-credentials` step in `run-seed.yml`.
- **The runner is ephemeral, so fixed per-run costs are re-paid every run.** Build
  expensive shared state (e.g. the bulk-data staging DB, ~38 min) once per job and
  reuse it across chunks via a `staging_path` rather than per chunk.

Validate any `.github/` change locally with the linters CI enforces (see the
local gate in [AGENTS.md](../AGENTS.md)).

## The predict/evaluate matrix

`plan` parses the issue body's ` ```json ``` ` case block and runs
`fedcourts predict-matrix` / `evaluate-matrix`, which expands the **registry ×
cases × events** into a GitHub Actions matrix. When prediction scope is gated
(`predict.scope=scotus_touched`) the builder reads each case's latched
`predict_eligible` flag, so `plan` first `dvc pull`s the corpus; with the gate on
and no corpus on disk the build fails loud rather than emit an empty matrix. Each
matrix cell routes to Claude Code or Codex by the entry's `engine`. The agent writes files only; a uniform
step validates, commits to a branch, and opens one PR. The workflow's
`strategy.max-parallel` throttles the whole fan-out, however many cases it spans.

To trigger prediction/evaluation for **one** case, open an issue whose body
contains a single object and apply `run:predict` (or `run:evaluate`):

    ```json
    {"court": "ca9", "docket": 64512345, "events": ["evt-motion-stay"]}
    ```

To trigger **many** cases from one issue (e.g. a whole SCOTUS long-conference
list of petitions), use a JSON array of the same objects:

    ```json
    [
      {"court": "scotus", "docket": 24001, "events": ["evt-petition-cert"]},
      {"court": "scotus", "docket": 24002, "events": ["evt-petition-cert"]}
    ]
    ```

`events` is optional per case: omit it (or pass `[]`) to target the case's
default events — its **open** events for `run:predict`, its **resolved** events
for `run:evaluate`, so already-resolved events are skipped. Every listed case is
multiplied by the registry and its events to produce one matrix cell — and one
PR — per predictor/evaluator × case × event.

## Reconcile: an agent finishes pull's outcome detection

`run-pull` records `outcome.json` itself only when a decided docket is
unambiguous (a machine-readable disposition, a decision date, and a single open
event). Everything else — an unreadable/absent disposition, no decision date, or
a case-level disposition that cannot be attributed across several open events — it
hands to an agent by filing a **`run:reconcile`** issue (it does not guess). That
label routes to `run-reconcile`, **not** back to the deterministic pull, so filing
or relabeling one never re-runs a full refresh.

`run-reconcile` mirrors `run-predict`/`run-evaluate`: `plan` parses the issue's
` ```json ``` ` case block into a **per-case** matrix (`fedcourts
reconcile-matrix`; one cell per case, because the agent must weigh a case's open
events together to attribute the disposition), the agent reads the point-in-time
snapshot and writes `outcome.json` for each event it can settle, and the workflow
validates, commits, and opens one PR per case. An event the agent cannot settle
with confidence is left open with a note on the issue — recording nothing beats a
guess.

Closing the cascade gap: a reconciled `outcome.json` reaches the default branch
only when its PR **merges**, so the handoff to evaluation is fired by the merge,
not by detection. On a merged `reconcile/*` PR, `run-reconcile` opens a
`run:evaluate` issue (App token) for exactly the events the PR settled — so a
hand-reconciled outcome is scored just like a deterministically-detected one.

## Graceful degradation on limits

Agent steps (dev, predict, evaluate, reconcile) are bounded by a step-level
`timeout-minutes` set below the job's, so a run that overruns trips the *step* —
not the job. A step timeout (or a max-turns stop) fails only that step and leaves
the runner alive, so the finalize step still runs (`if: !cancelled()`) and the
agent's partial work survives instead of being discarded with the cancelled job.

What "finalize" salvages depends on the stage. The matrix stages
(predict/evaluate/reconcile) already have the workflow do git: when the agent did
not finish cleanly, the finalize step commits whatever it produced and opens the
PR as a **draft** (with a note) rather than a ready one — and if that partial
output fails schema validation it stays a draft for review instead of failing the
job. In `run-dev`, where the agent does its own git, a rescue step commits any
leftover changes on the issue branch and opens a **draft** PR for a maintainer to
finish. A run that finished cleanly is unaffected: the draft path only triggers
when the agent stopped early.

## Snapshot sequencing

`run-pull` pushes factual snapshots **to the corpus** (`dvc push`) before it
queues `run:predict`, so `run-predict` — a read-only corpus consumer (`dvc pull`)
— sees the snapshot it must predict from. Raw facts never go through PRs (they are
CourtListener data, not agent output); agent outputs (predictions, evaluations)
always do.
