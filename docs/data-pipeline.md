# Data pipeline: ingestion & freshness

The design contract for the ingestion channels — the **pull** (CourtListener
enrichment), **live** (forward SCOTUS poll), and **historical** (Term walker)
jobs — and for the stores they write. For the label/workflow mechanics see
[pipeline.md](pipeline.md); for the store split at a glance see the *Data
model* section of the [README](../README.md).

## Scope

Two different scopes apply, and keeping them apart is what bounds the bill:

- **Ingestion scope — the full set.** The ingestion channels assemble the
  **Supreme Court and all 13 federal courts of appeals** (`scotus`, `ca1`–`ca11`,
  `cadc`, `cafc`); district courts are intentionally **out of scope** for now.
  Ingestion is deterministic script work — cheap relative to the agentic stages
  — and the whole corpus is assembled precisely so predict/evaluate can **query
  the full history** for retrieval and back-testing, even for cases they never
  predict.
- **Prediction scope — SCOTUS dockets only.** The agentic predict/evaluate
  stages cost one to two orders of magnitude more than ingestion (see
  [budget.md](budget.md)), so they run on a deliberate subset:
  `predict.scope=scotus_docket` — only cases whose `court == "scotus"` (the
  immutable row property every scope seam reads directly). On top of the court
  predicate ride the shared exclusion rules (`corpus.OUT_OF_SCOPE_RULES`,
  applied via `out_of_scope_reason_full`): **pre-1925 mandatory-jurisdiction
  matters** (a bare, non-Term-prefixed docket number — a merits, not a
  discretionary-cert, disposition meaning), **stale still-open petitions** from
  long-past October Terms, cases whose only outcome signal is a **published
  opinion with no machine-readable disposition**, **stay/emergency
  applications** (`22A123`) and **original-jurisdiction** matters (`22O141`),
  **pro se / in-forma-pauperis petitions** (the IFP docket serial ≥ 5001 — a
  documented scope decision so the salience gate spends the fundable slice on the
  paid cert docket; see [salience.md](salience.md)), and a guard for
  **internally inconsistent dates**. Each gates prediction only, never ingestion.
  The two-directional scope reconcile releases a case latched for **staleness** or
  a **bare published-opinion import** once it gains a real disposition; the
  **form-keyed** exclusions (IFP serial, applications, original jurisdiction) are
  permanent by construction — the docket form never changes, so they never
  release. Because the corpus keys a case by
  `<court>/<docket>`, a case's SCOTUS docket and its originating
  court-of-appeals docket are **separate rows**: only the SCOTUS row is
  predicted, and the lower-court link columns (`originating_court` /
  `originating_docket_number`) are retrieval context — never a scope trigger.

  Within this prediction scope, [salience.md](salience.md) designs a
  **salience-ordered** gate — hard eligibility filters, then a deterministic
  ranking that spends the tournament on the most salient slice up to a fundable
  capacity — plus the two pre-registered scores (deterministic salience and the
  model-produced big-case score) and the segment base rate that anchors them.

## The binding constraint: the CourtListener API budget

CourtListener's REST API is throttled per token (see [budget.md](budget.md)
for the held tier); the in-process governor (`courtlistener/ratelimit.py`)
throttles to whatever ceilings the runner environment sets
(`FEDCOURTS_COURTLISTENER_RPM` / `_RPH` / `_RPD`). At roughly **3 requests per
docket** the budget is a few hundred dockets a day at most — and the
supremecourt.gov live channel spends none of it.

Because pull runs headless inside a CI job, budget pressure and a degraded
upstream must **degrade a run, never hang it**. Three guards enforce that, all
tuned in `config/tracking.yaml`: the throttle raises rather than sleep out an
hour/day-scale wait, a wall-clock deadline (`pull.max_run_minutes`), and a
circuit breaker (`pull.max_consecutive_transient_failures`) for a down
upstream. However a run stops early, it defers the unreached cases (their
`last_pulled` untouched, so they stay at the front of the next window's
stalest-first rotation), records why, and still writes its updates.

