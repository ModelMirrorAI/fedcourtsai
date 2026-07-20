# CLI reference (`fedcourts`)

`fedcourts` is a thin wrapper over the library, used by humans, scripts, and the
pipeline workflows. Run `uv run fedcourts --help` for the live listing, or
`uv run fedcourts <command> --help` for a command's flags; this page is the
grouped overview. `--version` prints the installed package version.

Commands fall into the groups headed below: **ingestion** (write the corpus),
**corpus inspection** (read it), **validation** (the gate), **corpus
transport** (move the blob), **diagnostics**
(read-only probes), **metrics & reporting**, **agent support** (fan-out
matrices and registries), **maintenance** (corpus-informed cleanup), and
**local iteration**. For the design behind the
corpus/ledger split see [data-pipeline.md](data-pipeline.md); for how the
workflows wire these together see [pipeline.md](pipeline.md).

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
| `historical-terms` | Load one capped chunk of the historical per-Term set through the live channel: walk the configured October Terms' docket serials sequentially (persisted per-(Term, stream) cursors, so runs resume) and ingest every decided petition except denials, which are systematically sampled per `historical:` in `config/tracking.yaml` — the committed sampling frame. Ingested petitions land already resolved (label, snapshot, events, OT2021+ documents) and feed the statpack's per-Term base rates and replay/evaluation only; **writes no handoff queues**. The `run-seed` workflow loops it, passing the budget still remaining as `--max-run-seconds` so the final chunk stops itself before the job's hard timeout. | `--report`, `--totals`, `--max-probes`, `--max-run-seconds`, `--summary-out` |
| `discover` | Onboard newly-filed dockets in the tracked courts, advancing each court's watermark (dormant in production: `pull.discover_new_filings` is off — the live channel onboards SCOTUS filings). | `--since`, `--limit` |
| `pull-all` | Refresh the stalest tracked cases within the API budget; write the predict/evaluate handoff queues plus the unrecorded-outcome queue (decided but not deterministically recordable, surfaced on the run log). | `--limit`, `--out`, `--evaluate-out`, `--unrecorded-out` |
| `live-poll` | One SCOTUS live-channel cycle: probe the Term's docket-number frontier for new petitions (persisted per-Term cursor), re-poll the pending watchlist (distributed petitions first, nearest conference first), detect resolution from the proceedings text, and write the same three queues as `pull-all` — with predict queued on **distribution transitions** (fresh distribution or relist) of gate-admitted petitions, the cert-calendar predict trigger. The cycle ends with the salience gate's selection pass and its bounded sweep of selected petitions the transition trigger missed (see `docs/salience.md`). | `--term`, `--limit`, `--out`, `--evaluate-out`, `--unrecorded-out` |
| `make-fixture-corpus` | Build a tiny deterministic synthetic corpus (cases/events/snapshots across several courts) so the read commands work offline, no remote. | `--out` |

`--limit` / `--max-probes` / `--max-run-seconds` may only *lower* the per-run cap
from `config/`, never raise it, so a run provably stays within budget.

## Corpus inspection — read the corpus

