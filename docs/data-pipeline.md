# Data pipeline: ingestion & freshness

How case data enters and stays current in `fedcourtsai`. This is the design
contract for the ingestion channels — the **pull** (CourtListener enrichment),
**live** (forward SCOTUS poll), and **historical** (Term walker) jobs. For the
label/workflow mechanics see [pipeline.md](pipeline.md); for the on-disk shapes
see [data-model.md](data-model.md).

## Scope

Two different scopes apply, and keeping them apart is what bounds the bill:

- **Ingestion scope — the full set.** The ingestion channels assemble the
  **Supreme Court and all 13 federal courts of appeals**:

  ```
  scotus  ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11  cadc  cafc
  ```

  District courts are intentionally **out of scope** for now. Ingestion is
  deterministic script work — the supremecourt.gov channels spend no API budget,
  pull is bounded by the CourtListener throttle — so it is cheap relative to the
  agentic stages. The whole
  corpus is assembled precisely so predict/evaluate can **query the full history**
  for retrieval and back-testing, even for cases they never predict.
- **Prediction scope — the SCOTUS-interaction gate (pilot).** The agentic
  predict/evaluate stages cost one to two orders of magnitude more than ingestion
  (see [budget.md](budget.md)), so in the pilot they run on a deliberate subset: a
  case becomes **in-scope for prediction the first time it interacts with the Supreme
  Court** — a petition for certiorari is the canonical trigger — and **stays in-scope
  for the remainder of its lifecycle**. So a gated case's later merits events, and any
  remand activity back in the courts of appeals, are predicted, while the ~42K/yr
  appeals cases that never reach SCOTUS are ingested but not predicted. The gate
  latches once and never clears; widening it beyond SCOTUS-touched cases is a later,
  cost-data-driven decision ([milestones.md](milestones.md)). One narrowing rides on
  top of the latch: a **pre-1925 mandatory-jurisdiction matter** (detected by its
  bare, non-Term-prefixed docket number, e.g. `801`) is dropped from the
  predict/evaluate set — its `evt-petition-disposition` carries a merits, not a
  discretionary-cert, meaning, so the modern event model does not fit it
  (`corpus.is_historical_mandatory`). Ingestion still covers it; only prediction
  is gated. Sibling narrowings drop other cases the modern cert model cannot
  score: a **stale, still-open petition** from a long-past October Term
  (`corpus.is_stale_unresolvable`); one whose only outcome signal is a **published
  opinion with no machine-readable disposition** — decided, but the outcome lives
  only in the opinion text and is a merits, not a cert, label
  (`corpus.is_published_opinion_unresolvable`); a **stay/emergency application**
  (`22A123`) or **original-jurisdiction** matter (`22O141`), whose disposition is a
  stay or merits ruling rather than a cert grant/deny
  (`corpus.is_non_cert_scotus_form`); and a court-agnostic guard for a case with
  **internally inconsistent dates** (`corpus.is_date_inconsistent`). Each gates
  prediction only, never ingestion, and the two-directional scope reconcile releases
  any case that later gains a real disposition.

  Because the corpus keys a case by `<court>/<docket>`, the *same real-world case's*
  SCOTUS docket and originating court-of-appeals docket are **separate rows**. Both
  belong in scope, so when a SCOTUS docket is ingested carrying a lower-court link
  (CourtListener `appeal_from` + `originating_court_information.docket_number`, stored
  as the `originating_court` / `originating_docket_number` corpus columns), the
  ingestion seam latches the matching *tracked* CoA docket eligible too — joining on
  court id + normalized docket-number string. The REST (pull) path carries that docket
  number; a bulk-shaped path does not (CourtListener publishes no
  originating-court-information bulk table), so it fills only the originating court and
  the precise latch is pull-driven. The match is a conservative exact one — an
  unlinked or untracked SCOTUS docket is a harmless no-op — and, like the SCOTUS latch
  itself, forward-only.

## The binding constraint: the CourtListener API budget

CourtListener's REST API is throttled per token — the free authenticated tier
allows 5 requests/minute, 50/hour, 125/day; the pilot's paid membership tier
raises that (see [budget.md](budget.md) for the held tier and the math). The
in-process governor (`courtlistener/ratelimit.py`) throttles to whatever
ceilings the runner environment sets (`FEDCOURTS_COURTLISTENER_RPM` / `_RPH` /
`_RPD`). At roughly **3 requests per docket** (1 docket + ~2 pages of entries)
the budget is a few hundred dockets a day at most — and the supremecourt.gov
live channel spends none of it.