That cap makes one thing non-negotiable: **the REST API cannot load history.**
So loading and forward enrichment use different sources:

| Channel        | Source                               | Spends API budget? |
|----------------|--------------------------------------|--------------------|
| **historical** | supremecourt.gov **docket JSON**     | No (~0)            |
| **live**       | supremecourt.gov **docket JSON**     | No (~0)            |
| **pull**       | CourtListener **REST API**           | Yes — owns it      |

The supremecourt.gov docket JSON serves every SCOTUS petition of the e-filing
era (OT2017+; see [live-sources.md](live-sources.md)). The channel charters:

- **Historical loading is the historical Term walker**
  (`fedcourts historical-terms`, the `run-seed` workflow) — the
  same client, identity, and ingest seams as the forward poller, landing the
  sampled decided set for the statpack's per-Term base rates and the cert
  back-test set.
- **Pull is targeted enrichment.** The live channel owns SCOTUS freshness;
  pull's REST budget keeps the tracked set's CourtListener records current.
  **CourtListener discovery is off** (`pull.discover_new_filings: false`): the
  live channel's frontier probing onboards newly filed SCOTUS petitions —
  fresher and budget-free — and circuit discovery would onboard cases outside
  the prediction scope.
- **Resolution is deterministic-first; ambiguity is triaged, not delegated.**
  The shared cert-disposition resolver (`pipeline/cert_signals.py`) matches
  disposition orders in plain proceedings text, GVR forms included; anything it
  cannot record deterministically becomes an **unrecorded outcome** for
  maintainer triage (see *Pull* below) — no agent runs and no issue is filed.

## The planned end-state: a CourtListener database replica

Free Law Project offers **replication of the CourtListener Postgres database**
— the intended eventual upstream once funding allows: full field coverage,
current within replication lag, no request caps. The pivot swaps the
**channels**, never the **corpus**: the replica arrives as one more source
feeding the same normalized rows through the shared normalizer
(`ingest.from_bulk_row`). Adoption also needs a terms review of the agreement;
the access-gated, no-republication stance in [data-sources.md](data-sources.md)
already matches that shape. Until then, four guardrails keep interim work from
blocking the pivot: ingestion stays channel-agnostic; the API budget governor
stays scoped to the REST client (a constraint to be deleted, not a dependency);
enrichment flows through ingestion into the corpus, never as agent-side API
calls; and bulk-shaped tooling stays thin — durable investment goes into the
normalization seam and the corpus schema, both of which survive the swap. The
replica serves the *historical* roles; the **live frontier** is a separate
track with its own source, independent of both the REST budget and the replica
timeline ([live-sources.md](live-sources.md)).

## Three writer jobs, one shared core

Two workflows carry three writer jobs over one corpus — `run-pull`'s **pull** and
**live**, and `run-seed`'s **historical** walker — differing on every axis that
matters, while the shared `corpus-write` lock keeps at most one running at a time:

| Axis      | historical (Term walker, run-seed)      | pull (enrichment, run-pull)       | live (forward poll, run-pull)   |
|-----------|-----------------------------------------|-----------------------------------|---------------------------------|
| Source    | supremecourt.gov JSON                   | REST API                          | supremecourt.gov JSON           |
| Charter   | decided history, newest Term first      | keep CourtListener records current | pending petitions: discovery, watchlist, outcomes |
| Budget    | ~0 API (politeness caps)                | owns the CourtListener budget     | ~0 API (politeness caps)        |
| Cadence   | **daily** (4 dead-zone windows)         | **daily** (4 windows)             | **daily** (4 windows)           |
| Handoffs  | none — lands already-resolved history   | predict/evaluate issues           | predict/evaluate issues         |

They share an **ingestion core** (`fedcourtsai.pipeline.ingest`: a
normalization layer where a CourtListener API docket, a bulk-shaped row, and a
supremecourt.gov docket JSON all become the same normalized row, then upsert
through `fedcourtsai.corpus`) plus shared dedup/cursor utilities. **Unify the
library and the data, not the job:** every job writes the same stores through
the same APIs; separate jobs only keep the budget boundary crisp.