Read-only views. They read the pulled file by default; where
`--corpus-backend` is listed, `ranged` queries the immutable blob in place on
the corpus remote instead (per-query egress in KBs, read stats echoed to stderr;
see *The ranged read backend* in [data-pipeline.md](data-pipeline.md)).
`query` and `open-events` additionally accept `service` — forward the request
to a `corpus-serve` sidecar (needs `FEDCOURTS_CORPUS_SERVICE_URL`) so the
calling shell holds no cloud credentials; same rows, and `query` prints the
same read-stats line
(see *The corpus query sidecar* in [data-pipeline.md](data-pipeline.md)). The
provisioning commands (`provision-snapshot`, `materialize-event`) additionally
accept `casestore` — read the case's snapshot/documents/event from the per-case
content store rather than the corpus blob (needs `FEDCOURTS_CASESTORE_URL`).
Under the corpus-split mode (`FEDCOURTS_CORPUS_SPLIT=1` — set in production, off
by default for dev environments) those two commands default to `casestore`
without the explicit flag, so the whole fleet reads one store from one setting.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `corpus-info` | Show the packed corpus location, row count, and snapshot count. | `--corpus-backend` |
| `build-index` | Build the small, payload-stripped **index** beside the corpus (`index.db`): copy the blob, empty the `snapshots`/`documents` tables and NULL `cases.opinion_text` (the bulk that lives in the per-case content store), then `VACUUM`. Keeps every other column (incl. `summary`), events, cursors, and the schema, so it is a drop-in for `statpack`/`backtest`/`query` — proven byte-identical by the parity gate. Under the corpus-split mode the production writer emits this payload-free shape directly; `build-index` converts a legacy full blob to it (and anchors the parity gates). | `--out` |
| `query` | Retrieve relevant priors for a predictor, most relevant first, one JSON row per line. Each row carries the case caption and a derived decade `era` (Term year, else filing/decision date) so relevance is judgeable; `--era` restricts retrieval to one period. `--decided-before` is the back-test replay clock — an exclusive year cutoff keeping only priors that provably precede it (rows with no derivable year are excluded); live forward prediction omits it, and a replay cell reads it from `DECIDED_BEFORE`. | `--court`, `--topic`, `--judge`, `--citation`, `--disposition`, `--era`, `--decided-before`, `--include-open`, `--limit`, `--full`, `--corpus-backend` |
| `stats` | Aggregate disposition **base-rates** over the corpus — the aggregate counterpart of `query`. Rolls the matched set into overall base-rates and, with `--group-by`, a per-group breakdown (court / topic / judge / SCOTUS `term_year` / disposition / `originating_court`, the circuit-scorecard cut / `era`, the decade bucket usable on rows `--term` cannot parse / the cert-signal cuts: `relist_bucket` and `cvsg` read the live-parsed columns and bucket unparsed rows as `(unknown)`, while `fee_class` reads the docket serial's numbering stream — paid vs IFP — and sends off-form rows to `(none)`). Shares the `query` filter grammar plus a `--date-from`/`--date-to` filed-date window, a `--term` SCOTUS October-Term filter (SCOTUS cases only — other courts' docket numbers never match), an `--era` decade filter, and `--cert-stage`, which keeps only modern Term-prefixed discretionary-cert dockets — the calibration anchor for cert predictions. Emits an `AnalyticsReport` JSON on stdout and a Markdown summary on stderr; `--summary-out` also appends the summary to a file. Skips gracefully (exit 0) when the corpus is absent. | `--court`, `--topic`, `--judge`, `--citation`, `--disposition`, `--date-from`, `--date-to`, `--term`, `--era`, `--cert-stage`, `--resolved-only`, `--group-by`, `--summary-out` |
| `open-events` | Print a case's unresolved (predictable) event ids, one per line. | `--court`, `--docket`, `--corpus-backend` |
| `corpus-serve` | Serve `query`/`open-events` over localhost HTTP — the sidecar behind the `service` backend. Holds the one corpus connection (and, on `ranged`, the cloud credentials from its own environment) so callers query credential-free; `/healthz` proves the corpus actually opens. Runs until interrupted. Local recipe: `corpus-serve --corpus-backend local`, then `FEDCOURTS_CORPUS_BACKEND=service FEDCOURTS_CORPUS_SERVICE_URL=http://127.0.0.1:8377 fedcourts query …`. | `--corpus-backend`, `--host`, `--port` |
| `conference-set` | The pending-before-conference set: every pending modern-cert petition with a parsed "DISTRIBUTED for Conference of …" membership, grouped by conference date — the live cert watchlist the September long-conference report reads off. `--out` also writes the per-petition JSON. | `--out` |
| `live-frontier` | Snapshot the live cert watchlist's readiness for the ops dashboard: watchlist size, the distribution calendar with the next conference relative to `--today`, and how many watchlist petitions carry provisioned filed-document text. Produced where the corpus is pulled and published to the `ops-metrics` branch (the corpus-writer path) so the corpus-free `run-ops` presenter can render it. Emits a `LiveFrontier`; skips gracefully when the corpus is absent. | `--out`, `--today` |
| `provision-snapshot` | Materialize a case's latest corpus snapshot to disk for an agent run — plus any stored filed-document text (petition, questions presented, brief in opposition — fetched pipeline-side by the live poller) under `record/documents/` with a `documents.json` manifest, and the cell's mode context (`record/context.json`). `--refuse-terminal` (the run-predict forward path) refuses to provision a forward cell whose snapshot already shows the outcome — the latest entry reads terminal, or any entry carries a machine-readable disposition order — exit 3, nothing written: a forward prediction on a decided case would be a mislabeled back-test. | `--court`, `--docket`, `--out`, `--mode`, `--refuse-terminal`, `--corpus-backend` |
| `corpus-integration-check` | Run the fixed read set the `integration-test` workflow's ranged-reads scenario dispatches — a point lookup (open events), a priors retrieval, a snapshot provisioning — each on its own connection so a ranged run reports per-read GET/byte counters. Emits the machine report JSON on stdout and a Markdown summary on stderr; `--summary-out` also appends the summary. Exits non-zero on any empty read or a blown wall-clock budget. | `--court`, `--docket`, `--limit`, `--budget-seconds`, `--snapshot-out`, `--summary-out`, `--corpus-backend` |
| `mcp-integration-check` | Probe the tokenless CourtListener MCP sidecar the way the `integration-test` workflow's mcp-sidecar scenario does: a minimal MCP client completes the streamable-HTTP handshake and asserts `tools/list` advertises at least one tool — the exact surface the generated cell configs point at, without spending a CourtListener call (so the sidecar may run token-free). Same Markdown table and step/budget JSON shape as `corpus-integration-check`, keyed on the probed URL; exits 2 when the endpoint cannot be probed at all (transport failure or a JSON-RPC-level refusal), 1 when the handshake yields no server name, the tool list is empty, or the budget blows. | `--url`, `--budget-seconds`, `--summary-out` |
| `materialize-event` | Project a predictable event's `event.yaml` from the corpus into the git ledger. | `--court`, `--docket`, `--event`, `--out`, `--corpus-backend` |
| `paths` | Print the resolved corpus/case/event paths for a case. | `--court`, `--docket`, `--event` |

