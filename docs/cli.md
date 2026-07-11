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

Onboard and refresh raw facts. `pull`/`discover`/`pull-all` use the
rate-limited CourtListener **REST API** (need an API token); `live-poll` and
`historical-terms` use the **supremecourt.gov docket JSON** (no token, no
budget — the SCOTUS live channel, [live-sources.md](live-sources.md)). All
ingest through the same core, so the corpus is written identically. `make-fixture-corpus` is the
odd one out: it writes a tiny **synthetic** corpus from hard-coded facts (no
source, no network) for offline local runs and tests, never a substitute for the
real corpus.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `pull` | Onboard or refresh one docket from the REST API and report whether it changed (the first pull onboards). | `--court`, `--docket` |
| `historical-terms` | Load one capped chunk of the historical per-Term set through the live channel: walk the configured October Terms' docket serials sequentially (persisted per-(Term, stream) cursors, so runs resume) and ingest every decided petition except denials, which are systematically sampled per `historical:` in `config/tracking.yaml` — the committed sampling frame. Ingested petitions land already resolved (label, snapshot, events, OT2021+ documents) and feed the statpack's per-Term base rates and replay/evaluation only; **writes no handoff queues**. The `run-pull` workflow's `historical` job loops it. | `--report`, `--totals`, `--max-probes`, `--summary-out` |
| `discover` | Onboard newly-filed dockets in the tracked courts, advancing each court's watermark (dormant in production: `pull.discover_new_filings` is off — the live channel onboards SCOTUS filings). | `--since`, `--limit` |
| `pull-all` | Refresh the stalest tracked cases within the API budget; write the predict/evaluate handoff queues plus the unrecorded-outcome queue (decided but not deterministically recordable, surfaced on the run log). | `--limit`, `--out`, `--evaluate-out`, `--unrecorded-out` |
| `live-poll` | One SCOTUS live-channel cycle: probe the Term's docket-number frontier for new petitions (persisted per-Term cursor), re-poll the pending watchlist (distributed petitions first, nearest conference first), detect resolution from the proceedings text, and write the same three queues as `pull-all` — with predict queued on **distribution transitions** (fresh distribution or relist), the cert-calendar predict trigger. | `--term`, `--limit`, `--out`, `--evaluate-out`, `--unrecorded-out` |
| `make-fixture-corpus` | Build a tiny deterministic synthetic corpus (cases/events/snapshots across several courts) so the read commands work offline, no remote. | `--out` |

`--limit` / `--max-probes` may only *lower* the per-run cap from
`config/`, never raise it, so a run provably stays within budget.

## Corpus inspection — read the corpus