## Storage: one corpus, one ledger

Raw facts and derived judgments have different shapes and lifetimes, so they
live in different stores, split by **kind**:

1. **Raw facts → the corpus**, which has two halves:
   - **The index** — a small, **payload-free SQLite database**
     (`corpus/corpus.db`) carrying the scannable `cases` columns (including
     `summary` and a `has_opinion` presence bit), the events and cursors, and
     the schema itself — everything queries, scans, scope gating, and base
     rates need. The blob lives in the private S3 remote at a
     **content-addressed, add-only** key (`index/sha256/<digest>`) and only
     the small JSON pointer (`corpus/corpus.db.ref`: key, size, sha256,
     schema version) is
     committed — `fedcourts corpus-push` publishes a new immutable version,
     `corpus-pull` fetches and **checksum-verifies** what the pointer names,
     the same boto3-against-S3 pattern the content store uses. (The `metrics/`
     roll-ups are plain git-tracked files; the offline gate checks they stay
     committed.)
   - **The per-case content store** (`fedcourtsai.casestore`) — a browsable,
     **write-once**, access-gated S3 store holding the bulk payloads: dated
     point-in-time snapshots, extracted filed-document text, and opinion
     bodies, keyed to mirror the git ledger's `data/cases/<court>/<docket>/`
     shape. Write-once discipline keeps "what did a cell see?" reproducible:
     document text leaves are content-addressed, dated snapshots are immutable
     per day, and the small manifests are versioned rather than deleted —
     fitting the read-write role's no-delete posture. Only *changed* cases
     upload, so storage scales with case churn, not run count, and per-case
     objects stay **behind index pointers, never git tree entries**.

   The write seams (`upsert_rows` / `upsert_snapshot` / `upsert_documents` /
   `upsert_events`) mirror each mutated case to the store and keep the bulk
   payloads out of the blob; the payload *reads* — the writer's change
   detection and document dedup, the readers' provisioning and `cert-backtest`
   replay — are served from the store through a **payload read source**. A
   parity gate (`tests/test_corpus_split_writer.py`) proves the payload-free
   blob equals a legacy full blob run through `build-index`.
   `FEDCOURTS_CORPUS_SPLIT` (`Settings.corpus_split`) selects these split
   read/write paths: set on the production `runner` environment, default
   **off** so a dev environment without the store (the fixture loop, offline
   tests) reads and writes a single self-contained blob. The store's location
   comes from `FEDCOURTS_CASESTORE_URL` (wired per writer job in `run-pull`);
   mirroring is best-effort — a store failure logs, never breaking the SQLite
   write.
2. **Derived judgments → the git ledger** under `data/`, where the
   schema/`validate`/PR-review machinery applies (see *The ledger* below).

The rule is **pack, don't proliferate**: millions of per-case files would choke
`git` even under LFS, so raw facts go to the packed index and the access-gated
store — while the reasoning stays readable text in git, because that diff is
the explainability trail a reviewer actually reads.

### The ledger (case-centric)

Everything in git is keyed by `case_id` / `event_id` (always derived via
`fedcourtsai.ids`/`fedcourtsai.paths`; `run_id` is a UTC timestamp), so a
single event's story sits in one subtree — the layout is in the README's *Data
model* section. **Why case-centric:** an evaluator reads one directory to see
all predictors' outputs plus the outcome; a new prediction touches only its own
run directory. The cost is that a cross-predictor leaderboard is a glob
(`fedcourts leaderboard`) — a cheap trade.

**Per-cell sidecar files** land beside each cell's judgment. `usage.json`
records the cell's token usage and estimated USD cost (rates in
`fedcourtsai.pricing`), captured from the engine's own run log — never the
agent's word — plus the cell's pipeline provenance (`pipeline_sha`).
`flags.json` (an `AgentFlags`) is a cell's **durable feedback channel**,
written only when there is a structured note to surface; the `collect` job
rolls every cell's flags into the run PR body, the Actions summary, and one
long-lived **agent-feedback** tracking issue, so the note survives the trigger
issue's closure, and `run-ops` surfaces recent flags. `tooling.json` (an
`AgentToolingFeedback`) is solicited every run — a short self-report on the
cell's tooling, scanned by `run-ops` into a tooling digest; advisory, never
gating. `retrieval_log.json` is the harness-captured tool-call transcript the
evaluators' leakage grading reads.