## Validation — the gate

The offline checks the PR gate can run without the corpus remote.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `validate` | Validate the git ledger under a path: schema conformance plus git-only references. This is what CI runs on every PR. | `PATH` (default `data`) |
| `validate-corpus` | Open the corpus and assert the cross-store integrity + referential invariants, emitting a `CorpusValidation` verdict. Skips gracefully when the corpus is absent. | `--out`, `--baseline-count`, `--today` |
| `corpus-scope-audit` | Census the corpus's still-open SCOTUS events that the predict scope excludes, per exclusion reason (the shared rules: era, staleness, published-opinion, non-cert docket form, disbarment, consolidated-member agreement, date consistency, and the snapshot-aware bare opinion-import profile), with a recoverable-vs-bare split, plus a breakdown of the *unclassified* open events (why each stays in scope) and a docket-number **shape histogram** for the not-parseable bucket — the scope-refinement signal (the concrete formats a Term-parser broadening would target). A shape under ~100 open events is an accepted fragment: it stays visible in the histogram by design, and no exclusion predicate is chased for it. The read-only counterpart of `reconcile-scope`, for ad-hoc scope triage. Emits a `CorpusScopeAudit`; skips gracefully when the corpus is absent. | `--out` |
| `scope-manifest` | Publish the prediction-scope decision (`predict_eligible` / `predict_excluded` / exclusion reason / sample weight / salience score, version, and selection latch) for every docket **already public** under `data/cases`, to `data/scope/scope.json` — the transparency counterpart of `reconcile-scope` (which decides scope in the corpus; this publishes it). Enumerated from the committed `data/cases` tree **alone**, never a corpus scan, so it discloses only the already-public set and by construction cannot enumerate the wider ingested corpus. Deterministic and offline; writes the empty `skipped` manifest when the corpus is absent. Emits a `ScopeManifest`; regenerate and open a reviewed PR when the public set or its latches change. | `--out` |
| `corpus-status` | Check the committed corpus + metrics bookkeeping is internally consistent — the blob out of git and gitignored, the `corpus.db.ref` pointer well-formed, the metrics roll-ups committed — and, when the corpus blob is present locally, that its physical layout matches the ranged-read contract (64 KB pages, non-WAL at rest). | `PATH` (default `.`) |