Read-only views. They read the `dvc pull`-ed file by default; where
`--corpus-backend` is listed, `ranged` queries the immutable blob in place on
the DVC remote instead (per-query egress in KBs, read stats echoed to stderr;
see *The ranged read backend* in [data-pipeline.md](data-pipeline.md)).

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `corpus-info` | Show the packed corpus location, row count, and snapshot count. | `--corpus-backend` |
| `query` | Retrieve relevant priors for a predictor, most relevant first, one JSON row per line. Each row carries the case caption and a derived decade `era` (Term year, else filing/decision date) so relevance is judgeable; `--era` restricts retrieval to one period. `--decided-before` is the back-test replay clock — an exclusive year cutoff keeping only priors that provably precede it (rows with no derivable year are excluded); live forward prediction omits it, and a replay cell reads it from `DECIDED_BEFORE`. | `--court`, `--topic`, `--judge`, `--citation`, `--disposition`, `--era`, `--decided-before`, `--include-open`, `--limit`, `--full`, `--corpus-backend` |
| `stats` | Aggregate disposition **base-rates** over the corpus — the aggregate counterpart of `query`. Rolls the matched set into overall base-rates and, with `--group-by`, a per-group breakdown (court / topic / judge / SCOTUS `term_year` / disposition / `originating_court`, the circuit-scorecard cut / `era`, the decade bucket usable on rows `--term` cannot parse). Shares the `query` filter grammar plus a `--date-from`/`--date-to` filed-date window, a `--term` SCOTUS October-Term filter (SCOTUS cases only — other courts' docket numbers never match), an `--era` decade filter, and `--cert-stage`, which keeps only modern Term-prefixed discretionary-cert dockets — the calibration anchor for cert predictions. Emits an `AnalyticsReport` JSON on stdout and a Markdown summary on stderr; `--summary-out` also appends the summary to a file. Skips gracefully (exit 0) when the corpus is absent. | `--court`, `--topic`, `--judge`, `--citation`, `--disposition`, `--date-from`, `--date-to`, `--term`, `--era`, `--cert-stage`, `--resolved-only`, `--group-by`, `--summary-out` |
| `open-events` | Print a case's unresolved (predictable) event ids, one per line. | `--court`, `--docket`, `--corpus-backend` |
| `conference-set` | The pending-before-conference set: every pending modern-cert petition with a parsed "DISTRIBUTED for Conference of …" membership, grouped by conference date — the live cert watchlist the September long-conference report reads off. `--out` also writes the per-petition JSON. | `--out` |
| `live-frontier` | Snapshot the live cert watchlist's readiness for the ops dashboard: watchlist size, the distribution calendar with the next conference relative to `--today`, and how many watchlist petitions carry provisioned filed-document text. Produced where the corpus is pulled and published to the `ops-metrics` branch (the corpus-writer path) so the corpus-free `run-ops` presenter can render it. Emits a `LiveFrontier`; skips gracefully when the corpus is absent. | `--out`, `--today` |
| `provision-snapshot` | Materialize a case's latest corpus snapshot to disk for an agent run — plus any stored filed-document text (petition, questions presented, brief in opposition — fetched pipeline-side by the live poller) under `record/documents/` with a `documents.json` manifest, and the cell's mode context (`record/context.json`). | `--court`, `--docket`, `--out`, `--mode`, `--corpus-backend` |
| `corpus-integration-check` | Run the fixed read set the `integration-corpus` workflow dispatches — a point lookup (open events), a priors retrieval, a snapshot provisioning — each on its own connection so a ranged run reports per-read GET/byte counters. Emits the machine report JSON on stdout and a Markdown summary on stderr; `--summary-out` also appends the summary. Exits non-zero on any empty read or a blown wall-clock budget. | `--court`, `--docket`, `--limit`, `--budget-seconds`, `--snapshot-out`, `--summary-out`, `--corpus-backend` |
| `materialize-event` | Project a predictable event's `event.yaml` from the corpus into the git ledger. | `--court`, `--docket`, `--event`, `--out`, `--corpus-backend` |
| `paths` | Print the resolved corpus/case/event paths for a case. | `--court`, `--docket`, `--event` |

## Validation — the gate

The offline checks the PR gate can run without the DVC remote.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `validate` | Validate the git ledger under a path: schema conformance plus git-only references. This is what CI runs on every PR. | `PATH` (default `data`) |
| `validate-corpus` | Open the corpus and assert the cross-store integrity + referential invariants, emitting a `CorpusValidation` verdict. Skips gracefully when the corpus is absent. | `--out`, `--baseline-count`, `--today` |
| `corpus-scope-audit` | Census the corpus's still-open SCOTUS events that the predict scope excludes, per exclusion reason (the shared rules: era, staleness, published-opinion, non-cert docket form, disbarment, consolidated-member agreement, date consistency, and the snapshot-aware bare opinion-import profile), with a recoverable-vs-bare split, plus a breakdown of the *unclassified* open events (why each stays in scope) and a docket-number **shape histogram** for the not-parseable bucket — the scope-refinement signal (the concrete formats a Term-parser broadening would target). A shape under ~100 open events is an accepted fragment: it stays visible in the histogram by design, and no exclusion predicate is chased for it. The read-only counterpart of `reconcile-scope`, for ad-hoc scope triage. Emits a `CorpusScopeAudit`; skips gracefully when the corpus is absent. | `--out` |
| `dvc-status` | Check the committed DVC metadata is internally consistent — the offline half of `dvc status` — and, when the corpus blob is present locally, that its physical layout matches the ranged-read contract (64 KB pages, non-WAL at rest). | `PATH` (default `.`) |

## Diagnostics — read-only probes

Measurements a maintainer runs to answer a build question, writing nothing.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `probe-recoverability` | For sparse dockets, fetch the docket, its entries, and any linked opinion cluster from the CourtListener **REST API** and classify the disposition as **RECOVERABLE** (an ingestion gap a pull re-fetch can close — with the source: entry-order / cluster-disposition / citation / date_terminated), **ABSENT** (genuinely bare upstream), or **AMBIGUOUS**. Strictly read-only: touches no corpus, `data/`, DVC, or git. Emits the `ProbeReport` JSON on stdout and a Markdown summary on stderr; `--summary-out` also appends the summary to a file (e.g. the Actions step summary), `--report-out` also writes the JSON to a file (e.g. for a run artifact). Needs a REST token, so it is dispatched by the `run-analytics` workflow (recoverability / recoverability-sample modes). | `--dockets`, `--sample-dateless`, `--seed`, `--report-out`, `--summary-out` |
| `probe-live-terms` | The live-sources reachability probe: for each October Term from `--max-term` back to `--min-term`, fetch a small sample of `supremecourt.gov` docket-JSON numbers and report availability, document-link coverage, schema stability, and whether the proceedings text carries machine-matchable disposition orders. Strictly read-only and budget-free — the supremecourt.gov channel, not the CourtListener client (no token, no governor; browser UA + ~1 req/s politeness built in). Emits per-Term/per-record JSON on stdout and the Markdown findings table on stderr. Findings + the Term-floor decision: [live-sources-probe.md](live-sources-probe.md). | `--max-term`, `--min-term`, `--numbers`, `--throttle`, `--report-out`, `--summary-out` |

Targets come from exactly one of two flags. `--dockets` takes one or more
`court/docket` pairs, repeated and/or comma-separated (e.g.
`--dockets scotus/1000512,scotus/1000515`). `--sample-dateless N` instead draws a
deterministic stratified random sample of N resolved-but-dateless corpus rows
(strata: SCOTUS modern-cert, ca4, other circuits pooled; `--seed` fixes the draw)
— it needs the corpus on disk (`dvc pull`), and the summary then adds a
per-stratum verdict rollup plus the corpus's dated share at probe time.

## Metrics & reporting

Deterministic roll-ups (committed) and point-in-time snapshots (surfaced, not
committed), plus the spend ledger.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `leaderboard` | Rank predictors from the evaluations ledger into `metrics/leaderboard.json`. | `--out` |
| `backtest` | Replay the reference predictors over resolved corpus events into `metrics/backtest.json`. The prior-vote baseline is **time-masked**: it votes only over priors that provably precede each trial's own year, and a trial with no derivable year gets the conservative floor rather than a hindsight vote. | `--out`, `--court`, `--limit` |
| `cert-backtest` | Back-test cert predictors over the most recently decided modern discretionary-cert petitions (outcome hidden), scoring accuracy, Brier, **lift over the always-deny floor**, and a P(granted) calibration view into `metrics/cert-backtest.json` — labeled retrospective. Offline reference baselines always run; `--engine auto` additionally replays every enabled predictor over **redacted snapshots** in a scratch tree, each through its **own configured engine** (an apples-to-apples read; a predictor whose engine has no registered runner is skipped and named, never mislabeled through another engine), while a concrete backend (`stub`, `replay`, `claude-code`, `codex`) routes every predictor through that one backend for offline runs and single-engine sweeps. Spends tokens on a real engine; never writes `data/`. Petitions with no held snapshot or petition event are dropped up front and named, so all backtesters in one report score the same set; each cell's `DECIDED_BEFORE` is the trial's year, so the agent's own corpus retrieval is time-masked too. | `--out`, `--limit`, `--engine`, `--work-dir` |
| `statpack` | Roll the corpus into a base-rate **statpack** — headline counts, filing→decision timing, curated breakdowns (by court, SCOTUS petitions by topic and by **originating circuit**), and a per-SCOTUS-Term detail array (base rates + timing per Term, recent first; the Markdown shows the latest 10) — into `metrics/statpack.{json,md}`. Deterministic and offline; writes the empty pack when the corpus is absent. | `--out`, `--markdown-out` |
| `ops-report` | Roll pipeline health, **substance** (scored cells by stratum with deltas vs `--previous`, replay calibration vs the statpack's deny base rate, per-predictor score distributions, `--live-frontier` readiness), spend, open agent flags, agent tooling feedback, data health, and open `run:*` trigger issues (stalled fan-outs) into the ops dashboard Markdown (and optional JSON); `--digest-out` renders the weekly interrogative digest. | `--runs`, `--json`, `--generated-at`, `--corpus-validation`, `--live-frontier`, `--previous`, `--digest-out`, `--data-health-out`, `--trigger-issues` |
| `record-usage` | Record one run's measured token usage and estimated cost next to its prediction/evaluation output. | `--court`, `--docket`, `--event`, `--run-id`, `--engine`, `--role`, `--actor`, `--model`, `--*-tokens`, `--claude-execution-file`, `--codex-sessions-dir`, `--gemini-telemetry-file`, `--pipeline-sha` |
| `usage-summary` | Sum the recorded `usage.json` ledger into an actual \$/run, as JSON on stdout. | — |

## Agent support — matrices, registries, schemas

Helpers the workflows and agents use to fan out and stay in contract.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `predict-matrix` | Emit the predictor × case × event GitHub Actions matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `evaluate-matrix` | Emit the evaluator × case × event matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `authorize-trigger` | Authorize a `run:*` label trigger (Bot handoff or write collaborator), or refuse and exit non-zero. The fan-out workflows call it before any privileged step. | `--sender-type`, `--actor`, `--repo` |
| `mcp-config` | Emit one engine's MCP client config (Claude `--mcp-config` JSON, Codex `config.toml` tables, Gemini `settings.json`) from the versioned tool manifest (`mcp_servers:` in the actor registry). Run it in a step whose env holds the tokens the manifest names — they are injected into the emitted, gitignored file. | `--engine`, `--role`, `--actor`, `--base-settings` |
| `record-retrieval` | Record the cell's tool-call transcript to `retrieval_log.json` — harvested from the engine's own log (the same sources `record-usage` reads), never the agent's word — with the pinned tool manifest snapshotted alongside. An empty transcript still records: "retrieved nothing" is evidence for the evaluators' leakage grading. | `--court`, `--docket`, `--event`, `--run-id`, `--engine`, `--role`, `--actor`, `--mode`, `--claude-execution-file`, `--codex-sessions-dir`, `--gemini-telemetry-file` |
| `finalize-produced` | Print `true`/`false` for whether the agent wrote its own judgment artifact (prediction/evaluation), so a cell with only the pre-materialized event scaffold is reported as producing nothing. | `--role`, `--court`, `--docket`, `--event`, `--actor`, `--run-id` |
| `assert-paths` | Enforce the append-only `data/` path jail on a change set (`git diff --name-status`): exit non-zero on any path outside `data/` or any non-addition. The collect jobs and the required CI `paths` check both call it. | `--name-status-file`, `--run-id` |
| `collect-plan` | Emit the per-run aggregate PR decision for predict/evaluate — one ready PR (auto-merged, closing the trigger issue) plus a draft for salvageable partials — as compact JSON. | `--role`, `--run-id`, `--status-dir`, `--issue` |
| `post-agent-feedback` | Latch a predict/evaluate run's agent-flag roll-up (`collect-plan`'s `feedback_comment`) onto the single long-lived `agent-feedback` issue: find-or-create, post once (marker-deduped). The collect job calls it with the ambient `GITHUB_TOKEN`. | `--body-file`, `--repo` |
| `stall-comment` | Print the trigger-issue comment for a run that **produced no output** (every cell died before or while its agent ran). The collect jobs post it with the ambient `GITHUB_TOKEN` so a wholesale failure is loud on the issue instead of silently orphaning it; `collect-plan`'s `stalled` field (no cell produced *and* no agent finished cleanly) decides when. | `--role`, `--run-url` |
| `metrics-refresh-plan` | Emit the review-PR plan for a metrics refresh (`run-analytics`, metrics-refresh job): given `git diff --name-only -- metrics/` output, print `{"changed":[…],"pr":<branch/title/commit/body\|null>}` with per-artifact headlines read from the regenerated files. `pr` is null when nothing changed, so a no-op refresh opens no PR. | `--changed-file`, `--run-id` |
| `predictors` | List configured predictors (id, engine, model, enabled). | — |
| `evaluators` | List configured evaluators (id, engine, model, enabled). | — |
| `export-schemas` | Write JSON Schema for every pydantic model into `schemas/` (for agents and Codex `--output-schema`). CI fails if the committed schemas drift. | `OUT` (default `schemas`) |

## Maintenance — corpus-informed cleanup

Deterministic sweeps that prune already-merged derived artifacts the append-only
writers can never remove. They need the corpus, so a maintainer runs them
locally over a pulled corpus (`dvc pull`) and lands the result as a **reviewed**
(not auto-merged, manually merged) PR on a `cleanup/*` branch.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `cleanup-out-of-scope-predictions` | Prune committed predictions for cases now out of predict scope, gated on the real corpus row via the same shared exclusion reasoning `predict-matrix` drops on (`corpus.out_of_scope_reason_full`). The event definition and any `outcome.json` stay; only the predictions go. Prints `{"prunable":[…],"removed":<bool>}`; dry-run by default. | `--apply` |
| `reconcile-scope` | The **corpus**-side counterpart: over the SCOTUS dockets, latch `predict_excluded` on those the shared exclusion reasoning now matches (the row rules plus the snapshot-aware bare opinion-import rule) and clear it on those back in scope, so `open-events` drops them at the source. Run where the corpus is pulled (the run-pull historical job), `dvc push` after; prints a `ScopeReconcileResult`. Dry-run by default. | `--apply` |
| `assert-cleanup-paths` | Enforce the **cleanup jail** on a change set (`git diff --name-status`): exit non-zero unless every change is a *delete* under a `data/cases/**/events/*/predictions/` subtree. The maintainer's sweep and the required CI check (`cleanup-paths`, on `cleanup/*` branches) both call it — the destructive counterpart to `assert-paths`. | `--name-status-file` |

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
(`make-fixture-corpus`) for a fully offline run, a real `dvc pull`-provisioned
one, or (via the corpus-backend setting) the blob in place on the DVC remote.
With no `--event` it runs every event the case defines; a resolved event also
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
  over the same cell contract the workflows use (the inline-identifier kickoff
  prompt plus the env vars), so the cells are byte-identical in shape to a CI
  run. The `claude` CLI ships in the devcontainer (`codex` you install
  yourself).

**Auth for the real engines.** Credentials are inherited from the environment,
never assembled by the command. For Claude, set either:

- `ANTHROPIC_API_KEY` — pay-per-token, exactly as CI meters automated inference; or
- `CLAUDE_CODE_OAUTH_TOKEN` — the **subscription** OAuth token from
  `claude setup-token`, so local iteration draws on your Claude subscription
  instead of billing per token. This mirrors the `claude_code_oauth_token` fallback
  noted in `run-predict.yml`.

For Codex, set `OPENAI_API_KEY`.
