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
  opinion with no machine-readable disposition**, **non-substantive
  stay/emergency applications** (`22A123` — an extension or unreadable ask; a
  *substantive* application is the interim predict scope, see
  [salience.md](salience.md)) and **original-jurisdiction** matters (`22O141`),
  **pro se / in-forma-pauperis petitions** (the IFP docket serial ≥ 5001 — a
  documented scope decision so the salience gate spends the fundable slice on the
  paid cert docket; see [salience.md](salience.md)), **disbarment dockets**
  (attorney discipline, not discretionary cert), **consolidated dockets whose
  members all classify out of scope**, and a guard for
  **internally inconsistent dates**. Each gates prediction only, never ingestion.
  The two-directional scope reconcile releases any case whose exclusion stops
  matching — one latched for **staleness**, a **bare published-opinion
  import**, an undecided **disbarment** docket, a **consolidated** parent
  whose members later resolve, or an **application** whose ask a later poll
  latches as substantive. The purely **form-keyed** exclusions (IFP
  serial, original jurisdiction) are permanent by construction —
  the docket form never changes, so they never release. Because the corpus keys a case by
  `<court>/<docket>`, a case's SCOTUS docket and its originating
  court-of-appeals docket are **separate rows**: only the SCOTUS row is
  predicted, and the lower-court link columns (`originating_court` /
  `originating_docket_number`) are retrieval context — never a scope trigger.

  Within this prediction scope, [salience.md](salience.md) describes a live
  **salience-ordered** gate — hard eligibility filters, then a deterministic
  ranking that spends the tournament on the most salient slice up to a fundable
  capacity — plus the two pre-registered scores (deterministic salience and the
  model-produced big-case score) and the segment base rate that anchors them.

## The binding constraint: the CourtListener API budget

CourtListener's REST API is throttled per token (see [budget.md](budget.md)
for the held tier); the in-process governor (`courtlistener/ratelimit.py`)
throttles to whatever ceilings the prod environment sets
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
(`ingest.from_bulk_row`) — note the storage projection withholds the
cluster-derived fields from bulk-sourced circuit rows (`to_corpus_row`; the
predicate keys on the channel), so a replica with a sound cluster join must
revisit that carve-out — and the bulk-cluster scrub sweep beside it, whose
stored-state predicate treats those fields as bulk-provenance marks on any
non-SCOTUS row (the only other channel that writes them is the SCOTUS-scoped
opinion enrichment, so a non-SCOTUS row's are the bulk join's; a replica
channel writes them at every court, so the sweep must be retired or re-scoped
before the replica does). Adoption also needs a terms review of the agreement;
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
| Charter   | decided history, newest Term first      | keep CourtListener records current | pending petitions & applications, granted dockets to judgment: discovery, watchlist, outcomes |
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
   read/write paths: set on the `prod` environment, default
   **off** so a dev environment without the store (the fixture loop, offline
   tests) reads and writes a single self-contained blob. The store's location
   comes from `FEDCOURTS_CASESTORE_URL` (wired at job level in the writer
   jobs — `run-pull` and `run-seed`);
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

The judgment file itself (`prediction.json` / `evaluation.json`) also carries one
harness-written field, `process_version` — the stamp of the process that produced
the cell (prompt template + resolved registry config, hashed to a content
`digest`). Like `usage.json`, it is the harness's word, not the agent's: a
post-agent `stamp-cell` step injects it from the registry in force at run time.
Headline metrics partition on this digest so the July/August shakedown is
excluded from the frozen board without deleting it. See
[process-version.md](process-version.md).