## Corpus transport — move the blob

The pull/push pair the data workflows (and a developer with credentials) use to
move the corpus index blob between disk and the S3 remote; both read the remote
URL from `CORPUS_REMOTE_URL` (legacy `DVC_REMOTE_URL` accepted).

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `corpus-pull` | Download the blob the committed `corpus/corpus.db.ref` pointer names, verifying its checksum + size before the file lands. | `--missing-pointer fail\|warn` |
| `corpus-push` | Digest the local blob, upload it to its content-addressed key (put-if-absent; the remote stays add-only), and rewrite the pointer — blob before pointer, so a committed pointer always resolves. | |

## Diagnostics — read-only probes

Measurements a maintainer runs to answer a build question, writing nothing.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `probe-live-terms` | The live-sources reachability probe: for each October Term from `--max-term` back to `--min-term`, fetch a small sample of `supremecourt.gov` docket-JSON numbers and report availability, document-link coverage, schema stability, and whether the proceedings text carries machine-matchable disposition orders. Strictly read-only and budget-free — the supremecourt.gov channel, not the CourtListener client (no token, no governor; browser UA + ~1 req/s politeness built in). Emits per-Term/per-record JSON on stdout and the Markdown findings table on stderr. Run it to re-establish the Term floor and the disposition-resolver recall claim after a pattern change; the standing conclusions live in [live-sources.md](live-sources.md). | `--max-term`, `--min-term`, `--numbers`, `--throttle`, `--report-out`, `--summary-out` |

## Metrics & reporting

