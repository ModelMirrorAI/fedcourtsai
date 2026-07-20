# Pipeline & labels

Work is represented as GitHub issues; applying a `run:*` label triggers the
matching workflow. A stage hands off by creating/labeling an issue for the next
stage.

| Label           | Workflow         | Trigger(s)                          | Engine(s)            |
|-----------------|------------------|-------------------------------------|----------------------|
| `run:pull`      | `run-pull`       | daily schedules (pull + live jobs), label, manual | script (no agent)    |
| _(none)_        | `run-seed`       | daily schedules (4 dead-zone windows), manual | script (no agent)    |
| `run:predict`   | `run-predict`    | issue labeled (created by run-pull) | Claude Code + Codex + Gemini |
| `run:evaluate`  | `run-evaluate`   | issue labeled                       | Claude Code + Codex + Gemini |
| `run:backtest`  | `run-backtest`   | issue labeled, manual dispatch (engine/limit params) | Claude Code + Codex (replay) |
| _(none)_        | `run-ops`        | daily schedule (+ a weekly digest tick), manual | script (no agent)    |
| _(none)_        | `run-analytics`  | manual dispatch + weekly schedule   | script (no agent)    |
| _(none)_        | `integration-test` | manual dispatch                 | script; the engine-smoke scenario runs one real agent cell |

`run-ops` is not part of the issue cascade: it is a read-only daily roll-up of
operational analytics, consolidated so it reads as a summary — pipeline health
(the Actions run history, dormant workflows folded into one line), **substance**
(is the machine producing: scored cells by stratum with deltas against the
week-old snapshot when one exists — else the newest,
replay calibration vs the modern-cert deny base rate with the sample size beside
every number, per-predictor evaluation-score distributions, and live-frontier
readiness — each sub-block shown only once its feed exists), **spend & cost**
(the `usage.json` ledger + Actions minutes from run durations), **agent signals**
(the committed `flags.json` / `tooling.json` and evaluator leakage gradings,
scoped to a recent window so old, fixed flags age out of the summary — the
`agent-feedback` issue and the raw ledger still keep every flag), and **open
trigger issues** (still-open `run:*` fan-out triggers = stalled runs, oldest
first, so an orphaned issue never sits invisible) — rendered by
`fedcourts ops-report`. It surfaces the current view in one long-lived "Ops
dashboard" issue and appends each JSON snapshot to a dedicated **`ops-metrics`
branch** (an orphan time-series that never merges to `main`, so the default
branch stays clean and a prior snapshot backs the substance deltas). On the
Monday schedule tick it additionally posts the short **weekly digest** comment
to the dashboard issue — the same numbers as fixed questions demanding a
reaction ("Replay calibration on N scored cell(s): lift over always-deny — do
you believe it?"), with the daily dashboard staying the reference view. It triggers
nothing and touches neither `main` nor the corpus.

It is also the **presenter** of the published corpus-side artifacts (see *Data
validation* in [data-pipeline.md](data-pipeline.md)): the corpus-writer path
produces a correctness verdict and the live-frontier readiness snapshot where
the corpus is already pulled, and `run-ops`
renders them as the **data-health** section and the substance section's
watchlist view, escalating a failing verdict to one
long-lived issue — so the dashboard surfaces run-health, data-health, and
substance while staying a read-only presenter that never touches the corpus.

`run-analytics` is the **corpus analysis & derived metrics** surface, also outside
the cascade: every task that reads the corpus and answers a question or refreshes a
derived artifact is a mode here (dispatch `mode` input, or the weekly schedule),
each as its own least-privilege job holding only the credentials its mode needs:

- **`corpus-stats`** (dispatch) assumes the read-only S3 role, pulls the
  corpus (`fedcourts corpus-pull`), and runs `fedcourts stats` to aggregate disposition base-rates (overall,
  filtered to one SCOTUS Term via the `term` input, or grouped by court / topic /
  judge / SCOTUS Term / disposition / originating circuit / decade era, with a
  cert-stage cut restricted to modern discretionary-cert dockets). Read-only: results go
  to the Actions step summary and run log, nothing else.
- **`metrics-refresh`** (weekly schedule, or dispatch) keeps the committed metrics
  artifacts from drifting stale: `metrics/leaderboard.json` (input: the `data/`
  evaluations ledger) and `metrics/backtest.json` / `metrics/statpack.{json,md}`
  (input: the corpus) are deterministic stage commands that previously only
  changed when someone reran them locally. It reruns those tested
  `fedcourts` commands and — only when an artifact actually changed (they are
  byte-stable, so a no-op refresh diffs empty) — opens a **reviewed** PR rendered
  by the tested `metrics-refresh-plan` command: never a
  direct commit to `main`, never auto-merged. This is the workflow's only
  write-capable job (it alone mints the dev App token). The branch is fixed
  (`metrics/refresh`) and force-pushed, so an unmerged refresh PR is updated in
  place by the next tick rather than stacking.

`integration-test` is the infrastructure preflight, also outside the cascade:
a manual-dispatch, strictly side-effect-free scenario runner over the **corpus
read backends, the two sidecars, and cascade cells** against the real corpus
remote — the tested `fedcourts corpus-integration-check` read set, a
cell's-eye probe of the service sidecar, the tokenless CourtListener MCP
sidecar under the tested `mcp-integration-check` client, a stub
`local-cascade` cell, or (the one token-spending scenario) a single
real-engine cell over the service sidecar — dispatched around changes to
corpus access, the sidecars, engine CLIs, or the corpus-consuming workflows
and before releases, from main or (via an approval-gated deployment
environment) from a PR branch. See *Infra-bound integration* in
[testing.md](testing.md).

**run-seed** runs the **historical Term walker** (supremecourt.gov, budget-free),
accumulating resolved outcomes reverse-chronologically by Term for the statpack's
per-Term base rates and the cert back-test set. It is a corpus writer split out
of run-pull so the backfill runs on a denser schedule (four dead-zone windows a
day); it shares the `corpus-write` concurrency group, so it still serializes with
run-pull's forward writers. **run-pull**'s **pull** job does targeted
CourtListener enrichment from the rate-limited **REST API** (it owns that budget;
the live job owns SCOTUS freshness for free). run-seed also runs the
**predict-scope reconcile** (`fedcourts reconcile-scope`), gated to one window a
day so it keeps the sweep's daily cadence: it latches out-of-scope cases (the
shared exclusion rules — era, staleness, docket form, date consistency, and the
snapshot-aware bare opinion-import profile) in the corpus so they leave the
predictable set at the source, then pushes the blob and commits the pointer like
any other corpus write. The full design — sources, budget boundary, the
corpus/ledger storage split, and the historical corpus — is in
[data-pipeline.md](data-pipeline.md).

