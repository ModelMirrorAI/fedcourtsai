# CLI reference (`fedcourts`)

`fedcourts` is a thin wrapper over the library, used by humans, scripts, and the
pipeline workflows. Run `uv run fedcourts --help` for the live listing, or
`uv run fedcourts <command> --help` for a command's flags; this page is the
grouped overview. `--version` prints the installed package version.

Commands fall into five groups: **ingestion** (write the corpus), **corpus
inspection** (read it), **validation** (the gate), **metrics & reporting**, and
**agent support** (fan-out matrices and registries). For the design behind the
corpus/ledger split see [data-pipeline.md](data-pipeline.md) and
[data-model.md](data-model.md); for how the workflows wire these together see
[pipeline.md](pipeline.md).

Where a command writes a roll-up under `metrics/`, the path is relative to the
configured metrics root and `--out`/`--json` overrides it.

## Ingestion — write the corpus

Onboard and refresh raw facts. `seed`/`pull`/`discover`/`pull-all` use the
rate-limited CourtListener **REST API** (need an API token); `seed-backfill` uses
the public **bulk** snapshot (no token, no budget). All ingest through the same
core, so the corpus is written identically.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `seed` | Onboard one docket from the REST API into the corpus. | `--court`, `--docket` |
| `pull` | Refresh one already-onboarded docket and report whether it changed. | `--court`, `--docket` |
| `seed-backfill` | Load the next chunk of CourtListener bulk data, advancing the committed cursor. The `run-seed` workflow loops it. | `--max-cases`, `--report`, `--staging-path` |
| `discover` | Onboard newly-filed dockets in the tracked courts, advancing each court's watermark. | `--since`, `--limit` |
| `pull-all` | Refresh the stalest tracked cases within the API budget; write the predict/evaluate/reconcile handoff queues. | `--limit`, `--out`, `--evaluate-out`, `--reconcile-out` |

`--limit` / `--max-cases` may only *lower* the per-run cap from
`config/`, never raise it, so a run provably stays within budget.

## Corpus inspection — read the corpus

Read-only views, run after a `dvc pull` provisions the corpus.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `corpus-info` | Show the packed corpus location, row count, and snapshot count. | — |
| `query` | Retrieve relevant priors for a predictor, most relevant first, one JSON row per line. | `--court`, `--topic`, `--judge`, `--citation`, `--disposition`, `--include-open`, `--limit`, `--full` |
| `open-events` | Print a case's unresolved (predictable) event ids, one per line. | `--court`, `--docket` |
| `provision-snapshot` | Materialize a case's latest corpus snapshot to disk for an agent run. | `--court`, `--docket`, `--out` |
| `paths` | Print the resolved corpus/case/event paths for a case. | `--court`, `--docket`, `--event` |

## Validation — the gate

The offline checks the PR gate can run without the DVC remote.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `validate` | Validate the git ledger under a path: schema conformance plus git-only references. This is what CI runs on every PR. | `PATH` (default `data`) |
| `validate-corpus` | Open the corpus and assert the cross-store integrity + referential invariants, emitting a `CorpusValidation` verdict. Skips gracefully when the corpus is absent. | `--out`, `--baseline-count`, `--today` |
| `dvc-status` | Check the committed DVC metadata is internally consistent — the offline half of `dvc status`. | `PATH` (default `.`) |

## Metrics & reporting

Deterministic roll-ups (committed) and point-in-time snapshots (surfaced, not
committed), plus the spend ledger.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `leaderboard` | Rank predictors from the evaluations ledger into `metrics/leaderboard.json`. | `--out` |
| `backtest` | Replay the reference predictors over resolved corpus events into `metrics/backtest.json`. | `--out`, `--court`, `--limit` |
| `ops-report` | Roll pipeline health, backfill progress, spend, and data health into the ops dashboard Markdown (and optional JSON). | `--runs`, `--json`, `--previous`, `--generated-at`, `--corpus-validation`, `--data-health-out` |
| `record-usage` | Record one run's measured token usage and estimated cost next to its prediction/evaluation output. | `--court`, `--docket`, `--event`, `--run-id`, `--engine`, `--role`, `--actor`, `--model`, `--*-tokens`, `--claude-execution-file`, `--codex-sessions-dir` |
| `usage-summary` | Sum the recorded `usage.json` ledger into an actual \$/run, as JSON on stdout. | — |

## Agent support — matrices, registries, schemas

Helpers the workflows and agents use to fan out and stay in contract.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `predict-matrix` | Emit the predictor × case × event GitHub Actions matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `evaluate-matrix` | Emit the evaluator × case × event matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `reconcile-matrix` | Emit the per-case `run-reconcile` matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `predictors` | List configured predictors (id, engine, model, enabled). | — |
| `evaluators` | List configured evaluators (id, engine, model, enabled). | — |
| `export-schemas` | Write JSON Schema for every pydantic model into `schemas/` (for agents and Codex `--output-schema`). CI fails if the committed schemas drift. | `OUT` (default `schemas`) |