**Repo-level roll-ups** sit outside the per-case tree, each a deterministic,
offline function of the corpus regenerated and committed for review: the
`metrics/` artifacts (leaderboard, backtest, statpack) and
`data/scope/scope.json`, the published prediction-scope decision
(`predict_eligible` / `predict_excluded` / reason / `sample_weight`) for the
already-public case set. `metrics/` refreshes on the analytics workflow; the
scope manifest (`fedcourts scope-manifest`) is regenerated on demand — when the
public set or its scope latches change — and PR'd. It is enumerated from the
committed `data/cases` tree alone, never a corpus scan, so it discloses only the
already-public set and cannot enumerate the wider ingested corpus (see
[cli.md](cli.md)).

### Credentials and access roles

The corpus remote and the content store are private S3 behind **GitHub OIDC** —
no static keys in workflows; two IAM roles split read-write (the corpus
writers) from read-only (every consumer). No config file carries credentials
or the bucket URL; each job (and each operator) supplies the URL out of band
as the `CORPUS_REMOTE_URL` environment variable, and boto3 takes its
credentials from the environment. The full wiring — roles, the per-workflow
access table, trust scoping, bucket posture — is single-sourced in
[security.md](security.md). The CI gate has no remote, so it runs the offline
half: `fedcourts corpus-status` checks the committed bookkeeping is internally
coherent (blob out of git, pointer well-formed, metrics committed, ranged
layout); the online pull/push stays with the corpus-writer workflows that hold
the credentials.

The workflow variable is `CORPUS_REMOTE_URL` (the rename off the old
`DVC_REMOTE_URL` spelling is done). The tooling still accepts the legacy
`DVC_*` aliases, which now survive only for the Codespaces devcontainer secret
(still spelled `DVC_REMOTE_URL`); they retire when that secret is renamed too.

### Corpus-writer coordination

`corpus/corpus.db` is one mutable SQLite blob behind one committed pointer, and
three writer jobs across two workflows mutate it. A blob has no merge, so the
pointer is last-writer-wins: concurrent or divergent-base writers would silently
drop each other's rows. Two rules prevent that: **one lock** — all three writer
jobs, in `run-pull` (pull, live) and `run-seed` (historical), share the
repo-level `corpus-write` concurrency group (`cancel-in-progress: false`), so
corpus writers never run simultaneously even across workflows — and **reset to
the live tip before mutating**: because
`actions/checkout` pins the run's *creation-time* sha, each writer job first
`git fetch`es and `git reset --hard`s to the current tip of the default branch
before `corpus-pull → mutate → corpus-push → commit the pointer`, so it
always builds on its predecessor's writes (an unrelated tip advance after the
reset rebases cleanly; a pointer conflict aborts the rebase and fails loudly).
The commit-and-push is one shared retry loop —
`.github/actions/commit-corpus-to-main/push_with_retry.sh` — that every writer
reaches: the `pull` and `live` jobs through the `commit-corpus-to-main` composite
action wrapping it (the action adds the stage/commit/no-op guard), and the
historical walk's per-chunk checkpoint and scope-latch step by calling the script
directly. It rebases onto any advance and retries a *transient* push failure (a
GitHub `commit_refs` blip, not a branch advance) with exponential backoff, long
enough to outlast a brief server hiccup; a genuine pointer divergence still fails
loudly and immediately.
The content store needs no such lock: its per-case objects are write-once and
its manifests versioned, so concurrent mirrors cannot drop each other's data.

### The ranged read backend and the blob's physical layout