## Cascade

```
daily ×4 → run-seed → walk Terms newest-first, ingest decided petitions (denials sampled)
                              └─ checkpointed: corpus-push + pointer commit per chunk
   daily ×4 / run:pull → run-pull (pull job) → open pull-log issue → push fresh facts to the corpus
                                 ├─ refresh active cases (oldest-first, budget-capped)
                                 ├─ detect resolution → write outcome.json when the
                                 │  disposition is machine-readable (git ledger);
                                 │  else queue an unrecorded outcome, surfaced
                                 │  per-case on the pull-log issue comment
                                 └─ create issues  ← APP TOKEN
                                    ├─ run:predict    (changed case with open events,
                                    │                  unless the docket already looks
                                    │                  decided — skipped + surfaced;
                                    │                  held if PREDICT_HANDOFF_ENABLED=0)
                                    └─ run:evaluate   (predicted event that gained
                                                       an outcome)
   daily ×4 → run-pull (live job) → open live-log issue → push fresh facts to the corpus
                                 ├─ probe supremecourt.gov docket-number frontier
                                 │  → onboard new petitions (per-Term cursor)
                                 ├─ re-poll the pending cert watchlist (recent Terms first)
                                 ├─ detect resolution from the proceedings text
                                 │  → write outcome.json (git ledger); else queue an
                                 │    unrecorded outcome, surfaced per-case on the
                                 │    live-log issue comment
                                 └─ create run:predict / run:evaluate issues  ← APP TOKEN
                                    (predict held if PREDICT_HANDOFF_ENABLED=0)
       run:predict → plan (build matrix) → predict[matrix] (artifact per cell)
                                 └─ collect → one auto-merged PR per run (+ a draft PR for partials)
       run:evaluate → plan → evaluate[matrix] (artifact per cell)
                                 └─ collect → one auto-merged PR per run (+ a draft PR for partials)
```

To run the predict → evaluate → validate cascade for one case **locally** — off
Actions, over the fixture corpus, offline by default — use `fedcourts
local-cascade` (see [cli.md](cli.md)). It reuses the same engine-runner seam and
registries, so a green local run mirrors a green CI run.

## ⚠️ The handoff token gotcha

Events created with the default `GITHUB_TOKEN` **do not trigger other workflows**
(GitHub's loop-prevention). So every cross-workflow handoff (e.g. run-pull creating
a `run:predict` issue) and every PR that must trigger CI is made with a **GitHub
App installation token** (`actions/create-github-app-token`), not `GITHUB_TOKEN`.
See `docs/security.md` for the one-time App setup.