Deterministic roll-ups (committed) and point-in-time snapshots (surfaced, not
committed), plus the spend ledger.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `leaderboard` | Rank predictors from the evaluations ledger into `metrics/leaderboard.json`. | `--out` |
| `backtest` | Replay the reference predictors over resolved corpus events into `metrics/backtest.json`. The prior-vote baseline is **time-masked**: it votes only over priors that provably precede each trial's own year, and a trial with no derivable year gets the conservative floor rather than a hindsight vote. | `--out`, `--court`, `--limit` |
| `cert-backtest` | Back-test cert predictors over the most recently decided modern discretionary-cert petitions (outcome hidden), scoring accuracy, Brier, **lift over the always-deny floor**, and a P(granted) calibration view into `metrics/cert-backtest.json` — labeled retrospective. Offline reference baselines always run; `--engine auto` additionally replays every enabled predictor over **redacted snapshots** in a scratch tree, each through its **own configured engine** (an apples-to-apples read; a predictor whose engine has no registered runner is skipped and named, never mislabeled through another engine), while a concrete backend (`stub`, `replay`, `claude-code`, `codex`, `gemini`) routes every predictor through that one backend for offline runs and single-engine sweeps. All three engines are routable, so under `auto` all three run unless opted out; `--skip-engines` opts a named engine (or engines) out (erroring on an unknown name), and an engine whose CLI binary is missing at run time is dropped loudly rather than crashing the run. Spends tokens on a real engine; never writes `data/`. `--scope` narrows the population from `all` modern-cert petitions to `paid` (drops IFP) or `selected` (the salience gate's carve-out core — CVSG or at/above the salience floor — the N-independent core of the live selected slice, which also fills to N by rank); `--spread` samples across conference cohorts instead of the most recent N (which collapses onto the last, grant-heavy order lists) — together the closest replay-safe like-for-live read. Petitions with no held snapshot or petition event are dropped up front and named, so all backtesters in one report score the same set; each cell's `DECIDED_BEFORE` is the trial's year, so the agent's own corpus retrieval is time-masked too. | `--out`, `--limit`, `--engine`, `--skip-engines`, `--scope`, `--spread`, `--work-dir` |
| `statpack` | Roll the corpus into a base-rate **statpack** at `metrics/statpack.{json,md}`, two populations side by side: the labeled full-corpus overview (by court, by era) and the **live/historical-slice cert statistics** the predict/evaluate prompts anchor on — denial-reweighted disposition base rates (the modern-cert calibration anchor), cuts by originating circuit / relist count / CVSG status, a by-originating-court reader table naming state courts, a coverage block, and a per-SCOTUS-Term detail array (cursor-derived filings census per fee class, walk-complete flags, weighted estimates, grants and pace-to-grant; recent first — the Markdown shows the latest 10 and states the replay per-Term self-selection rule). Deterministic and offline; writes the empty pack when the corpus is absent. | `--out`, `--markdown-out` |
| `ops-report` | Roll pipeline health, **substance** (scored cells by stratum with deltas vs `--previous`, replay calibration vs the statpack's deny base rate, per-predictor score distributions, `--live-frontier` readiness), spend & cost, **agent signals** (flags, leakage, and tooling digests, windowed to recent runs), data health, and open `run:*` trigger issues (stalled fan-outs) into the ops dashboard Markdown (and optional JSON); `--digest-out` renders the weekly interrogative digest. | `--runs`, `--json`, `--generated-at`, `--corpus-validation`, `--live-frontier`, `--previous`, `--digest-out`, `--data-health-out`, `--trigger-issues` |
| `record-usage` | Record one run's measured token usage and estimated cost next to its prediction/evaluation output. | `--court`, `--docket`, `--event`, `--run-id`, `--engine`, `--role`, `--actor`, `--model`, `--*-tokens`, `--claude-execution-file`, `--codex-sessions-dir`, `--gemini-telemetry-file`, `--pipeline-sha` |
| `usage-summary` | Sum the recorded `usage.json` ledger into an actual \$/run, as JSON on stdout. | — |

## Agent support — matrices, registries, schemas

Helpers the workflows and agents use to fan out and stay in contract.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `predict-matrix` | Emit the predictor × case × event GitHub Actions matrix as compact JSON. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event` |
| `evaluate-matrix` | Emit the evaluator x case x event matrix for `run-evaluate`. Two plan-time gates drop cells before any model spend: an event with **no committed prediction** has nothing to score, and a judge that has **already graded** the event is not re-minted (which is what keeps a re-queue from double-counting in the leaderboard). `--force` disables the second for a deliberate re-grade after a prompt or rubric change; the workflow never passes it, so it is a local/maintainer operation. | `--run-id`, `--body-file`, `--court`, `--docket`, `--event`, `--force` |
| `authorize-trigger` | Authorize a `run:*` label trigger (Bot handoff or write collaborator), or refuse and exit non-zero. The fan-out workflows call it before any privileged step. | `--sender-type`, `--actor`, `--repo` |
| `mcp-config` | Emit one engine's MCP client config (Claude `--mcp-config` JSON, Codex `config.toml` tables, Gemini `settings.json`) from the versioned tool manifest (`mcp_servers:` in the actor registry). `--http-url <id>=<url>` (repeatable) emits that server as a remote streamable-HTTP entry — a localhost URL, no launch command, no token (the `mcp-serve` sidecar holds it); the cell workflows use this for every server. Without it, stdio launches inject tokens from THIS process's env into the emitted, gitignored file — the local-run mode; run it in a step whose env holds them. | `--engine`, `--role`, `--actor`, `--base-settings`, `--http-url` |
| `mcp-serve` | Run one manifest server as the tokenless HTTP sidecar (foreground; the cell workflows background it). The launch step's env holds the server's API token, so no client config file ever does; serves the same pinned package the stdio transport would have spawned, on localhost. | `--role`, `--actor`, `--server`, `--port` |
| `record-retrieval` | Record the cell's tool-call transcript to `retrieval_log.json` — harvested from the engine's own log (the same sources `record-usage` reads), never the agent's word — with the pinned tool manifest snapshotted alongside. An empty transcript still records: "retrieved nothing" is evidence for the evaluators' leakage grading. | `--court`, `--docket`, `--event`, `--run-id`, `--engine`, `--role`, `--actor`, `--mode`, `--claude-execution-file`, `--codex-sessions-dir`, `--gemini-telemetry-file` |
| `finalize-produced` | Print `true`/`false` for whether the agent wrote its own judgment artifact (prediction/evaluation), so a cell with only the pre-materialized event scaffold is reported as producing nothing. | `--role`, `--court`, `--docket`, `--event`, `--actor`, `--run-id` |
| `assert-paths` | Enforce the append-only `data/` path jail on a change set (`git diff --name-status`): exit non-zero on any path outside `data/` or any non-addition. The collect jobs and the required CI `paths` check both call it. | `--name-status-file`, `--run-id` |
| `scan-diff-for-secrets` | Scan every changed `data/` file in a change set (plus any `--extra-file`, e.g. a PR body about to be posted) for secret material: literal containment of each `--known-secret-env` credential in cheap encodings, credential-shape patterns, and an entropy heuristic. Findings are reported as file/rule/line — never the matched text. Exit 1 on a hit, 2 on a misconfigured scan (unset env var, missing extra file); the collect jobs withhold the run branch on either. | `--name-status-file`, `--known-secret-env`, `--extra-file`, `--issue-comment-file`, `--run-url` |
| `collect-plan` | Emit the per-run aggregate PR decision for predict/evaluate — one ready PR (auto-merged, closing the trigger issue only when nothing is left to salvage and no whole engine is missing) plus a draft for salvageable partials — as compact JSON. | `--role`, `--run-id`, `--status-dir`, `--issue` |
| `post-issue-comment` | Comment on an issue exactly once, keyed by `--marker`: a comment already carrying the marker is not posted again. The collect job's stall and secret-scan reports use it, because that step re-runs whenever collect does — and re-running collect is the documented recovery for a transfer failure — so an unconditional comment would stack one copy per attempt and bury the warning. The stall marker keys on the run; the secret-scan marker also keys on the report's content, so a later attempt that hits a *different* file is never deduped into silence. | `--issue`, `--repo`, `--marker`, `--body-file` |
| `post-agent-feedback` | Latch a predict/evaluate run's agent-flag roll-up (`collect-plan`'s `feedback_comment`) onto the single long-lived `agent-feedback` issue: find-or-create, post once (marker-deduped). The collect job calls it with the ambient `GITHUB_TOKEN`. | `--body-file`, `--repo` |
| `stall-comment` | Print the trigger-issue comment for a run that **produced no output** (every cell died before or while its agent ran). The collect jobs post it with the ambient `GITHUB_TOKEN` so a wholesale failure is loud on the issue instead of silently orphaning it; `collect-plan`'s `stalled` field (no cell produced *and* no agent finished cleanly) decides when. | `--role`, `--run-url` |
| `metrics-refresh-plan` | Emit the review-PR plan for a metrics refresh (`run-analytics`, metrics-refresh job): given `git diff --name-only -- metrics/` output, print `{"changed":[…],"pr":<branch/title/commit/body\|null>}` with per-artifact headlines read from the regenerated files. `pr` is null when nothing changed, so a no-op refresh opens no PR. | `--changed-file`, `--run-id` |
| `predictors` | List configured predictors (id, engine, model, enabled). | — |
| `evaluators` | List configured evaluators (id, engine, model, enabled). | — |
| `export-schemas` | Write JSON Schema for every pydantic model into `schemas/` (for agents and Codex `--output-schema`). CI fails if the committed schemas drift. | `OUT` (default `schemas`) |

## Maintenance — corpus-informed cleanup

Deterministic sweeps that prune already-merged derived artifacts the append-only
writers can never remove. They need the corpus, so a maintainer runs them
locally over a pulled corpus (`fedcourts corpus-pull`) and lands the result as a **reviewed**
(not auto-merged, manually merged) PR on a `cleanup/*` branch.

| Command | Purpose | Key flags |
|---------|---------|-----------|
| `cleanup-out-of-scope-predictions` | Prune committed predictions for cases now out of predict scope, gated on the real corpus row via the same shared exclusion reasoning `predict-matrix` drops on (`corpus.out_of_scope_reason_full`). The event definition and any `outcome.json` stay; only the predictions go. Prints `{"prunable":[…],"removed":<bool>}`; dry-run by default. | `--apply` |
| `reconcile-scope` | The **corpus**-side counterpart: over the SCOTUS dockets, latch `predict_excluded` on those the shared exclusion reasoning now matches (the row rules plus the snapshot-aware bare opinion-import rule) and clear it on those back in scope, so `open-events` drops them at the source. Run where the corpus is pulled (the run-seed workflow), `corpus-push` after; prints a `ScopeReconcileResult`. Dry-run by default. | `--apply` |
| `migrate-gvr-labels` | One-time, deterministic migration for the `gvr` disposition (see `docs/salience.md`): relabel each committed `granted` outcome whose `disposition_basis` is `mootness` — an identifiable Munsingwear vacatur — to `actual_disposition = gvr`. `actual_granted` stays 1 (a GVR is a grant), the frozen `evaluation.json` records are untouched, and the cell keeps its `mootness` basis (procedural stratum), so no metric moves. Prints the count and the relabeled case ids. Dry-run by default. | `--apply` |
| `reconcile-salience-selection` | The salience gate's write pass (see `docs/salience.md`): score every in-scope SCOTUS cert petition with the frozen `sal-v1` function and latch `salience_selected` on each conference cohort's top-N by score plus the always-include carve-outs (CVSG, above-floor). The latch is one-way (sticky), so a re-run never de-selects a petition that later drifts below the cap. Production runs the same pass inside every `live-poll` cycle (see `docs/salience.md`); the command remains for manual runs and dry-run inspection, where the corpus is pulled and `corpus-push` follows an `--apply`. Prints a `SalienceSelectionResult`. Dry-run by default. | `--apply` |
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
| `local-cascade` | Provision a case's snapshot, predict it with every enabled predictor (`--predictor` narrows to one — the one-cell shape a token-spending smoke run wants), evaluate the resulting predictions with every enabled evaluator, and validate the produced ledger. `--require-predictions` fails the run when no predictor cell wrote a prediction — a real agent that finishes blocked exits 0 with a validly-empty ledger, which a smoke must treat as failure. | `--court`, `--docket`, `--event`, `--engine`, `--run-id`, `--predictor`, `--corpus-backend`, `--require-predictions` |

It reads the case from the packed corpus — point it at the synthetic fixture
(`make-fixture-corpus`) for a fully offline run, a real `corpus-pull`-provisioned
one, or (via the corpus-backend setting) the blob in place on the corpus remote.
`--corpus-backend` overrides that setting for the cascade's *own* provisioning
reads only (`local` or `ranged` — the query sidecar's `service` surface does not
serve them); the spawned agent still inherits the ambient corpus settings, so an
environment configured for the sidecar drives the agent's retrieval through it
while provisioning reads the blob directly — the split the `integration-test`
workflow's engine-smoke scenario runs on.
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
- `claude-code` / `codex` / `gemini` — drive the **real** headless agents
  (`claude`, `codex`, `gemini`) over the same cell contract the workflows use
  (the inline-identifier kickoff prompt plus the env vars), so the cells are
  byte-identical in shape to a CI run. The `claude` CLI ships in the devcontainer
  (`codex` you install yourself; `gemini` is `npm install`-ed, as the workflow
  does).

**Auth for the real engines.** Credentials are inherited from the environment,
never assembled by the command. For Claude, set either:

- `ANTHROPIC_API_KEY` — pay-per-token, exactly as CI meters automated inference; or
- `CLAUDE_CODE_OAUTH_TOKEN` — the **subscription** OAuth token from
  `claude setup-token`, so local iteration draws on your Claude subscription
  instead of billing per token. This mirrors the `claude_code_oauth_token` fallback
  noted in `run-predict.yml`.

For Codex, set `OPENAI_API_KEY`. The pinned codex CLI never reads that
variable itself, so the runner feeds it to `codex login --with-api-key`
(over stdin) before each cell — into a run-scoped temp `CODEX_HOME`, so your
`~/.codex` subscription login is never touched; unset the variable to use an
existing `codex login` instead, and an explicitly exported `CODEX_HOME` wins
over the run-scoped default. For Gemini, set `GEMINI_API_KEY`.