**Repo-level roll-ups** sit outside the per-case tree, each a deterministic,
offline function of the corpus regenerated and committed for review: the
`metrics/` artifacts (leaderboard, backtest, statpack, and the court-facing
docket pack) and
`data/scope/scope.json`, the published prediction-scope decision
(`predict_eligible` / `predict_excluded` / reason / `sample_weight`) for the
already-public case set. Leaderboard, backtest, and statpack refresh on the
analytics workflow. The other two are regenerated by hand and PR'd, and they
read opposite sources, so their disclosure properties differ. The **scope
manifest** (`fedcourts scope-manifest`) is enumerated from the committed
`data/cases` tree alone, never a corpus scan, so it discloses only the
already-public set and cannot enumerate the wider ingested corpus; regenerate it
when that set or its scope latches move. The `data/qp-topics/` artifacts are
**not** roll-ups, and both carry the deliberate disclosure exception argued in
`docs/qp-topic.md`. `qp-topic-reference.json` is hand-authored judgment (the
`qp-topic-v0` measurement baseline), edited only in an interactive session and
only via its own reviewed staging PR — neither the deterministic writers nor any
workflow regenerates it. `qp-topics.json` is machine-produced and appears once a
labeling run has produced one: that run's per-case labels, written by
`run-analytics`'s agent-backed `qp-topic-label` mode (`fedcourts qp-topics`,
which refuses to write below the publication gate) and landed as a reviewed PR
to `main` on the fixed `qp-topics/refresh` branch, never auto-merged. It is a
whole-file replacement per run, not an accumulating ledger. The **docket
pack** (`fedcourts
docket`) aggregates the whole corpus — it publishes counts and rates over every
ingested row, never a row itself — so it moves whenever the corpus does, and the
committed copy is a point-in-time snapshot that nothing schedules or gates (see
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

The workflow variable is `CORPUS_REMOTE_URL`. The tooling also accepts
`DVC_*` aliases so the Codespaces devcontainer secret — spelled
`DVC_REMOTE_URL` — keeps resolving; the new names win when both are set, and
the aliases retire once that secret is renamed.

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
historical walk's per-chunk checkpoint and its dedupe and scope-latch steps by
calling the script directly. It rebases onto any advance and retries a *transient* push failure (a
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
with a connection lock is the named fallback. `full` rides the wire contract,
and the opinion-body hydration it triggers lives in the shared payload shaper,
so the service serves a full body with no client change — the sidecar is the
credentialed process, which is what lets a credential-free cell ask for one.

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
`query --full` is the one reader that needs a payload the index does not hold:
it hydrates each prior's opinion body from the store through the same payload
read source, inside the shared payload shaper so the CLI and the query service
behave identically — the sidecar is the credentialed process, which is what
lets a credential-free cell ask for a body at all. The hydration is gated on
`full` *and* on the row's retained `has_opinion` bit, so the default path never
leaves the index and an opinion-less prior costs no store request. It degrades
rather than fails: a case whose `case.json` was never mirrored, and a store that
cannot be read at all, both yield an empty body, because the rows are shaped and
emitted one at a time and a raised error would truncate the result stream.

Two **preconditions** gate whether a body actually comes back, and one write
satisfies both: `has_opinion` is set only from a non-empty `opinion_text` at row
construction, and `case.json` is mirrored only by `upsert_rows` — so a body that
does not arrive through the ingestion upsert reaches neither the bit nor the
store. **Opinion enrichment** (`enrich-opinions`) is the channel that supplies
it. Per case it resolves the docket's published opinion cluster — from a stored
REST-shaped snapshot's `clusters` links where there is one, else a docket fetch
— takes the cluster's reporter citations and `citation_count`, and takes the
first sub-opinion's `plain_text` as the body; the row then goes through the same
upsert every other channel writes through, so the presence bit derives and the
content store re-mirrors in the same step. Only the *body* is conditional: a
cluster whose opinion carries no extracted text still lands its citations,
rather than having a body scraped out of the HTML rendering.

Because `has_opinion` latches, a wrong body is permanent — the row stops
matching the pass's own predicate and no later run revisits it — so the pass
**refuses rather than guesses**: a docket linking several clusters is skipped
(nothing in the list says which is the decision), a fetched cluster must name
the docket it was reached from, and an opinion whose upstream `type` marks it a
separate writing (a concurrence, a dissent) never becomes the case's body. Each
refusal is a counted line in the run's report.

Its **scope is its budget argument**. The pass walks the cert-granted SCOTUS
slice only — rows carrying `date_cert_granted`, which is grants and GVRs
together: ≈1,250 all-time and ≈120–130 a Term — at up to three REST requests a
case (docket, cluster, opinion), dropping to two on the rare row whose newest
snapshot is REST-shaped rather than the live channel's, and to one on a case
that stops at the docket. So ≈3,750 requests bounds a sweep of the standing
backlog in which every case reaches its opinion, and ≈400 a Term bounds a
Term's new grants, against the held
Tier-4 ceiling of 1,400/day of which the four daily pull windows commit ≈360
(30 dockets × ~3 requests × 4 windows — see [`config/tracking.yaml`](../config/tracking.yaml)
and [budget.md](budget.md)). `--max-cases`
(default 50, ≈half the 300/hr ceiling at three requests a case) bounds one
run's spend ahead of the client's own governor, so the
pace is the operator's choice rather than a race with the pull rotation — and
because the governor is per-process, not shared across runs, the pass is run
outside a pull window rather than beside one. Convergence is not monotone: a
grant that never publishes an opinion (a GVR, a DIG) is retried every run, and
so is a decided grant whose docket links no cluster upstream — the walk's
dominant refusal, since the id a granted row carries is its petition-stage
docket and the published cluster hangs off it only sometimes. Both residues
head a `case_id`-ordered walk, so they have to be raised past, not waited out —
and because a refused case stops at its first request, a sweep's spend sits
nearer the row count than the bound above while the coverage it buys is only
the rows that reach a cluster. The
same arithmetic is why the pass is *not* pointed at the whole corpus: opinion
coverage at bulk scale is the replication channel's problem
([data-sources.md](data-sources.md)), not more REST.

Filling the bit for this slice is what makes the `--full` read path live, and it
lands bodies for exactly the population the merits forecast stream is about — so
a replay cell's prior retrieval can return full SCOTUS opinion text. The
retrieval cutoff (`decided_before`) and the mode contract are the controls that
keep that honest, and they bind wherever the bit is filled.

`provision-snapshot --refuse-terminal` (the forward predict path's guard —
`run-predict` in production, mirrored by the integration harness) refuses a
forward cell at the provisioning seam through three gates, mechanical-first:
the **record gate** asks whether the event's outcome already *exists* — a
committed `outcome.json`, the corpus event's `resolved` flag, or the row's
latched outcome for the event's stage. Under the casestore backend the
production fleet provisions from (the corpus-split default), the source
exposes events but no rows, so the row-level half consults the corpus index
through the ordinary read backend — the cell workflows' provisioning step
carries the index credentials beside the casestore URL — and when no index is
reachable the event-keyed checks still gate the cell while the skipped half
is a spoken warning. The **staleness
bound** (`--max-snapshot-age-days`, off at the default of 0; `run-predict`
arms it at 10 days, generous against the live poller's daily-ish refresh) refuses a snapshot old enough to predate a pipeline pause: such a
snapshot passes every content check by construction, because it was taken
before anything it should disclose happened, and its case may be genuinely
pending — the refusal is about the input being stale, not the case being
decided. Only then does the **textual scan** ask whether the snapshot
discloses **its own event's** outcome. A forward prediction on a decided
event would be a mislabeled back-test. The question is keyed on the event
(`--event`), because one docket carries several events' outcomes at once: a
granted cert docket's grant order is a disclosed *cert* outcome and is also
what opens the merits proceeding, so the entry that must refuse a cert cell
is the merits cell's own record. On the merits event the test is therefore a
parsed merits judgment (and, record-side, the latched judgment); on every
other event it is any entry reading terminal, any entry carrying a
machine-readable disposition order, or — on an application docket — a legible
interim disposal. The predict matrix applies the same openness question one
seam earlier (`predict-matrix` drops a listed event the corpus records
resolved, wherever the scope gate consults the corpus at all — under
`predict.scope: all` neither does), so a stale trigger issue sheds its closed
events at plan time instead of minting cells this guard then refuses one by
one. A refusal
(exit 3) is a legitimate outcome, not an error — and it **short-circuits the
cell**: the workflow withholds the agent token, the retrieval config, the
engine steps, and the event materialization, so a refused forward cell
produces nothing rather than a context-less prediction claiming a mode it
never had. The cell's status records `produced=false` and the collect census
warns per cell. Only the other non-zero provisioning exit — no snapshot in
the corpus at all — keeps the best-effort shape: that cell runs snapshot-less,
notes the gap in `flags.json`, and predicts from priors and base rates only
per the prompt contract.

One trust boundary to keep in view: `record/context.json` is written by
provisioning but *lives in the agent's workspace* for the run, so the post-run
consumers that read it back — `stamp-cell` for the context block,
`record-retrieval --mode-from-context` for the log's mode — treat its
harness-written provenance as a statement about the writer, not
tamper-resistance, and accept its mode only inside the declared vocabulary
(anything else falls back to the caller's word, with a warning).

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
judges/panel/parties/attorneys/counsel, topic, citations, the live-parsed cert
signals, and
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
  each live/historical-slice row `sample_weight` times, so denials the earlier
  sampled walk kept at a higher weight never bias a published rate, and the
  per-Term array carries the
  cursor-derived filings census and walk-complete flags. The **docket pack**
  (`fedcourts docket` → `metrics/docket.{json,md}`) is the court-facing cut of
  the same machinery — the docket-composition sections plus a paid/IFP split and
  a pooled per-Term census, and no claim about this project's predictions.
- **Retrieval** — a handful of *relevant* priors at prediction time:
  `fedcourts query` (and `corpus.retrieve_priors`) — exact-match filters on
  court / topic / disposition plus overlap filters on judges and citations,
  ranked, defaulting to resolved cases. Semantic / embedding similarity lands
  on the same query seam once embeddings are stored.

How much a back-test score is allowed to mean is fixed by the
**backtest-as-iteration doctrine** — forward predictions are the test set, the
back-test is the validation set, and timing rather than any retrieval wall
separates them — stated in full under *Forward vs retrospective* and *The
backtest-as-iteration doctrine* in [metrics/README.md](../metrics/README.md).

The live cells run over a `Runner` seam (`fedcourtsai.pipeline.runner`); an
offline `stub` backend writes deterministic, schema-valid artifacts with no
model call, and `fedcourts make-fixture-corpus` builds a tiny **synthetic**
corpus, so the cell mechanics are exercised in pytest with no remote, token,
or network.

## Historical — the Term walker

- **Trigger:** the `run-seed` workflow's cron windows (four dead-zone slots a
  day, or manual dispatch). No trigger label: nothing an outside actor can file
  fires it. It shares run-pull's `corpus-write` lock, so it still serializes with
  the forward writers despite the separate schedule.
- **Each run** (deterministic, no agent, no API secret): loop
  `fedcourts historical-terms` in checkpointed chunks — walk the configured
  October Terms' docket serials newest-first from the persisted per-(Term,
  stream) cursors → ingest each decided petition through the shared
  live path, landing it already resolved (label, snapshot, events latched
  closed, OT2021+ documents provisioned) → push the corpus and commit the
  pointer per chunk (under the `corpus-write` lock) → write progress to the
  Actions step summary. Each window is a bounded chunk (≤40 min; the daily sweep window
  walks 25 to fund its trailing sweeps) under one App
  token, so no mid-loop token re-mint is needed. The cursors advance over every
  served serial (a 404 never advances them), so a capped or crashed run resumes
  gap-free; see [live-sources.md](live-sources.md) for the walk design.
- **What it keeps:** every decided petition, denials included. The walk must
  probe a serial before it can read the disposition, so declining to store one
  never saved a fetch — it only cost every rate computed over the result a
  denominator it had to reconstruct from weights. Corpus breadth is cheap; the
  expensive stages are predict and evaluate, which *select* from the corpus, and
  sampling belongs there because it is reversible there. Undecided petitions are
  skipped entirely (pending matters are the forward poller's charter), so the
  walker writes **no** predict/evaluate handoffs, ever.
- **Re-walking:** a Term walked to its frontier is invisible to later runs, so
  run-seed's manual dispatch carries `refresh_terms` / `refresh_streams` (blank
  on every scheduled window): it runs `fedcourts refresh-historical --apply`
  after the pull and before the loop, clearing the named Terms' cursors so the
  reset and the re-walk it implies are one serialized operation under the
  `corpus-write` lock. Re-walking **adds rows** — every re-served docket upserts
  through the same latches, so no row is deleted and `case_id` never moves — but
  an unlatched column takes the fresh parse, so a tightened parser retracts a
  stale reading as well as adding a missed one (`docs/cli.md`).
  The CLI is dry-run by default; the cost is upstream traffic, not risk to the
  corpus.
- **Maintenance sweeps:** after the loop, one window a day also runs seven
  converging sweeps in order — `fedcourts dedupe-live-rows --apply` (merging
  live-minted duplicate rows), `fedcourts reconcile-scope --apply` (the
  predict-scope latch sweep), `fedcourts relabel-application-events --apply`
  (application baselines to their motion/interim identity), `fedcourts
  backfill-merits-judgments --apply` (the judgment a merits-bound grant
  received), `fedcourts backfill-merits-events --apply` (the open merits
  forecast events on granted, undecided dockets — ledger `event.yaml` files
  staged in the same commit as the pointer, with the moment-column stamp
  `fedcourts backfill-event-moments --apply` riding the step first), and the
  attribution repairs (`fedcourts remove-unmintable-events --apply` then
  `fedcourts reopen-misattributed-outcomes --apply` — ledger deletions and
  rewrites staged in the one pointer commit, removal first so the entry-pinned
  case clears the reopen sweep's baseline-pair triage in the same window, each
  refusing to apply above its per-run blast-radius cap), and `fedcourts
  scrub-bulk-cluster-fields --apply` (the stored circuit slice's misjoined
  bulk cluster fields, dropped from the rows nothing re-serves — keyed on
  the fields no channel could have written to a non-SCOTUS row, the ingest
  projection's
  carve-out converged, refusing above its own blast-radius bound). Dedupe
  first, so the latch pass weighs deduped rows; the event mint immediately
  after the judgment backfill, so pendency is judged on judgment columns as
  latched as the stored snapshots allow; each is idempotent, so a converged
  corpus costs seconds. All ride run-seed (gated to keep their daily cadence)
  because the corpus is already pulled and pushed there; the sweep window's
  walk budget yields time for them (25 min against the other windows' 40),
  so the sweeps' bounded worst case never gambles the job cap.

## Pull — forward freshness

- **Trigger:** an intraday cron (several windows a day), `workflow_dispatch`,
  or a maintainer-applied `run:pull` label. Each window that ends in success
  or failure lands its row on the long-lived pipeline-runs dashboard issue; a
  failing window also opens a `pull-log` issue for a human, and a window
  cancelled mid-run (timeout, manual stop) gets only that alarm issue, no
  dashboard row (`run-log-dashboard` and `pull-log` are deliberately not
  `run:*` trigger labels — see [pipeline.md](pipeline.md)).
- **Budget governor:** a per-run cap (`max_cases_per_run`) with
  **oldest-`last_pulled`-first rotation** and skip-closed/resolved, sized to
  the active CourtListener tier's ceilings; a slice of each run
  (`eligible_refresh_reserve`) is reserved for the stalest SCOTUS dockets, so
  the in-scope set rotates ahead of the much larger active set.
- **Two forward jobs over the shared core:**
  1. **Refresh** active known cases (`pull_case`), queuing `run:predict` for
     changed cases with open case-baseline events — unless the refreshed docket already looks
     decided (its *latest* entry reads terminal, or its open events surfaced an
     unrecorded outcome). Such a case is diverted to the run's
     `predict_skipped_decided` list and surfaced on the job's Actions run log
     (the CLI's own output) instead of
     queued: a forward cell on a decided case would be a mislabeled back-test.
     The live job applies the same routing.
  2. **Detect resolution** of tracked open events → write `outcome.json`
     deterministically when the disposition is machine-readable, and queue
     `run:evaluate` **when the ledger holds a prediction to score**
     (ground-truth recording is ungated; the evaluator fan-out is). Anything
     ambiguous lands on the runner-local **unrecorded queue**, surfaced
     per-case on the pipeline-runs dashboard for maintainer triage; no issue
     is filed. A recorded cert **grant** that opens a merits proceeding —
     `granted` / `granted-in-part`, not a GVR or summary reversal, which
     terminate the case at the cert order — also mints the case's **open
     merits event** (`evt-order-judgment`, kind `order`, stage `merits`,
     opened on the grant date), so the granted docket stays in the live
     rotation and keeps polling toward its judgment instead of exiting the
     pipeline at the grant. On every later re-poll the
     already-attributed cert disposition is recognized as the record of the
     petition's resolution — a clean no-op, not a triage entry — until the
     judgment lands: the live ingest latches the parsed merits pair onto the
     row (`merits_judgment` / `merits_decided`, the shared
     `pipeline/judgment.py` parser the offline backfill also runs),
     detection resolves the open merits-stage
     event from those columns (`Outcome.judgment` plus the disturbed binary
     as `actual_granted`; an undated parse surfaces for triage instead of
     guessing a `resolved_at`), and the docket exits the rotation with its
     last open event. An open merits event is *usually* forecastable, but open
     is not the test: `store.forecastable_events` admits it on a row whose grant
     opened a merits proceeding, whose judgment is unlatched **and** whose
     proceeding is not recorded terminated, so the granted docket queues a
     merits predict cell the way an application docket queues its interim one.
     The terminated arm is what separates the two: a case that ended with no
     disposition (a post-grant Rule 46 dismissal, a docket whose only terminal
     notation is the mandate) keeps its merits event open, because nothing
     resolves an event on a row carrying no judgment — but there is no longer a
     judgment to forecast, so the event stops earning cells and simply sits.

## Event definition — deterministic, corpus-driven

Defining the **predictable events** of a docket is its own stage
(`fedcourtsai.pipeline.events`), decoupled from ingestion, so it runs once over
an ingested docket regardless of channel. It is classification, not analysis:
every event is pinned to a single docket entry with a closed `kind` enum
(`motion` / `petition` / `appeal` / `order`), and every docket carries the
**baseline** event — the disposition of the appeal; at SCOTUS, of the cert
petition (`stage = cert`) on a `YY-NNNN` docket or of the application on a
`YYAnnn` interim docket (a stay/injunction application is a motion under the
interim standard, so its baseline is `kind = motion` / `stage = interim`) —
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
distributions and resolutions within days of the conference (and retains a
granted docket, on its open merits event's account, until the judgment), and
the capped application rotation keeps re-polling unresolved interim
applications until
their outcomes and escalation signals land; pull's windows
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

  The path that bypasses it is the **deterministic writers**: pull, live, and
  seed commit to `main` directly, with no PR and therefore no gate. So a writer
  that lands a malformed or orphaned artifact reddens the data stage on *every
  open PR at once*, since each one validates the whole tree it checked out —
  the failure surfaces far from its cause and looks like the PR's own fault.
  **When a PR's data check fails for no reason you can find in its diff, check
  `main` first**: validate a clean checkout of the default branch, and if that
  fails too the fix belongs in the writer, not the PR.
- **Corpus integrity** — the committed pointer resolves, the corpus opens, its
  row count only ever **grows**, required columns are non-null, dates are
  ordered and not future-dated, coded columns hold declared vocabulary, and no
  id is duplicated (opinion-presence checks read the retained `has_opinion`
  bit; payload integrity is the content store's write-once discipline).
- **Referential integrity** — every judgment references an event and case that
  exist in the corpus, every evaluation targets a real prediction, and every
  prose document a prediction names exists beside it (so a pointer to a document
  the cell never wrote fails rather than passing as a valid record).
- **Record completeness** — a row that should have resolved by now has. A cert
  grant that opens a merits proceeding and is more than two Terms old, carrying
  neither a parsed judgment nor a recorded termination, is a decided docket the
  record never captured rather than a pending case, and every row-keyed merits
  gate reads it as forecastable. Unlike the two layers above this one cannot
  fail on a well-formed corpus alone — it measures the sweeps' coverage — so it
  names the cases whose record needs mending.

The corpus-dependent layers run as `fedcourts validate-corpus`, **produced
where the corpus is already pulled** (a non-blocking trailing step on the
corpus-writer path, publishing the verdict alongside the live-frontier
readiness snapshot); `run-ops` — a corpus-free presenter — renders the
**data-health** section from the verdict and escalates a failure to a single
long-lived issue: loud, never blocking. Because event definitions live in the
corpus, the predict/evaluate workflows materialize each event's `event.yaml`
into its ledger directory (`fedcourts materialize-event`) so the judgment PR
carries it — **on first touch only**: a file already present at the ledger
path is never rewritten by a cell, because data PRs are additive-only and a
corpus row that gained fields since the commit would otherwise turn every
later run PR into a jailed modification (drift is warned, not written). The
deterministic outcome writer is the asymmetry: it materializes the definition
beside every `outcome.json` it writes on its own writer lane, refusing to
write an outcome whose event the corpus does not hold — so the committed
definition converges at resolution even where cells left it at its
first-touch shape. An event definition also names its **stage** — the
decision standard that governs it (cert, interim, or merits) — carried from
the corpus row into `event.yaml` at that first materialization, so a cell and
its consumers read the standard from the record rather than inferring it from
the event id (a file older than the stage axis simply records none, which
reads as the null below). The field is nullable and
null means **no stage recorded**: either no Supreme Court standard governs the
event (a circuit appeal), or the writer does not classify one there yet;
consumers treat null as "no rule", never as a guess.