## Authoring or changing a workflow

**Prefer a job or mode on an existing surface over a new workflow file.** GitHub
scopes permissions, secrets, and minted tokens per **job**, so a new job on an
existing workflow is exactly as least-privilege as a new file — a new file adds
surface area without adding isolation. A task earns its own workflow only when it
needs a different *trigger class* (the `run:*` issue-label cascade vs
schedule/dispatch) or a different *risk class* (the agentic fan-outs, the corpus
writers). Everything else — a new analysis, a new derived
artifact, a new maintenance sweep — should land as a mode/job on `run-analytics`
(or the closest existing surface), reusing the shared composite actions
(`setup-python-env`, `corpus-readonly`, `corpus-ranged`, `corpus-sidecar`,
`mcp-sidecar`, `configure-git-identity`).

When you add a new `run:*` workflow or edit one, the existing workflows are the
canonical reference — each handles these cross-cutting traps inline, so copy the
pattern rather than rediscovering it:

- **Concurrency is evaluated before the job `if`.** An `issues: labeled` event
  fans out to *every* workflow that listens for it, and the job-level label filter
  runs only after the concurrency group is assigned. A corpus writer job (pull, live, historical)
  must therefore join the shared `corpus-write` group **only** when its own label
  matched — otherwise an unrelated label cancels a real writer. See the
  `concurrency:` expression in `run-pull.yml`. To dispatch one of
  these reliably, prefer `workflow_dispatch` over labeling.
- **`git add data/` aborts when `data/` is absent.** No `outcome.json` is written
  on most runs, so `data/` often does not exist; under `set -euo pipefail` the add
  fails the step before the no-op guard. Stage the always-present pointer
  unconditionally and guard the rest with `if [ -d data ]; then git add data/; fi`
  (see `run-pull.yml`). The same shape lives in run-predict/evaluate.
- **Long-running jobs outlive their credentials.** A GitHub App installation token
  has a hard 1h life and an AWS OIDC session defaults to 1h. A corpus-writer loop
  must therefore stay within that hour, or re-mint the App token before it ages
  out and raise `role-duration-seconds` to cover the run. `run-seed`'s walk takes
  the first path: each window is a bounded chunk (≤40 min) under one token, so it
  needs no re-mint — a deliberate simplification over a longer walk that would.
- **The runner is ephemeral, so fixed per-run costs are re-paid every run.** Build
  expensive shared state once per job and reuse it across a loop's chunks rather
  than per chunk.

Validate any `.github/` change locally with the linters CI enforces (see the
local gate in [AGENTS.md](../AGENTS.md)), and run the **`workflow-reviewer`**
subagent (`.claude/agents/workflow-reviewer.md`) on the diff before pushing — it
runs those linters and reviews for what they miss (the security model and the
logic-in-tested-Python convention above).

## The predict/evaluate matrix

`plan` parses the issue body's ` ```json ``` ` case block and runs
`fedcourts predict-matrix` / `evaluate-matrix`, which expands the **registry ×
cases × events** into a GitHub Actions matrix. When prediction scope is gated
(`predict.scope=scotus_docket`) the builder reads each case's corpus row (only a
SCOTUS docket is in scope, minus the shared exclusion reasons), so `plan` first
pulls the corpus; with the gate on
and no corpus on disk the build fails loud rather than emit an empty matrix. Each
matrix cell routes to Claude Code, Codex, or Gemini by the entry's `engine`. The
agent writes files only. The workflow's `strategy.max-parallel` throttles the
whole fan-out, however many cases it spans.

If the matrix comes back **empty** — every queued case was out of scope (or already
predicted) — the `predict`/`evaluate` and `collect` jobs are skipped, so nothing
would otherwise close the trigger issue; the `plan` job closes it with a note
instead of leaving it orphaned open. (Pull avoids filing such all-out-of-scope runs
in the first place; this is the backstop for a manually-filed or partial one.)

How a cell's output becomes a PR is the same across **`run:predict`** and
**`run:evaluate`**: each cell validates its own output and
uploads it (plus a status file) as an artifact rather than opening a PR, and a
final **`collect`** job unions the run's artifacts into **one PR** — auto-merged
once `gate` + `paths` are green, and closing the triggering issue on merge — with
any salvageable partial output split into a single companion **draft** PR. So a
fan-out of dozens of cells yields one (or two) PRs for the run, not one per cell.
The append-only `data/` path jail (`fedcourts assert-paths`) is enforced in
`collect` before the commit and again as the required `paths` check, so an
auto-merged PR can only add artifacts under `data/`; a schema re-validation and a
secret scan (`fedcourts scan-diff-for-secrets`) run beside it producer-side —
a validation failure downgrades the PR to a draft, while a secret-scan hit
**withholds the branch entirely** (nothing pushed; a redacted report lands on
the trigger issue) since the push itself would publish the secret (see
[security.md](security.md)).