`fedcourtsai.corpus_ranged` implements **ranged remote reads**: a read-only
SQLite VFS (apsw) that queries the immutable, content-addressed blob in place
on the remote, serving page reads from block-aligned S3 ranged `GET`s (fixed
256 KB blocks through a per-connection LRU; the file size comes from the
committed pointer, so the object is never `HEAD`ed). Immutability is what makes this
sound with **no consistency machinery**: the committed pointer names one exact
byte sequence, so a reader can never observe a torn write. The blob's physical
layout is a contract with that access pattern, and the writers guarantee it:
**64 KB pages** (a B-tree descent costs a handful of round trips) and a
**non-WAL journal mode at rest** (a WAL reader needs the `-wal` sidecar, which
never ships). `corpus.connect` creates every database with this layout, each
writer command (and `corpus-push` itself) rebuilds a drifted file (`VACUUM`)
before the push, and `fedcourts corpus-status` fails on a drifted local file —
enforced, not remembered. The retrieval read paths are index-served (pinned by `EXPLAIN
QUERY PLAN` tests), keeping a ranged point lookup at KB scale.

Read-only consumers go through `corpus.connect_readonly`, which picks the
backend from the corpus-backend setting (or an explicit override): `local`
opens the pulled file, `ranged` resolves the committed pointer against
the out-of-band remote URL; writers never use this seam. Each ranged connection
reports its `GET`s and bytes fetched to stderr — the per-query egress evidence
retrieval logging and the integration check consume — and the transport is one
callable `(key, byte range) -> bytes` (boto3-against-S3; offline tests
substitute an in-memory stand-in). Credit: michalc/sqlite-s3-query and
litements/s3sqlite (both MIT) are the reference implementations; this is
in-repo so it is typed, tested, and reviewed under the same gate.

### The corpus query sidecar (the `service` backend)

The decision behind the fourth backend, recorded here because it settles the
agent retrieval contract. The ranged backend needs cloud credentials **in the
calling shell**, and the callers that matter most are agent cells processing
adversarial docket text: two engines held read-only AWS credentials as an
accepted residual, and the third (Gemini)
could not run ranged queries at all — its CLI's env sanitizer refuses to allowlist
any credential-shaped variable name, which made corpus retrieval an accident
of harness rather than a level surface. The alternatives were to accept that
asymmetry, or to hand the third engine a credentials file (levelling *down* —
three exposed shells instead of two). The decision levels *up*: corpus
retrieval becomes a **query service**, so that no agent shell holds any
credential. The cell workflows launch the sidecar with step-scoped
credentials (see the security runbook, whose cells-hold-credentials residual
this retired); the same pattern also serves the CourtListener MCP tools —
`fedcourts mcp-serve`, the tokenless MCP sidecar whose client configs carry
only a localhost URL.

`fedcourts corpus-serve` (`fedcourtsai.corpus_service`) serves `query` and
`open-events` over localhost HTTP. The process holds the one corpus connection
— and, in a cell job, the cloud credentials from *its own* step environment —
while callers set `FEDCOURTS_CORPUS_BACKEND=service` plus
`FEDCOURTS_CORPUS_SERVICE_URL` (a name the Gemini sanitizer accepts) and keep
running the identical `fedcourts query` commands. It is a transport change,
not a new surface: rows are shaped by the same `corpus.prior_payload` on both
paths (byte-identical output, pinned by tests), and each response carries the
ranged connection's per-request `GET`/byte delta, from which `query` prints
the same `ranged corpus reads:` stderr evidence line (`open-events` stays
silent on both paths, as it always has). A warm sidecar cache honestly
reports `0 GET(s)` — the held connection keeps the ranged block cache warm
across a cell's whole query budget, so egress *drops* relative to
one-connection-per-invocation. The startup transfer is charged to whichever
request triggers the lazy open: in the workflow flow that is the launch
step's health check (visible in the sidecar log), so the agent's evidence
lines carry only its own queries' costs.

