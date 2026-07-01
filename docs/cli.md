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
core, so the corpus is written identically. `make-fixture-corpus` is the odd one
out: it writes a tiny **synthetic** corpus from hard-coded facts (no source, no
network) for offline local runs and tests, never a substitute for the real corpus.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `seed` | Onboard one docket from the REST API into the corpus. | `--court`, `--docket` |
| `pull` | Refresh one already-onboarded docket and report whether it changed. | `--court`, `--docket` |
| `seed-backfill` | Load the next chunk of CourtListener bulk data, advancing the committed cursor. The `run-seed` workflow loops it. | `--max-cases`, `--report`, `--staging-path` |
| `discover` | Onboard newly-filed dockets in the tracked courts, advancing each court's watermark. | `--since`, `--limit` |
| `pull-all` | Refresh the stalest tracked cases within the API budget; write the predict/evaluate/reconcile handoff queues. | `--limit`, `--out`, `--evaluate-out`, `--reconcile-out` |
| `full-refresh` | Reset the seed cursor + corpus forward cursors so the whole tracked set re-seeds and re-pulls fresh (history preserved). Run by `run-seed` on the `full_refresh` dispatch input. | `--dry-run`, `--report` |
| `make-fixture-corpus` | Build a tiny deterministic synthetic corpus (cases/events/snapshots across several courts) so the read commands work offline, no remote. | `--out` |

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
| `materialize-event` | Project a predictable event's `event.yaml` from the corpus into the git ledger. | `--court`, `--docket`, `--event`, `--out` |
| `paths` | Print the resolved corpus/case/event paths for a case. | `--court`, `--docket`, `--event` |

## Validation — the gate

The offline checks the PR gate can run without the DVC remote.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `validate` | Validate the git ledger under a path: schema conformance plus git-only references. This is what CI runs on every PR. | `PATH` (default `data`) |
| `validate-corpus` | Open the corpus and assert the cross-store integrity + referential invariants, emitting a `CorpusValidation` verdict. Skips gracefully when the corpus is absent. | `--out`, `--baseline-count`, `--today` |
| `corpus-scope-audit` | Census the corpus's still-open SCOTUS events that the predict scope excludes (pre-1925 mandatory jurisdiction #309, stale unresolvable #333, inconsistent dates #171), with a recoverable-vs-bare split, plus a breakdown of the *unclassified* open events (why each stays in scope) and a docket-number **shape histogram** for the not-parseable bucket — the #343 refinement signal (the concrete formats a Term-parser broadening would target). The read-only input for the seed-side corpus reconcile. Emits a `CorpusScopeAudit`; skips gracefully when the corpus is absent. | `--out` |
| `dvc-status` | Check the committed DVC metadata is internally consistent — the offline half of `dvc status`. | `PATH` (default `.`) |

## Diagnostics — read-only probes

Measurements a maintainer runs to answer a build question, writing nothing.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `probe-recoverability` | For sparse dockets, fetch the docket, its entries, and any linked opinion cluster from the CourtListener **REST API** and classify the disposition as **RECOVERABLE** (an ingestion gap a seed/pull backfill can close — with the source: entry-order / cluster-disposition / citation / date_terminated), **ABSENT** (genuinely bare upstream), or **AMBIGUOUS**. Strictly read-only: touches no corpus, `data/`, DVC, or git. Emits the `ProbeReport` JSON on stdout and a Markdown summary on stderr; `--summary-out` also appends the summary to a file (e.g. the Actions step summary). Needs a REST token, so it is dispatched by the `run-recoverability-probe` workflow. | `--dockets`, `--summary-out` |

`--dockets` takes one or more `court/docket` pairs, repeated and/or comma-separated
(e.g. `--dockets scotus/1000512,scotus/1000515`).

## Metrics & reporting

Deterministic roll-ups (committed) and point-in-time snapshots (surfaced, not
committed), plus the spend ledger.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `leaderboard` | Rank predictors from the evaluations ledger into `metrics/leaderboard.json`. | `--out` |
| `backtest` | Replay the reference predictors over resolved corpus events into `metrics/backtest.json`. | `--out`, `--court`, `--limit` |
| `ops-report` | Roll pipeline health, backfill progress, spend, open agent flags, agent tooling feedback, data health, and the out-of-scope-open-events census into the ops dashboard Markdown (and optional JSON). | `--runs`, `--json`, `--previous`, `--generated-at`, `--corpus-validation`, `--scope-audit`, `--data-health-out` |
| `record-usage` | Record one run's measured token usage and estimated cost next to its prediction/evaluation output. | `--court`, `--docket`, `--event`, `--run-id`, `--engine`, `--role`, `--actor`, `--model`, `--*-tokens`, `--claude-execution-file`, `--codex-sessions-dir` |
| `usage-summary` | Sum the recorded `usage.json` ledger into an actual \$/run, as JSON on stdout. | — |

## Agent support — matrices, registries, schemas