For `run:predict` and `run:evaluate`, `collect` also rolls up any
agent feedback (`flags.json`) the run surfaced and posts it three ways — each
gated on the run's secret scan, since flag messages are agent free text — the run PR
body, the Actions summary, and one long-lived **agent-feedback** tracking issue (the
single latched-issue pattern of `ops-dashboard` / `data-validation` / `pipeline-health`) — so a note
reaches a durable, centralized home even when a fully-failed run opens no PR.
The `run-seed` historical walker has its own instance of that pattern: a `guard`
job raises one long-lived **pipeline-health** issue if the checkpointed walk is
ever cancelled or fails (e.g. a chunk overran the job's hard timeout), and clears
it when a later walk finishes clean — so a silent, PR-less writer failure still
reaches a durable home.
Separately, every cell may also write a `tooling.json` self-report on its
environment/tooling, committed with the cell's output rather than rolled into the
per-run PR/issue; the `run-ops` dashboard scans these into a tooling-feedback
digest. See the `flags.json` and `tooling.json` channels in
[data-pipeline.md](data-pipeline.md).

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
multiplied by the registry and its events to produce one matrix cell per
predictor/evaluator × case × event — which `run:predict` and `run:evaluate`
collect into one PR for the run.

`predictors` is also optional per case and narrows the `run:predict` fan-out to
the named registry ids:

    ```json
    {"court": "scotus", "docket": 24001, "predictors": ["codex-baseline"]}
    ```

This is the **engine backfill** path: when one engine's cells failed (a quota
or provider outage) while the others delivered, re-firing the full registry
would re-run — and duplicate the committed predictions of — the healthy
engines: only resolved events are excluded (via default open-event
resolution), so an open event re-mints cells for every enabled predictor
regardless of which engines already committed a prediction. Naming an id that is
not an enabled predictor fails the plan job rather than silently skipping the
engine. `run:evaluate` ignores the field: an evaluator always scores every
committed prediction for its event.

## Unrecorded outcomes: what pull's outcome detection leaves behind

`run-pull` records `outcome.json` itself only when a decided docket is
unambiguous (a machine-readable disposition, a decision date, and a single open
event). Everything else — an unreadable/absent disposition, no decision date, or
a case-level disposition that cannot be attributed across several open events —
becomes an **unrecorded outcome** (it does not guess): the case lands on the
runner-local unrecorded queue (`unrecorded-queue.json`, the `UnrecordedOutcome`
detection in the library) instead of the git ledger. No issue is filed for
these. Both the pull and live jobs surface each one per-case on the day's
pull-log / live-log issue comment ("court/docket — reason"), with the count on
the Actions step summary, for maintainer triage — recording nothing beats a
guess.

## Recovering a run whose `collect` failed

`collect` is the single writer for a run's agent output, so its failure used to
discard the whole run — on 2026-07-18 one transient artifact-download failure
threw away 46 successful cells. It now degrades per artifact, and what it could
not collect is named rather than silently dropped. Two gaps, two remedies:

| the PR body / run log says | what happened | fix |
|---|---|---|
| *artifact did not transfer* | the cell likely succeeded; its output still exists | **re-run the `collect` job** |
| *no cell output at all* | the cell died before it could report | **re-queue** — no rerun helps |

Either gap keeps the trigger issue open, so a run never auto-merges presenting
itself as complete while omitting cells.

**Re-running collect is safe and repeatable.** `gh run rerun --failed`
re-executes only the failed job; the artifact listing is per-run, so it re-lists
and re-fetches the original attempt's uploads. The loop force-pushes its
run-scoped branch, finds-or-updates the PR (reconciling draft state), and
marker-dedupes the trigger-issue reports, so nothing stacks or aborts on a
second pass. A kind whose PR already merged is skipped.

Two caveats:

- **Cell artifacts are retained 7 days.** After that a transfer-lost cell is
  gone and only a re-queue recovers it.
- **`--failed` also re-runs failed *cells*,** and `upload-artifact` rejects a
  duplicate artifact name within a run, so those re-run cells fail at upload.
  `--failed` is the recovery for a *collect-only* failure; when cells failed
  too, re-apply the `run:*` label instead.