Deliberate minimalism, and its trade-offs: the server is single-threaded
stdlib `http.server` (nothing in the read stack is thread-safe; localhost
queuing is fine at a cell's query volume), the wire contract is a `/v1/` path
plus a `schema_version` literal on pydantic models with both ends always built
from the same checkout (so it is an internal protocol, deliberately not in the
exported data schemas), and a request that fails — sidecar down, backend error
— degrades exactly like a failed query today: stderr diagnosis, exit 1, the
cell continues on provisioned inputs. A hung upstream read blocks the
single-threaded server (including its health endpoint) until the transport
times out; if the sidecar is ever shared beyond one cell, a threaded server
with a connection lock is the named fallback. The deferred
`--full`-via-content-store routing (below, under *Provisioning*) stays
deferred, but `full` already rides the wire contract, so that work lands
server-side with no client change.

### Provisioning: how a cell gets its record

The predict/evaluate provisioning commands (`provision-snapshot`,
`materialize-event`) source a cell's `record/` — the point-in-time snapshot,
its filed-document text, and the event — from the **content store**
(`--corpus-backend casestore`, the default under the corpus-split mode, so the
whole forward fleet reads one store without per-command flags; an explicit
`--corpus-backend` still wins), proven byte-identical across backends by a
parity gate (`tests/test_provision_casestore.py`). The `casestore` backend has
no query surface, so `query` / `stats` / `open-events` / scope reconcile read
the index — locally pulled or ranged in place — and `cert-backtest` replay
reads its redacted snapshots from the store through the payload read source.
One reader is deliberately not store-routed: `query --full` /
`--include-opinion` reads the opinion body from the `cases` column, empty in
the payload-free index — a documented follow-up.

`provision-snapshot --refuse-terminal` (used by the `run-predict` forward path
only) is the forward-cell guard at the provisioning seam: it refuses to
provision a forward cell whose snapshot's latest entry reads terminal — a
forward prediction on a decided case would be a mislabeled back-test. A refused
cell is a legitimate outcome, not an error; the prompt contract tells the agent
to note the gap in `flags.json` and predict from priors and base rates only,
without retrieving the case's current docket state (the case already looks
decided, so its outcome is retrievable — the prompt's predict-as-if-undecided
rule governs).

One direction under consideration — not a commitment: the cells could
eventually retrieve case records from CourtListener itself at run time instead
of a provisioned store read; the corpus would remain the system of record for
ingestion, analytics, and back-testing.

### Developer access (Codespaces)

Interactive data discovery belongs in a codespace, not a workflow. The remote
serves it in two modes, both strictly **read-only** (see
[security.md](security.md)): **ranged queries** for quick lookups
(`--corpus-backend ranged` on `query` / `open-events` / `corpus-info` —
per-query egress in KBs) and **a deliberate full pull** for scan-heavy
exploration (`uv run fedcourts corpus-pull`). Default to ranged:
Codespaces runs on Azure, so every full pull is cross-cloud S3 egress.

Credentials arrive as **user-scoped** Codespaces secrets — never repo-level,
never committed: the **maintainer** via IAM Identity Center (short-lived SSO
sessions assuming the read-only role, configured by the devcontainer's
post-create hook), **contributors** via a dedicated read-only IAM user's key
pair, provisioned on demand (see [security.md](security.md)). The hook exports
the remote URL as `CORPUS_REMOTE_URL`, exactly the env contract the workflows
use; absent secrets it prints a note and succeeds — the offline fixture loop
and the full gate need no remote.

### Corpus schema

Each corpus row is a normalized, **labeled** record: identifiers, dates, the
realized `disposition` (making the corpus a ready-made back-testing set),
judges/panel/parties, topic, citations, the live-parsed cert signals, and
tracking state — defined and enforced in
[`fedcourtsai.corpus`](../src/fedcourtsai/corpus.py), with the column reference
in [corpus/README.md](../corpus/README.md). The SQLite format is internal; the
stable contract is the row schema, whose ids and `Disposition` vocabulary are
shared with the ledger models.

### Consumers of the historical corpus

- **Back-testing** — replay predictors against historical *resolved* events
  (outcome hidden at predict time): `fedcourts backtest` (the `backtest`
  stage → `metrics/backtest.json`) and the maintainer-triggered `cert-backtest`
  engine replay.