Helpers the workflows and agents use to fan out and stay in contract.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `predict-matrix` | Emit the predictor × case × event GitHub Actions matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `evaluate-matrix` | Emit the evaluator × case × event matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `reconcile-matrix` | Emit the per-case `run-reconcile` matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `authorize-trigger` | Authorize a `run:*` label trigger (Bot handoff or write collaborator), or refuse and exit non-zero. The fan-out workflows call it before any privileged step. | `--sender-type`, `--actor`, `--repo` |
| `finalize-produced` | Print `true`/`false` for whether the agent wrote its own judgment artifact (prediction/evaluation), so a cell with only the pre-materialized event scaffold is reported as producing nothing. | `--role`, `--court`, `--docket`, `--event`, `--actor`, `--run-id` |
| `assert-paths` | Enforce the append-only `data/` path jail on a change set (`git diff --name-status`): exit non-zero on any path outside `data/` or any non-addition. The collect jobs and the required CI `paths` check both call it. | `--name-status-file`, `--run-id` |
| `collect-plan` | Emit the per-run aggregate PR decision for predict/evaluate — one ready PR (auto-merged, closing the trigger issue) plus a draft for salvageable partials — as compact JSON. | `--role`, `--run-id`, `--status-dir`, `--issue` |
| `collect-reconcile-plan` | Emit the per-run aggregate reconcile PR decision (per case) as compact JSON; the ready PR's `reconcile:` commit fires the evaluate handoff on merge. | `--run-id`, `--status-dir`, `--issue` |
| `post-agent-feedback` | Latch a predict/evaluate run's agent-flag roll-up (`collect-plan`'s `feedback_comment`) onto the single long-lived `agent-feedback` issue: find-or-create, post once (marker-deduped). The collect job calls it with the ambient `GITHUB_TOKEN`. | `--body-file`, `--repo` |
| `predictors` | List configured predictors (id, engine, model, enabled). | — |
| `evaluators` | List configured evaluators (id, engine, model, enabled). | — |
| `export-schemas` | Write JSON Schema for every pydantic model into `schemas/` (for agents and Codex `--output-schema`). CI fails if the committed schemas drift. | `OUT` (default `schemas`) |

## Maintenance — corpus-informed cleanup

Deterministic sweeps that prune already-merged derived artifacts the append-only
writers can never remove. They need the corpus, so they run in `run-cleanup`
(`dvc pull`'d) and land as a **reviewed** (not auto-merged) PR.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `cleanup-out-of-scope-predictions` | Prune committed predictions for cases now out of predict scope — pre-1925 mandatory jurisdiction (#309) or stale unresolvable old SCOTUS petitions (#333), gated on the real corpus row (the same predicates `predict-matrix` drops on). The event definition and any `outcome.json` stay; only the predictions go. Prints `{"prunable":[…],"removed":<bool>}`; dry-run by default. | `--apply` |
| `reconcile-scope` | The **corpus**-side counterpart: over the predict-eligible cases, latch `predict_excluded` on those an exclusion predicate now matches (#309 / #333 / inconsistent dates #171) and clear it on those back in scope, so `open-events` drops them at the source. Run where the corpus is pulled (seed), `dvc push` after; prints a `ScopeReconcileResult`. Dry-run by default. | `--apply` |
| `assert-cleanup-paths` | Enforce the **cleanup jail** on a change set (`git diff --name-status`): exit non-zero unless every change is a *delete* under a `data/cases/**/events/*/predictions/` subtree. The cleanup job and the required CI check both call it — the destructive counterpart to `assert-paths`. | `--name-status-file` |

## Local iteration — the full cascade off Actions

`local-cascade` is the repeatable, local form of the "one full cascade proven"
milestone: it drives a single case through the whole derived-artifact pipeline —
**provision → predict → evaluate → validate** — without GitHub Actions, the
iteration loop that otherwise only runs inside `run-predict` / `run-evaluate`. It
reuses the production seams (the engine-runner, the predictor/evaluator
registries, the packed corpus) so a green local run faithfully predicts a green
CI run.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `local-cascade` | Provision a case's snapshot, predict it with every enabled predictor, evaluate the resulting predictions with every enabled evaluator, and validate the produced ledger. | `--court`, `--docket`, `--event`, `--engine`, `--run-id` |

It reads the case from the packed corpus — point it at the synthetic fixture
(`make-fixture-corpus`) for a fully offline run, or a real `dvc pull`-provisioned
one. With no `--event` it runs every event the case defines; a resolved event also
gets its ground-truth `outcome.json` materialized so the evaluate stage has
something to score. The derived artifacts land under `data/` exactly as a real run
would — **review and discard them**, don't commit a local cascade's output.

**Engines.** `--engine` selects the backend for every cell:

- `stub` (default) — the deterministic, offline, token-free reference engine.
  This is the acceptance path: valid artifacts end to end with no network.
- `replay` — also offline, but emits a **captured real prediction** from the
  cassette at `FEDCOURTS_REPLAY_ROOT` (a committed recording under `tests/cassettes`)
  instead of the stub's trivial floor. The recorded forecast carries a real
  probability and panel votes, so the scoring metrics and leaderboard roll-up run
  over realistic output; identity fields are rebound to each cell. Set
  `FEDCOURTS_REPLAY_ROOT` or the command errors clearly.
- `claude-code` / `codex` — drive the **real** headless agents (`claude`, `codex`)
  over the same env-var + prompt-file contract the workflows use, so the cells are
  byte-identical in shape to a CI run. The `claude` CLI ships in the devcontainer
  (`codex` you install yourself).

**Auth for the real engines.** Credentials are inherited from the environment,
never assembled by the command. For Claude, set either:

- `ANTHROPIC_API_KEY` — pay-per-token, exactly as CI meters automated inference; or
- `CLAUDE_CODE_OAUTH_TOKEN` — the **subscription** OAuth token from
  `claude setup-token`, so local iteration draws on your Claude subscription
  instead of billing per token. This mirrors the `claude_code_oauth_token` fallback
  noted in `run-predict.yml`.

For Codex, set `OPENAI_API_KEY`.