A rerun discards hand-edits to an unmerged draft branch — it is rebuilt from the
artifacts. Finish a draft by merging it, not by editing and then re-running.

## Graceful degradation on limits

Agent steps (predict, evaluate) are bounded by a step-level
`timeout-minutes` set below the job's, so a run that overruns trips the *step* —
not the job. A step timeout (or a max-turns stop) fails only that step and leaves
the runner alive, so the salvage step still runs (`if: !cancelled()`) and the
agent's partial work survives instead of being discarded with the cancelled job.

What salvage looks like is uniform across **`run:predict`** and
**`run:evaluate`**: each cell records its status and uploads its output
(`if: !cancelled()`); the `collect` job then routes a cell that did not finish
cleanly — or whose output failed schema validation — into the run's **draft** PR
(never the auto-merging ready one), and a cell that produced nothing is warned
about rather than committed. A run that finished cleanly is
unaffected: the draft path only triggers when the agent stopped early.

## Pausing the tournament without pausing ingestion

`seed`/`pull`/`live` (cheap, API-budgeted) and `predict` (the model spend) can be
run independently. One variable holds the predict fan-out at the handoff seam:

| Variable | Unset | Effect when `0` or `false` |
|---|---|---|
| `PREDICT_HANDOFF_ENABLED` | `1` — files | `run:predict` issues are not filed |

Set it in the `runner` environment (a repository-level variable of the same name
works identically, unless an environment-level one shadows it). It defaults to
filing, so an unset or mistyped variable keeps the tournament running: the
failure that costs coverage is the quiet one. Ingestion is untouched — the corpus
keeps refreshing and outcomes keep being recorded, so a pause costs prediction
coverage for that window, never data.

**Holding predict is lossless, and resuming needs no backfill.** The predict
queue lives in the corpus, not in the issue — the issue is only a trigger
carrying a snapshot of it. A **selected** case stays queueable for as long as it
has open, never-predicted events, and the live channel's selection sweep re-polls
exactly that set each cycle (`pipeline/live.py`, gated on `event_has_predictions`
from `matrix.py`), debounced to daily by `predict_queued_at`. So a held window
never needs its issue re-filed or re-opened.

The drain is paced, not instant: the sweep is capped at
`salience.sweep_cases_per_cycle` (25 in `config/tracking.yaml`) and works stalest
first, so a backlog larger than the cap spreads over the following cycles — the
same behaviour [salience.md](salience.md) describes. A case that is unselected or
latched out of scope is never re-queued at all.

Held windows are marked **held** on the run log and step summary rather than
reported as dispatched, so a growing backlog is legible as a paused channel and
not misread as a stalled fan-out.

### Why there is no `EVALUATE_HANDOFF_ENABLED`

The evaluate queue is **edge-triggered** and one-shot, so the same treatment
would silently destroy data. It is built from `result.resolved` — events that
*this poll* closed — and `upsert_events` is resolved-latching, so no later poll
re-emits them. There is no evaluate sweep, no `evaluate_queued_at`, and nothing
that derives an evaluate backlog from corpus state.

A held evaluate window would therefore be lost permanently, and lost *silently*:
the corpus push and the outcome commit both land before the handoff step, so the
outcomes would be recorded and the predictions would exist with nothing left to
ever grade them. Evaluate volume is also small — one cell per evaluator on newly
resolved events, against predict's case × predictor fan-out — so it is not where
the spend is. For `run:evaluate`, the open issue *is* load-bearing queue state,
not merely a trigger; if one must be stopped, close it deliberately and use the
[single-issue manual path](#the-predictevaluate-matrix) to recover.

### Disabling the workflow is not the same as holding the handoff

Disabling `run-predict` / `run-evaluate` in the GitHub UI stops the *runs* but
not the *issues*. The issues keep arriving and sit unconsumed — and `run-ops`
lists every still-open `run:*` issue as a **stalled fan-out**, so a
workflow-disabled-only pause steadily reddens the ops dashboard with what looks
like broken runs. Holding the handoff avoids that; for a full predict pause, do
both.

## Snapshot sequencing

`run-pull` pushes factual snapshots **to the corpus** — the per-case content
store plus the `corpus-push` of the index — before it queues `run:predict`, so
`run-predict` — a read-only corpus consumer (its plan job reads the index in
place over the ranged backend; its cells provision from the content store and
query the index through the credential-holding corpus sidecar) — sees the
snapshot it must predict from. Raw facts never go through PRs (they are
CourtListener data, not agent output); agent outputs (predictions, evaluations)
always do.