- **Base-rate aggregation** — `fedcourts stats` on demand, and the published
  **statpack** (`fedcourts statpack` → `metrics/statpack.{json,md}`, kept fresh
  by `run-analytics`'s weekly metrics-refresh job); its cert statistics count
  each live/historical-slice row `sample_weight` times, so the walker's denial
  sampling never biases a published rate, and the per-Term array carries the
  cursor-derived filings census and walk-complete flags.
- **Retrieval** — a handful of *relevant* priors at prediction time:
  `fedcourts query` (and `corpus.retrieve_priors`) — exact-match filters on
  court / topic / disposition plus overlap filters on judges and citations,
  ranked, defaulting to resolved cases. Semantic / embedding similarity lands
  on the same query seam once embeddings are stored.

How much a back-test score is allowed to mean is fixed by the pre-registration
stratification ([`fedcourtsai.leaderboard`](../src/fedcourtsai/leaderboard.py)):
**forward predictions are the test set; the back-test is the validation set.**
No redaction removes a model's parametric memory of a famous case, so back-test
deltas drive the iteration loop while predictor *skill* is only ever claimed
from forward cells; back-test reports carry a hard-coded `retrospective`
stratum, and the leaderboard never blends the strata. The replay/forward
difference is deliberately *behavioral, not technical* — the **leakage
doctrine** in [AGENTS.md](../AGENTS.md): timing is the leakage control, and a
`replay` cell gets the same tools plus etiquette, harness-side retrieval
logging, and evaluator grading instead of walls. The live cells run over a
`Runner` seam (`fedcourtsai.pipeline.runner`); an offline `stub` backend writes
deterministic, schema-valid artifacts with no model call, and `fedcourts
make-fixture-corpus` builds a tiny **synthetic** corpus, so the cell mechanics
are exercised in pytest with no remote, token, or network.

## Historical — the Term walker

- **Trigger:** the `run-seed` workflow's cron windows (four dead-zone slots a
  day, or manual dispatch). No trigger label: nothing an outside actor can file
  fires it. It shares run-pull's `corpus-write` lock, so it still serializes with
  the forward writers despite the separate schedule.
- **Each run** (deterministic, no agent, no API secret): loop
  `fedcourts historical-terms` in checkpointed chunks — walk the configured
  October Terms' docket serials newest-first from the persisted per-(Term,
  stream) cursors → ingest each sampled decided petition through the shared
  live path, landing it already resolved (label, snapshot, events latched
  closed, OT2021+ documents provisioned) → push the corpus and commit the
  pointer per chunk (under the `corpus-write` lock) → write progress to the
  Actions step summary. Each window is a bounded chunk (≤40 min) under one App
  token, so no mid-loop token re-mint is needed. The cursors advance over every
  served serial (a 404 never advances them), so a capped or crashed run resumes
  gap-free; see [live-sources.md](live-sources.md) for the walk design.