Because pull runs headless inside a CI job, budget pressure and a degraded
upstream must **degrade a run, never hang it** — a silent stall gets the job
killed at its timeout, discarding even the completed refreshes. Three guards
enforce that, all tuned in `config/tracking.yaml`: the throttle raises rather
than sleep out an hour/day-scale wait (minute pacing still sleeps; the bound is
the client's max-wait setting), a wall-clock deadline (`pull.max_run_minutes`)
stops the rotation between cases, and a circuit breaker
(`pull.max_consecutive_transient_failures`) stops it when consecutive
timeouts/5xx/429s show the upstream is down — each doomed case otherwise burns
a full retry cycle of budget and minutes. However a run stops early, it defers
the unreached cases (their `last_pulled` untouched, so they stay at the front
of the next window's stalest-first rotation), records why, and still writes its
queues and corpus updates.

That cap makes one thing non-negotiable: **the REST API cannot load history.**
The backlog is millions of dockets across 13 circuits; at ~30/day that is
decades. So historical loading and forward enrichment use different sources:

| Channel        | Source                               | Spends API budget? |
|----------------|--------------------------------------|--------------------|
| **historical** | supremecourt.gov **docket JSON**     | No (~0)            |
| **live**       | supremecourt.gov **docket JSON**     | No (~0)            |
| **pull**       | CourtListener **REST API**           | Yes — owns it      |

The supremecourt.gov docket JSON serves every SCOTUS petition of the e-filing
era (OT2017+), so the historical Term walker builds per-Term history without
touching the throttle at all.

## The planned end-state: a CourtListener database replica

Free Law Project offers **replication of the CourtListener Postgres database** —
a commercial subscription feeding a self-hosted, continuously-updated replica.
That is the intended eventual upstream, once the project has the funding for the
agreement and a hosted Postgres to receive it: one source with full field
coverage (docket entries, cert-stage dates, the people/judges directory, the
citation graph), current within replication lag, and **no request caps** — it
collapses the historical/pull source split (breadth vs REST depth) and dissolves
the budget constraint above.

The pivot swaps the **channels**, never the **corpus**. The packed corpus and
its point-in-time snapshots remain the system of record agents read — under
the **leakage doctrine**: *timing is the leakage control; the snapshot
is the provisioned baseline, not a ceiling.* A **forward** cell uses everything
practically available — the outcome does not exist yet, so nothing it can
retrieve leaks it; the snapshot's job is comparability (every predictor in a
fan-out reads the same guaranteed-common baseline, so the tournament compares
predictors, not fetch timing). A **replay** cell gets the *same tools* plus
etiquette (the mode rides in `record/context.json`), harness-side retrieval
logging (`retrieval_log.json`, read from the engine's own transcript), and
evaluator grading — instead of walls. The replay/forward configuration
difference is deliberately *behavioral, not technical* — a written decision:
the dry run validates event formation, prompts, and scoring, not the forward
stratum's evidence availability, and backtest results are iteration signal,
never claimable performance. Either way, the replica arrives as one more source
feeding the same normalized rows — richer, faster ingestion, not a new
consumer surface.

Until then, four guardrails keep interim work from blocking the pivot:

1. **Ingestion stays channel-agnostic.** Everything downstream consumes the
   normalized corpus row; nothing keys behavior on which channel produced it.
   New upstream fields land as columns mapped in the shared normalization layer,
   never as channel-specific side tables.
2. **The API budget governor stays scoped to the REST client.** It is a
   constraint to be deleted, not a dependency: nothing outside pull should build
   on request-scarcity semantics.
3. **Enrichment flows through ingestion into the corpus, never as agent-side
   API calls.** The same rule that protects replay integrity and forward
   comparability today is what makes the replica a drop-in upstream later.
4. **Bulk-CSV-specific tooling stays thin.** The quarterly export is an interim
   source; durable investment goes into the normalization seam and the corpus
   schema, both of which survive the swap.

The **date backfill** (`pull.backfill_reserve`, removed July 2026) was the
worked example of these guardrails: bulk rows lack the decision-time dates
(cert-stage, termination) the replica carries natively, so a slice of each pull
window re-fetched dateless dockets through the existing governor, following the
linked **opinion cluster** when the docket record itself carried no dates. As
the guardrails promised, the selector, reserve, and cluster hop were deleted
with the drip they fed (see the pivot section below), while the durable parts —
the cert-date columns, their normalization-layer mapping, the petition-aware
resolution clock — stayed.

## Pivot (July 2026): retire the bulk-era channels, go live-first

The live-sources track ([live-sources.md](live-sources.md)) made the bulk-era
catch-up channels a dead end before the replica arrived: the supremecourt.gov
docket JSON carries the dispositions, dates, and documents the CourtListener
REST drip could not recover at any budget. What changed:

- **The date backfill is deleted** (selector, `backfill_reserve`, the
  cert-shell feeder `backfill_unresolved_cert_min_term`, and the opinion-cluster
  hop). It was re-fetching dockets whose upstream records are stubs — every
  flagged case landed in an unresolvable reconcile issue. Its budget slice
  returns to the refresh rotation. The per-Term historical set it was meant to
  grow now comes through the live channel instead (the `historical-terms`
  walker).
- **The bulk-CSV seed path is deleted** (git history keeps it; a future
  bulk-shaped source — the replica, or CourtListener logical replication —
  re-enters through the shared normalizer, `ingest.from_bulk_row`). Historical
  loading is the **historical Term walker** (`fedcourts historical-terms`,
  `run-pull`'s daily `historical` job): it walks October Terms' docket serials
  newest-first over the supremecourt.gov docket JSON — the same client,
  identity, and ingest seams as the forward poller — and lands the sampled
  decided set (every decided petition, with denials systematically sampled; the
  committed `historical:` section of `config/tracking.yaml` is the sampling frame),
  primarily for the statpack's per-Term base rates, secondarily the cert
  back-test set. See [live-sources.md](live-sources.md).
- **Pull is re-aimed as targeted enrichment.** The live channel owns SCOTUS
  freshness; pull's REST budget goes to keeping the SCOTUS-touched set's
  CourtListener records current — most importantly the originating CoA dockets
  the `predict_eligible` latch flags — rather than rotating the whole active
  set stalest-first as the primary freshness mechanism.
- **`discover_new_filings` is off as of the live channel's adoption** (the
  decision recorded at the pivot): the live channel's frontier
  probing onboards newly filed SCOTUS petitions — fresher and budget-free —
  and circuit discovery onboarded cases the SCOTUS-touch gate won't predict
  for years. Its budget slice returned to the enrichment rotation.
- **`run-reconcile` is paused** (workflow disabled) while the refactor decides
  its fate: with stub upstream records every reconcile agent run failed, and
  the live channel's proceedings-text resolution makes most resolutions
  deterministic.

Adoption also needs a terms review of the replication agreement itself; the
access-gated, no-republication stance in [data-sources.md](data-sources.md)
already matches the shape such an agreement requires.

The replica serves the *historical* roles (loading breadth, refresh depth). The
**live frontier** — discovering genuinely pending cases and provisioning case
content for forward prediction — is a separate track with its own source and
design: see [live-sources.md](live-sources.md). It follows the same guardrails
(a third channel through the shared normalizer, the corpus as system of
record) and is independent of both the REST budget and the replica timeline.

## Three writer jobs, one shared core

`run-pull` carries three writer jobs on one surface because they differ on every
axis that matters — source, charter, budget ownership, and cadence — while the
cron minute keeps at most one running per scheduled window:

| Axis      | historical (Term walker)                | pull (enrichment)                 | live (forward poll)             |
|-----------|-----------------------------------------|-----------------------------------|---------------------------------|
| Source    | supremecourt.gov JSON                   | REST API                          | supremecourt.gov JSON           |
| Charter   | decided history, newest Term first      | keep CourtListener records current | pending petitions: discovery, watchlist, outcomes |
| Budget    | ~0 API (politeness caps)                | owns the CourtListener budget     | ~0 API (politeness caps)        |
| Cadence   | **daily** (1×, off-peak)                | **daily** (4 windows)             | **daily** (4 windows)           |
| Handoffs  | none — lands already-resolved history   | predict/evaluate issues           | predict/evaluate issues         |

They share an **ingestion core** (`fedcourtsai.pipeline.ingest`: a normalization
layer where a CourtListener API docket, a bulk-shaped row, and a supremecourt.gov
docket JSON all become the same normalized
row, then upsert into the packed corpus in `fedcourtsai.corpus`), shared
dedup/cursor utilities, and shared PR plumbing. **Unify the
library and the data, not the job.** Every job writes the same corpus, in the same
format, through the same APIs; keeping the jobs separate only keeps the budget
boundary crisp (the pull job owns the token; the other two never touch it) and
operational status legible.

```
                shared core (pipeline ingest + store + serialize)
   API docket JSON      ─┐
   bulk-shaped row       ┼─►  one normalized corpus row
   live docket JSON     ─┘
   ┌─────────────────────────────┐
   │ PULL — historical job (1×/d)│ supremecourt.gov (budget-free) ─► decided
   │  Term walker                │ petitions newest-Term-first; per-Term cursors
   ├─────────────────────────────┤
   │ PULL — pull job (4×/day)    │ REST API (per-tier governor) ─► enrichment: fresh
   │  refresh + outcome          │ facts + snapshots; outcome.json + handoffs (ledger)
   ├─────────────────────────────┤
   │ PULL — live job (4×/day)    │ supremecourt.gov (budget-free) ─► discovery,
   │  watchlist + documents      │ watchlist, outcomes, filed-document text
   └─────────────────────────────┘
```

## Storage: one corpus, one ledger

Raw facts and derived judgments have different shapes and lifetimes, so they live
in different stores — but the split is by **kind**, not by phase. Every writer
job writes the *same* corpus through the *same* ingestion core:

1. **Raw facts → the corpus.** Dockets, snapshots, judges, case metadata and
   tracking state, and event definitions go into a **packed, queryable store** —
   a single **SQLite** database, `corpus/corpus.db` — versioned with **DVC** (the
   blob in the DVC remote, the `corpus.db.dvc` pointer in git). One
   format, written identically whether a row comes from the REST API, the live
   poll, or the historical walk, through the shared ingestion seam in
   `fedcourtsai.corpus`. DVC
   also versions pipeline **metrics** (`metrics/`, registered in `dvc.yaml`):
   back-test results and leaderboards.
2. **Derived judgments → git.** Outcomes, predictions, evaluations, and their
   reasoning are tiny, critical, and worth reading in a diff, so they stay in
   plain git under `data/`, where the schema/`validate`/PR-review machinery
   applies. See [data-model.md](data-model.md).

The rule is **pack, don't proliferate**: millions of per-case files would choke
`git` even under LFS (one tree entry per pointer), so all facts — historical and
fresh alike — go into a handful of large artifacts in one shared format. Keeping
every channel of the pipeline on the same structures, schema, and APIs is the
point: the channels differ on *source* and *budget*, not on how a fact is shaped
or stored. The reasoning stays readable text in git because that diff is the
explainability trail a reviewer actually reads.

### Credentials for the DVC remote

The DVC remote is a **private S3 bucket** the maintainer provisions out of band.
Workflows authenticate with **GitHub OIDC**, not static keys: each job that
touches the remote runs `aws-actions/configure-aws-credentials` (pinned to a
commit SHA) to assume an IAM role, reading the role ARN and region from the
`runner` environment. The committed `.dvc/config` holds **no credentials and no
bucket URL** — it only names the default remote (`storage`); the URL is supplied
out of band into the gitignored `.dvc/config.local` (`dvc remote add --local -d
storage …`) before any push/pull. See [SECURITY.md](../SECURITY.md).

Access mirrors each workflow's role in the pipeline:

| Workflow                                  | Role / access | Why                              |
|-------------------------------------------|---------------|----------------------------------|
| `run-pull` (all three jobs)               | read-write    | corpus writers (`dvc push`)      |
| `run-predict`, `run-evaluate`, `run-reconcile` — plan jobs | read-only | scope gating over the whole corpus (full `dvc pull`) |
| `run-predict`, `run-evaluate`, `run-reconcile` — cell jobs | read-only | point lookups + retrieval, blob queried in place (ranged reads, no pull) |
| `run-analytics`, `run-cleanup`            | read-only     | scan-heavy analysis / metrics refresh / cleanup (full `dvc pull`) |
| `ci`                                      | none          | gate stays offline/fast          |

The split is deliberate: a cell touches KBs of one case's data, so it reads the
immutable blob in place via the ranged backend and moves no full blob; the plan
jobs, `run-analytics`, and `run-cleanup` scan the corpus and keep the full pull.

The gate has no remote, so it cannot diff the corpus blob against S3; it runs the
offline half instead. `fedcourts dvc-status` checks that the committed DVC
bookkeeping is internally coherent — every DVC-tracked data output (the
`corpus/corpus.db.dvc` pointer, any cached stage output) is a well-formed pointer
that is gitignored and absent from git, so the corpus blob can never slip into the
repo, and every `cache: false` pipeline output (the `metrics/` roll-ups) is
committed. The online `dvc status` against the remote stays with the corpus-writer
workflows that hold the credentials.

**Two IAM roles, split by access.** Corpus writers (`AWS_ROLE_TO_ASSUME`) assume a
**read-write** role; retrieval consumers (`AWS_ROLE_TO_ASSUME_READONLY`) assume a
**read-only** role, so a compromised predict/evaluate/reconcile runner cannot write
or poison the corpus. The write role is **append-only** — get/put/list but **no
delete** — and the bucket has **versioning** on, so no run can wipe corpus objects
(no run garbage-collects the *remote* — the historical job prunes only its local
runner cache with `dvc gc --workspace`, never `--cloud`; remote pushes only ever
add).
Both roles' OIDC trust is scoped to this repo's `runner` environment, so only
`runner`-environment jobs — never an arbitrary PR-branch job — can assume them. The
OIDC wiring (`permissions: id-token: write` + the credentials step) grants each job
its access without any long-lived key.

### Corpus-writer coordination

`corpus/corpus.db` is one mutable SQLite blob behind one DVC pointer
(`corpus/corpus.db.dvc`), and three writer jobs mutate it — `run-pull`'s
enrichment, live-poll, and historical jobs. A blob has no merge, so
the pointer is last-writer-wins: if two ran concurrently, or built on
divergent bases, the second commit would silently drop the other's rows. Two rules
prevent that:

- **One lock.** The writer jobs share the `corpus-write` concurrency group
  (`cancel-in-progress: false`), so corpus writers never run simultaneously — a
  second run queues until the first finishes.
- **All commit straight to the default branch.** Each run does `dvc pull → mutate
  → dvc add → dvc push → commit the pointer (+ outcomes)` and pushes
  directly. Serialized by the lock, every run pulls the latest committed pointer
  before mutating, so it always builds on its predecessor's writes. No writer
  goes through a long-lived PR whose stale base could revert the others on merge.
  If the default branch advanced for an unrelated reason between checkout and push
  (e.g. a `run:predict` / `run:evaluate` PR merged), the commit is rebased onto the
  new tip and the push retried — the lock means the pointer itself never conflicts,
  so this is a clean fast-forward, not a corpus merge.

### The corpus file's physical layout

The blob's physical layout is a contract with **ranged remote reads** — read-only
SQLite querying the immutable, content-addressed blob in place on the remote via
HTTP range requests, instead of transferring it whole. Two properties govern that
access pattern, and the corpus writers guarantee both: **64 KB pages** (SQLite's
maximum page size, so a B-tree descent costs a handful of round trips instead of
dozens) and a **non-WAL journal mode at rest** (a WAL reader needs the `-wal`
sidecar, which never ships with the blob). `corpus.connect` creates every database
with this layout; each writer command rebuilds a drifted file (`VACUUM` at the
target page size) before its workflow's `dvc add`, under the `corpus-write` lock
the job already holds; and `fedcourts dvc-status` fails on a drifted local file,
so the invariant is enforced rather than remembered. The read paths behind
retrieval and provisioning are index-served (pinned by `EXPLAIN QUERY PLAN`
tests), which keeps a ranged point lookup at KB scale rather than a table scan.

### The ranged read backend

`fedcourtsai.corpus_ranged` implements those ranged reads in-repo: a read-only
SQLite VFS (apsw) that serves page reads from block-aligned S3 ranged `GET`s.
The immutability argument is what makes this sound with **no consistency
machinery**: the blob is content-addressed, so the committed pointer names one
exact byte sequence — a corpus update publishes a *new* object, and a reader
can never observe a torn write. Mechanics:

- **Blocks and cache.** `xRead` is served from fixed 256 KB block fetches
  through a per-connection in-process LRU (64 blocks), so a B-tree descent
  costs a handful of `GET`s and repeated lookups cost none. The file size comes
  from the DVC pointer — the object is never `HEAD`ed.
- **Selection.** Read-only consumers go through `corpus.connect_readonly`,
  which picks the backend from the corpus-backend setting (or an explicit
  override): `local` opens the `dvc pull`-ed file, `ranged` resolves the
  committed pointer against the out-of-band remote URL. The read-side CLI
  commands (`query`, `open-events`, `provision-snapshot`, `corpus-info`) take
  `--corpus-backend`. Writers never use this seam.
- **Stats.** Each ranged connection counts its `GET`s and bytes fetched;
  the CLI reports them to stderr — the per-query egress evidence retrieval
  logging and the integration check consume.
- **Seams.** The transport is one callable `(key, byte range) -> bytes`
  (boto3-against-S3 today; an S3-compatible endpoint elsewhere is a contained
  swap, and offline tests substitute an in-memory stand-in). The pointer→key
  resolver is the only code that knows DVC's remote cache layout and fails
  loudly if that coupling breaks.

Credit: michalc/sqlite-s3-query and litements/s3sqlite (both MIT) are the
reference implementations; this is implemented in-repo so it is typed, tested,
and reviewed under the same gate as everything else.

### Developer access (Codespaces)

Interactive data discovery — corpus anomalies, field distributions, one-off
lookups — belongs in a codespace, not a workflow. The remote serves it in two
modes, both strictly **read-only** (see [SECURITY.md](../SECURITY.md)):

- **Ranged queries** for quick lookups: `uv run fedcourts query
  --corpus-backend ranged ...` (likewise `open-events`, `provision-snapshot`,
  `corpus-info`) reads the blob in place on the remote — per-query egress in
  KBs, no transfer, nothing to keep fresh.
- **A deliberate full pull** for scan-heavy exploration:
  `uv run dvc pull corpus/corpus.db.dvc` materializes `corpus/corpus.db`
  locally, where full table scans and ad-hoc analysis run at local-SQLite
  speed.

Default to ranged, and pull only when a session is genuinely scan-heavy:
Codespaces runs on Azure, so every full pull is cross-cloud S3 internet
egress. That is why the pull is a documented one-liner and never part of
container creation.

Credentials arrive as **user-scoped** Codespaces secrets — never repo-level,
never committed — through one of two flows with the same read-only blast
radius. The **maintainer** authenticates via IAM Identity Center: the
devcontainer's post-create hook (`.devcontainer/setup-corpus-access.sh`)
writes `~/.aws/config` profiles whose short-lived SSO session
(`fedcourts-sso`) assumes the read-only corpus role
(`fedcourts-ro`, made the shell's default profile) —
rerun `aaws sso login --sso-session modelmirror --use-device-code`
when the session expires. **Contributors** use a dedicated read-only IAM user's
key pair (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`), which boto3 reads
straight from the environment — nothing to configure. The IAM user is
provisioned on demand (see [SECURITY.md](../SECURITY.md)); ask via an issue
if you need corpus access. In either flow, when
the remote's URL secret (`DVC_REMOTE_URL`) is present the hook writes the
gitignored `.dvc/config.local` exactly as the workflows do, and the
application reads the URL for the ranged backend from the same bare variable
(`fedcourtsai.config` accepts it as an alias of the `FEDCOURTS_`-prefixed
name) — ranged queries work with no further setup and no pull. Absent
secrets, the hook prints a note and succeeds — the offline fixture loop and
the full gate need no remote.

### Corpus schema

Each corpus row is a normalized, **labeled** record so it serves both consumers:

```
case_id, court, docket_number, case_name (caption), date_filed, date_decided,
disposition (outcome label), judges[], topic (nature/subject),
citations[], opinion_text, summary
# embedding[] — later upgrade for semantic retrieval
```

Carrying `disposition` makes the corpus a ready-made **back-testing** set, and
the structured columns make it **queryable** for retrieval. The schema is
defined and enforced in [`fedcourtsai.corpus`](../src/fedcourtsai/corpus.py)
(`CorpusRow` + the `cases` table); see [corpus/README.md](../corpus/README.md)
for the column reference. The SQLite format is internal — the stable contract
is the row schema, whose ids and `Disposition` vocabulary are shared with the
ledger models in `fedcourtsai.schemas`.

### Consumers of the historical corpus

- **Back-testing** — replay predictors against historical *resolved* events
  (outcome hidden at predict time), score against the known disposition. Run by
  `fedcourts backtest` (the `backtest` DVC stage), a deterministic offline replay
  that writes `metrics/backtest.json`; see [`fedcourtsai.backtest`](../src/fedcourtsai/backtest.py).
- **Base-rate aggregation** — roll the corpus into disposition base-rates instead of
  individual priors. On demand as `fedcourts stats` (overall, filtered to one SCOTUS
  Term with `--term`, or grouped by court / originating circuit /
  topic / judge / SCOTUS Term); as the published **statpack** (`fedcourts statpack`,
  the `statpack` DVC stage → `metrics/statpack.{json,md}`, kept fresh by
  `run-analytics`'s weekly metrics-refresh job — see [pipeline.md](pipeline.md));
  and behind `run-analytics`'s dispatch modes. See
  [`fedcourtsai.analytics`](../src/fedcourtsai/analytics.py).
- **Retrieval** — at prediction time a model pulls a handful of *relevant*
  priors instead of loading the bulk set into context. Structured retrieval is
  implemented today as `fedcourts query` (and the `corpus.retrieve_priors`
  library API): exact-match filters on court / topic / disposition plus
  overlap filters on judges and citations, ranked by how much each prior shares
  and defaulting to resolved (labeled) cases. Procedural **posture** is not a
  case-level column — it is carried by a case's predictable-event `kind` — so it
  is not yet a query filter; semantic / embedding similarity lands on the same
  query seam once embeddings are stored.

The back-test harness scores each predictor on disposition accuracy, binary
granted accuracy, and the Brier score of P(granted). It runs over a
`Backtester` seam: two reference baselines (a constant floor and a
corpus-retrieval majority vote) run entirely offline so the metric is real
today, and the configured agentic predictors plug into the same seam and are
replayed out of band, exactly as `run-predict` runs them live.

How much a back-test score is allowed to mean is fixed by the pre-registration
stratification (see [`fedcourtsai.leaderboard`](../src/fedcourtsai/leaderboard.py)):
**forward predictions are the test set; the back-test is the validation set.**
A replay can never be a true test — no redaction removes a model's parametric
memory of a famous case, and screening many prompt or retrieval variants
against the same resolved history makes the winner's score optimistic in the
usual multiple-comparisons way. So back-test deltas drive the intermediate
feedback loop — retrieval quality, calibration shape, prompt scaffolding, lift
over the always-deny floor — while predictor *skill* is only ever claimed from
forward cells. The schemas enforce the line: both back-test reports carry a
hard-coded `retrospective` stratum, and the leaderboard never blends the
strata.

The live predict/evaluate cells have the same shape of seam. A cell hands its
inputs — court, docket, event, the acting predictor/evaluator id, the run id,
the role, the prompt, and the output root — to a `Runner`
(`fedcourtsai.pipeline.runner`) that writes the cell's artifacts at the canonical
`ids`/`paths` locations. The workflow's runner is the coding agent
(`claude-code-action` / the Codex equivalent); an offline `stub` backend writes
deterministic, schema-valid canned artifacts with no model call and no network,
so the cell mechanics — provisioning paths, schema conformance, the
`validate`/consume path — are exercised in pytest without spending tokens or
running Actions. Wiring the live workflow onto the seam is separate; the stub is
the offline reference, mirroring the `Backtester` baselines above.

Those offline reference *engines* still read a corpus, which on a laptop would
need a `dvc pull` of the S3 remote behind OIDC. `fedcourts make-fixture-corpus`
removes that dependency: it builds a tiny, deterministic **synthetic** corpus
([`fedcourtsai.fixture`](../src/fedcourtsai/fixture.py)) — a handful of cases
across several courts, a mix of resolved and open, with their predictable events
and dated snapshots — so the read commands (`provision-snapshot`, `query`,
`open-events`) and the pytest suite run with no remote, token, or network. It is
the offline reference *data* under the engines above; it is never a substitute
for the real corpus the run-pull writer jobs produce.

## Historical — the Term walker

- **Trigger:** `run-pull`'s daily `historical` cron window (or dispatch
  mode=historical). No trigger label: nothing an outside actor can file fires
  it.
- **Each run** (deterministic, no agent, no API secret): loop
  `fedcourts historical-terms` in checkpointed chunks — walk the configured
  October Terms' docket serials newest-first over the supremecourt.gov docket
  JSON, resuming from the persisted per-(Term, stream) cursors in the corpus →
  ingest each sampled decided petition through the shared live path (identity
  reconciled, snapshot stored, resolved row + `outcome.json` recorded, events
  latched closed, OT2021+ documents provisioned) → `dvc push` the corpus and
  commit the pointer directly to the default branch after every chunk (under
  the shared `corpus-write` lock — see Corpus-writer coordination) → comment
  cumulative progress on the day's open `pull-log` issue.
- **Sampling frame:** every decided petition is ingested except denials, which
  are kept when their serial is a multiple of `historical.denial_sample_every`
  — deterministic per serial, so resumed runs keep the identical sample; the
  committed `historical:` section of `config/tracking.yaml` documents the
  set's construction. Undecided petitions are skipped entirely (pending
  matters are the forward poller's charter), so the walker writes **no**
  predict/evaluate handoffs, ever.
- **Resumability:** the cursors advance over every served serial (a 404 never
  advances them), so a capped or crashed run resumes gap-free and the frontier
  is re-confirmed cheaply; see [live-sources.md](live-sources.md) for the walk
  design.
- **Scope maintenance:** after the loop, the job runs `fedcourts
  reconcile-scope --apply` — the predict-scope latch sweep rides the daily
  historical window because the corpus is already pulled and pushed there.

## Pull — forward freshness

- **Trigger:** an intraday cron that fires several windows a day (staggered from
  other jobs), `workflow_dispatch`, or a maintainer-applied `run:pull` label for an
  on-demand refresh (which re-runs the full `pull-all`, not a single case).
  Recording a decided event's outcome is split off to `run:reconcile` (see *Detect
  resolution* below), so it is **no longer** the deterministic pull's job.
- **Per-window tracking:** the day's windows share one short-lived `pull-log`
  issue — the first window opens it, each posts a summary (handoffs opened, whether
  snapshots were committed), and the final daily window closes it on success — left
  open as a record if a window fails. The `pull-log` label is deliberately not a
  `run:*` trigger label, so the tracking issue never re-fires pull.
- **Budget governor:** a per-run cap (`max_cases_per_run` dockets ≈ ~3 requests
  each) with **oldest-`last_pulled`-first rotation** and **skip closed/resolved**
  cases, sized so each window stays under the active CourtListener tier's hourly
  ceiling and the day's windows under its daily one. A slice of each run
  (`eligible_refresh_reserve`) is reserved for the stalest **predict-eligible**
  cases, so the SCOTUS-touched pilot set rotates ahead of the much larger active
  set and new docket activity is caught before a case resolves. As the active set
  grows past one run's capacity, each case is simply
  refreshed every few days. The rotation key `last_pulled` is **per-case tracking
  state in the corpus** — raw facts, tracking state included, live in the corpus,
  not git — so the governor adds and maintains that column.
- **Two forward jobs over the shared core:**
  1. **Refresh** active known cases (`pull_case`), ingesting fresh facts into the
     corpus through the shared core and queuing `run:predict` for changed cases
     with open events. This is targeted CourtListener *enrichment* — most
     importantly the originating CoA dockets the `predict_eligible` latch flags;
     the supremecourt.gov live channel owns SCOTUS freshness.
  2. **Detect resolution** of tracked open events → write `outcome.json` to the
     git ledger deterministically when the disposition is machine-readable (a
     concrete disposition, a decision date, and a single open event), and queue
     `run:evaluate` for it **when the ledger holds a prediction to score**
     (ground-truth recording is ungated; the evaluator fan-out is — a
     never-predicted resolution has nothing to evaluate, and the evaluate plan
     re-checks the same gate before minting cells). Anything ambiguous is **not** guessed: it lands on
     the reconcile queue. The `run-reconcile` agent workflow that used to
     consume that queue is **operationally paused** while the live channel —
     whose proceedings text makes most resolutions deterministic — settles
     reconcile's fate; the live job surfaces ambiguous resolutions on its daily
     log instead of filing issues.
- **CourtListener discovery is off** (`pull.discover_new_filings: false`):
  the live channel's frontier probing onboards
  newly filed SCOTUS petitions, and circuit discovery onboarded cases the
  SCOTUS-touch gate would not predict for years. The watermark machinery below
  remains implemented but dormant, and reactivates by flipping the flag.

## Event definition — deterministic, corpus-driven

Defining the **predictable events** of a docket is its own stage, decoupled from
ingestion (`fedcourtsai.pipeline.events`), so it runs once over an ingested docket
regardless of which channel the case entered by. Every entry
path calls the **same** `extract_events`, differing only in a normalization seam
(`from_bulk_row` for bulk-shaped rows, `from_api_docket` for REST objects),
so every docket yields identical event rows for the same input.
It is classification, not analysis: every event is pinned to a single docket entry
with a closed `kind` enum (`motion` / `petition` / `appeal` / `order`), so the
stage maps qualifying docket entries → event definitions (`kind`,
`docket_entry_id`, `opened_at`, `description`) and writes them as corpus rows.

- **Baseline.** Every docket carries the one thing always worth predicting — the
  disposition of the appeal, or the petition at SCOTUS — even when no entries are
  machine-readable.
- **Baseline-only when there are no entries.** Entry-pinned events
  (`motion` / `petition` / `order`) are produced only where the source actually
  carries the docket entries. A bulk-shaped row often does not, so such a docket
  gets its baseline event alone; a later forward `pull` refresh, which fetches
  the full entries, enriches the case with the finer-grained events. The baseline
  always stands so no docket is left with nothing to predict.
- **Predictable / unresolved** = the request entry has no *later disposing order
  referencing it* (citing its docket-entry number). When a disposing order does
  reference it, the event is recorded `resolved`; with no citation the stage does
  not guess, so the event stays predictable.
- **Deterministic first, agent only if ambiguous.** An entry that reads like a
  request but matches more than one `kind` is surfaced for triage rather than
  classified — the same deterministic-first / agent-fallback split resolution
  detection uses (see the reconcile pause note above). The default path runs no
  agent.

## Discovery frontier

> **Dormant.** CourtListener forward discovery is off
> (`pull.discover_new_filings: false`) — the live channel onboards SCOTUS
> filings. The mechanics below stay correct and reactivate with the flag; they
> also document the watermark semantics the live channel's per-Term cursors
> mirror.

Forward discovery searches each court from a per-court **discovery watermark** held
in the corpus (tracking state, never git `data/`). For the frontier to stay
gap-free, two rules hold:

- **The watermark only moves forward.** A write older than the stored value is
  ignored, so a later forward watermark always wins, and a re-run never rewinds it.
- **A no-results run still advances it.** A discovery pass that finds no new dockets
  records the date it searched from, so the next run resumes there instead of
  resetting to the start default. (It advances only to a date already searched, so
  it can never skip a real filing.) Without this a court that keeps finding nothing
  would restart from "today" every run — a steady-state hole, not a one-time miss.

A court should normally have `--since` passed to `discover` before its first
forward discovery, so its frontier is meaningful. The `today`
default is only a last resort for a court with no watermark; on its own it
discovers nothing useful.

## Steady state

History sits in the DVC corpus (the bulk-era load plus the historical Term
set the historical Term walker keeps growing). **SCOTUS freshness is the live
channel's**: the run-pull `live` job polls supremecourt.gov four times a day —
frontier probing onboards new petitions within a cycle, the watchlist refresh
catches distributions and resolutions within days of the conference. Pull's
four CourtListener windows spend the API budget on enrichment of the
SCOTUS-touched set. The result is that the *prediction-relevant* slice — every
pending petition and its originating docket — is complete to within one live
cycle, while circuit breadth advances only as enrichment reaches it.

## Data validation

Two stores that must agree — the DVC corpus (raw facts) and the git ledger
(derived judgments) — plus an append-only corpus and a schema that is law give the
data a set of **invariants** worth asserting on their own, distinct from
`run-ops`'s run-health analytics. Run-health asks *did the runs succeed*;
validation asks *is the data correct and internally consistent*. The two meet at
**completeness**: validation produces a correctness verdict, the ops dashboard
([pipeline.md](pipeline.md)) presents it — separate tools, clean handoff.

The invariants fall in three layers:

- **Schema conformance** — every git-ledger artifact under `data/` validates
  against its model. `fedcourts validate` already enforces this in the local gate
  and PR CI; scheduling it on `run-ops` as well catches anything that reached the
  default branch without the gate, plus model/data bit-rot over time.
- **Corpus integrity** — the committed `corpus/corpus.db.dvc` pointer resolves
  against the remote, the corpus opens, its row count only ever **grows** (the
  append-only write role and bucket versioning make a drop a red flag), required
  columns are non-null, no point-in-time snapshot is future-dated and every case's
  filing/decision dates are ordered and not future-dated, coded columns hold values
  from their declared vocabulary (the `Disposition` and `EventKind` enums, the
  tracked-court set), and no case, event, snapshot, or whitespace-variant id is
  duplicated.
- **Referential integrity** — every `outcome.json` / `prediction.json` /
  `evaluation.json` references an event and case that exist in the corpus (no
  orphan judgments), and every evaluation targets a real prediction.

The corpus-dependent layers land as a `fedcourts validate-corpus` command (sibling
to `validate`) that emits a **JSON verdict** — pass/fail plus per-check counts,
shaped like the other reports. Because `run-ops` is a corpus-free presenter
(see [pipeline.md](pipeline.md)), the verdict
is **produced where the corpus is already pulled**: the corpus-writer path
(`run-pull`'s pull and historical jobs) runs the check as a
non-blocking trailing step and publishes the verdict — alongside the
live-frontier readiness snapshot (`fedcourts live-frontier`), which rides the
same publish — and `run-ops` then renders a
**data-health** section from the verdict (and the substance section's watchlist
view from the snapshot) and, on failure, opens or updates a single
long-lived issue — loud, but never blocking the pipeline. The git-only referential
checks fold into `fedcourts validate` so they also run at PR time: a judgment whose
event has no `event.yaml` in the git tree, or whose declared ids disagree with its
path, is caught in review rather than a day later. Because forward discovery keeps
event definitions in the corpus, the predict/evaluate/reconcile workflows
materialize each event's `event.yaml` from the corpus into its ledger directory
(`fedcourts materialize-event`, beside the snapshot provisioning) so the judgment
PR carries it — and the deterministic outcome writer (`record_outcomes`, the
pull/live path that commits straight to main) materializes it beside every
`outcome.json` it writes, refusing to write an outcome whose event the corpus
does not hold. The corpus checks need the
remote, so they stay on the schedule (the gate is deliberately offline) — at PR time
"the event exists" means it is defined in the git ledger; the schedule additionally
confirms it against the corpus. This automates, and extends across stores, the
manual corpus spot-check that backed the early backfill.