- **Sampling frame:** every decided petition is ingested except denials, kept
  when their serial is a multiple of `historical.denial_sample_every` —
  deterministic per serial, so resumed runs keep the identical sample.
  Undecided petitions are skipped entirely (pending matters are the forward
  poller's charter), so the walker writes **no** predict/evaluate handoffs, ever.
- **Scope maintenance:** after the loop, the job runs `fedcourts
  reconcile-scope --apply` — the predict-scope latch sweep rides one run-seed
  window a day (gated to keep its daily cadence) because the corpus is already
  pulled and pushed there.

## Pull — forward freshness

- **Trigger:** an intraday cron (several windows a day), `workflow_dispatch`,
  or a maintainer-applied `run:pull` label. The day's windows share one
  short-lived `pull-log` issue (its label is deliberately not a `run:*`
  trigger label).
- **Budget governor:** a per-run cap (`max_cases_per_run`) with
  **oldest-`last_pulled`-first rotation** and skip-closed/resolved, sized to
  the active CourtListener tier's ceilings; a slice of each run
  (`eligible_refresh_reserve`) is reserved for the stalest SCOTUS dockets, so
  the in-scope set rotates ahead of the much larger active set.
- **Two forward jobs over the shared core:**
  1. **Refresh** active known cases (`pull_case`), queuing `run:predict` for
     changed cases with open events — unless the refreshed docket already looks
     decided (its *latest* entry reads terminal, or its open events surfaced an
     unrecorded outcome). Such a case is diverted to the run's
     `predict_skipped_decided` list and surfaced on the log issue instead of
     queued: a forward cell on a decided case would be a mislabeled back-test.
     The live job applies the same routing.
  2. **Detect resolution** of tracked open events → write `outcome.json`
     deterministically when the disposition is machine-readable, and queue
     `run:evaluate` **when the ledger holds a prediction to score**
     (ground-truth recording is ungated; the evaluator fan-out is). Anything
     ambiguous lands on the runner-local **unrecorded queue**, surfaced
     per-case on the daily log issue for maintainer triage; no issue is filed.

## Event definition — deterministic, corpus-driven

Defining the **predictable events** of a docket is its own stage
(`fedcourtsai.pipeline.events`), decoupled from ingestion, so it runs once over
an ingested docket regardless of channel. It is classification, not analysis:
every event is pinned to a single docket entry with a closed `kind` enum
(`motion` / `petition` / `appeal` / `order`), and every docket carries the
**baseline** event — the disposition of the appeal, or the petition at SCOTUS —
even when no entries are machine-readable. An event is
**predictable/unresolved** while no later disposing order references its entry
(with no citation the stage does not guess); an entry matching more than one
`kind` is surfaced for triage rather than classified — the default path runs
no agent.

**Dormant: the discovery frontier.** CourtListener forward discovery is off
(`pull.discover_new_filings: false`) — the live channel onboards SCOTUS
filings — but the mechanics stay correct and reactivate with the flag. It
searches each court from a per-court **discovery watermark** held in the
corpus; two rules keep the frontier gap-free (the live channel's per-Term
cursors mirror the same semantics): the watermark only moves forward (a re-run
never rewinds it), and a no-results run still advances it to a date already
searched — so a court that keeps finding nothing resumes where it left off,
and can never skip a real filing.

## Steady state

History sits in the corpus, in the historical Term set the walker keeps growing
newest-Term-first. **SCOTUS freshness is the live channel's**: frontier probing
onboards new petitions within a cycle, the watchlist refresh catches
distributions and resolutions within days of the conference; pull's windows
spend the API budget on enrichment of the in-scope SCOTUS set. The
*prediction-relevant* slice — every pending petition and its originating docket
— is complete to within one live cycle, while circuit breadth advances only as
enrichment reaches it.

## Data validation

Two stores that must agree, an append-only remote, and a schema that is law
give the data **invariants** worth asserting on their own, distinct from
`run-ops`'s run-health analytics. Three layers:

- **Schema conformance** — every git-ledger artifact under `data/` validates
  against its model (`fedcourts validate`, in the local gate and PR CI, and on
  the schedule to catch anything that bypassed the gate).
- **Corpus integrity** — the committed pointer resolves, the corpus opens, its
  row count only ever **grows**, required columns are non-null, dates are
  ordered and not future-dated, coded columns hold declared vocabulary, and no
  id is duplicated (opinion-presence checks read the retained `has_opinion`
  bit; payload integrity is the content store's write-once discipline).
- **Referential integrity** — every judgment references an event and case that
  exist in the corpus, and every evaluation targets a real prediction.

The corpus-dependent layers run as `fedcourts validate-corpus`, **produced
where the corpus is already pulled** (a non-blocking trailing step on the
corpus-writer path, publishing the verdict alongside the live-frontier
readiness snapshot); `run-ops` — a corpus-free presenter — renders the
**data-health** section from the verdict and escalates a failure to a single
long-lived issue: loud, never blocking. Because event definitions live in the
corpus, the predict/evaluate workflows materialize each event's `event.yaml`
into its ledger directory (`fedcourts materialize-event`) so the judgment PR
carries it — and the deterministic outcome writer materializes it beside every
`outcome.json` it writes, refusing to write an outcome whose event the corpus
does not hold.
