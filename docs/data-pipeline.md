# Data pipeline: ingestion & freshness

The design contract for the ingestion channels — the **pull** (CourtListener
enrichment), **live** (forward SCOTUS poll), **historical** (Term walker), and
**enrich** (opinion clusters) jobs — and for the stores they write. For the
label/workflow mechanics see
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

## Five writer jobs, one shared core

Three workflows carry five writer jobs over one corpus — `run-pull`'s **pull**,
**live**, and dispatch-only **enrich**, `run-seed`'s **historical** walker, and
`run-repair`'s dispatch-only **repair** bench —
differing on every axis that matters, while the shared `corpus-write` lock keeps
at most one running at a time. Five is the count of jobs that write the
*corpus*; run-repair carries a sixth writer job, the ledger-only **regrade**,
which takes the same lock and commits to `main` without touching a corpus row
(*[Corpus-writer coordination](#corpus-writer-coordination)*). These jobs are the **only** place *production*
corpus writes can happen: the write role is job-scoped and the pointer commit
rides the data App, neither of which any interactive session holds — so a
maintenance pass
that mutates the corpus (a backfill, a relabel, an overhang clear) is always a
step or dispatch input on one of these workflows. Its home is
`run-repair` whenever its dry-run is a triage list a maintainer must read before
an apply, which is what *[Maintenance passes](#maintenance-passes)* below
describes; a pass a scheduled window can converge toward on its own is a
standing sweep on the walker instead.

| Axis      | historical (Term walker, run-seed)      | pull (enrichment, run-pull)       | live (forward poll, run-pull)   | enrich (opinions, run-pull) | repair (maintenance bench, run-repair) |
|-----------|-----------------------------------------|-----------------------------------|---------------------------------|-----------------------------|----------------------------------------|
| Source    | supremecourt.gov JSON                   | REST API                          | supremecourt.gov JSON           | REST API (opinion clusters) | the stored corpus itself, and for the OCR recovery alone the filings it names (supremecourt.gov PDFs) |
| Charter   | decided history, newest Term first      | keep CourtListener records current | pending petitions & applications, granted dockets to judgment: discovery, watchlist, outcomes | granted dockets → published opinion: reporter citations and opinion body | repair what no channel corrects: re-derive, relabel, normalize, remove |
| Budget    | ~0 API (politeness caps)                | owns the CourtListener budget     | ~0 API (politeness caps)        | shares the CourtListener budget, bounded per dispatch | ~0 API; each apply bounded by a blast-radius count, or by a slice where the cost is runner minutes |
| Cadence   | **daily** (4 dead-zone windows)         | **daily** (4 windows)             | **daily** (4 windows)           | **dispatch only** (never scheduled) | **dispatch only** (never scheduled) |
| Handoffs  | none — lands already-resolved history   | predict issues                    | predict issues                  | none — enriches rows already ingested | none |

They share an **ingestion core** (`fedcourtsai.pipeline.ingest`: a
normalization layer where a CourtListener API docket, a bulk-shaped row, and a
supremecourt.gov docket JSON all become the same normalized row, then upsert
through `fedcourtsai.corpus`) plus shared dedup/cursor utilities. **Unify the
library and the data, not the job:** every job writes the same stores through
the same APIs; separate jobs only keep the budget boundary crisp.

One writer sits outside these four without contradicting the claim above: the
dispatch-only `staging-corpus-refresh` workflow holds the **staging** pair's
read-write role (`fedcourts corpus-seed-slice`), which is read-only against
production. It writes a disposable slice, never these stores — which is the
point of it, since that lets the read/write seams be exercised end to end with
nothing gaining production write access.

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
   comes from `FEDCOURTS_CASESTORE_URL`, wired beside the flag as one pair at
   job or step level: the writer lanes (`run-pull`, `run-seed`, `run-repair`), the cell
   workflows, the back-test, the integration scenarios, and the analysis
   surface. `tests/test_workflow_cell_invariants.py` pins both the spelling and
   which workflows carry it, per workflow rather than as a count, so a
   corpus-reading workflow that declares neither half is a deliberate act;
   mirroring is best-effort — a store failure logs, never breaking the SQLite
   write.
2. **Derived judgments → the git ledger** under `data/`, where the
   schema/`validate`/PR-review machinery applies (see *The ledger* below).

The rule is **pack, don't proliferate**: millions of per-case files would choke
`git` even under LFS, so raw facts go to the packed index and the access-gated
store — while the reasoning stays readable text in git, because that diff is
the explainability trail a reviewer actually reads.

### Index retention: keep every version

`corpus-push` never overwrites and never deletes. Each push writes a **new
immutable object** at `index/sha256/<digest>` under the remote's prefix, and
nothing in the system removes one. The control is the explicit `Deny` on every
delete in the read-write role ([security.md](security.md)); the shape of
`fedcourtsai.corpus_remote`'s transport mirrors it, offering upload, download,
and existence checks and no list or delete primitive to call. So the prefix
only grows. The scale: the blob is ~1.1 GB and the writers hold twelve
scheduled windows a day (`run-pull`'s two cron entries, four pull windows and
four live, plus `run-seed`'s four historical ones), with dispatches and label
runs on top and several pushes possible inside one window — in practice the
committed pointer moves a median of **13 times a day**, on the order of 14 GB a
day of new objects. That is a floor on the accretion, not a count of it: a push
whose pointer commit never lands still leaves its object behind.

Those figures are measurements, and they age. The push rates were read off the
pointer's own history on **2026-08-28** (621 revisions since 2026-07-13);
re-measure them from `git log --follow --format=%cI -- corpus/corpus.db.ref` on
`main`, and the blob size from `fedcourts corpus-info` after a pull. The
lifecycle rule below is sized against them, so a figure that has moved is a
reason to re-read that sizing.

The accumulation is deliberate. `corpus/corpus.db.ref` is a git file, so **every
pointer any commit ever carried stays resolvable**: check out a historical
commit, `corpus-pull`, and you get byte-for-byte the index that commit's runs
read, checksum-verified against the `sha256` the pointer itself records. That is
the index half of the reproducibility contract underneath the pre-registration
record — the scannable state any commit's runs read is recoverable whole, while
the bulk payloads a cell was provisioned rest on the content store's own
write-once discipline — and it holds only for as long as no object is ever
collected. Reclaiming the tail would buy storage by making old commits
unresolvable, which is the one thing the corpus is committed against.

Cost is therefore managed by **storage class, not deletion**. A bucket lifecycle
rule transitions objects under the index prefix to **S3 Glacier Instant
Retrieval** 30 days after creation:

```json
{
  "Rules": [
    {
      "ID": "corpus-index-glacier-ir",
      "Status": "Enabled",
      "Filter": { "Prefix": "<prefix>/index/sha256/" },
      "Transitions": [
        { "Days": 30, "StorageClass": "GLACIER_IR" }
      ]
    },
    {
      "ID": "corpus-index-abort-stale-multipart",
      "Status": "Enabled",
      "Filter": { "Prefix": "<prefix>/index/sha256/" },
      "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
    }
  ]
}
```

`<prefix>` is the remote URL's own key prefix, ahead of the `index/sha256/` the
pointer records — substituted from `CORPUS_REMOTE_URL`, which each operator
holds out of band. The rule is the **account owner's** to apply — this
repository holds no infrastructure-as-code for the bucket, the workflow roles
grant enumerated object actions rather than `s3:*`, and the read-write role
denies lifecycle configuration outright, because a rule installed there would
expire objects under S3's own principal and so route around its delete `Deny`
([security.md](security.md)). Apply it by
*adding* the rule to whatever the bucket already carries:
`put-bucket-lifecycle-configuration` replaces the entire configuration, so read
the current one, merge, and put back the union.

**A transition, never an expiration.** A lifecycle rule is age-based, and age
cannot tell it which object the committed pointer currently names — a writer
pause long enough would eventually catch the live blob. That is survivable only
because Glacier Instant Retrieval is instant: first-byte latency in
milliseconds, the same as Standard, with no restore step — nothing in the read
path needs `s3:RestoreObject`, so the read-only role's grant is untouched by
the rule. The difference is price: a per-GB retrieval charge, and dearer GETs
for the ranged readers that issue hundreds of them. So the worst case for a
rule that does catch the current object is a costlier week, not a broken
`corpus-pull`. An expiration, or a class that *does* require a restore (Glacier
Flexible Retrieval, Deep Archive), turns that same scenario into an outage —
and would need a permission no role holds to get out of.
Glacier IR's two billing floors are both free here: the 90-day minimum billable
duration costs nothing where nothing is ever deleted, and the 128 KB minimum
billable object size is irrelevant to a ~1.1 GB blob. The read side of the
contract is the same either way — historical pulls are rare and deliberate, so
paying retrieval for one is the right trade against holding the whole tail hot.

**Why 30 days.** Across the pointer's history the median gap between revisions
is under two hours and the longest is 47 (1.6 h and 47.4 h on the same
2026-08-28 read), so an object is superseded within hours and anything past a
fortnight is noncurrent with near-certainty; a
tighter threshold would already be safe. Thirty is chosen because the
difference is a *constant, not a growth term*: the threshold fixes how much of
the prefix stays in Standard — thirty days of accretion, ~430 GB at 13 pushes a
day of a ~1.1 GB blob — while everything older transitions under either choice. A fixed extra fortnight of
Standard storage is
what buys a month of headroom for an unusual writer pause (an expired
credential, an upstream outage, a deliberate freeze) to be noticed and resolved
before ordinary reads start paying retrieval.

**The index prefix only.** The rule names `index/sha256/` and nothing else; the
per-case content store is deliberately outside it. Its write-once leaves have no
age past which they stop being read on a hot path — a `replay` cell provisions
the dated snapshot of an event that may be a Term old, and `cert-backtest`
replays historical snapshots wholesale — so a retrieval charge there would land
on exactly the scan-heavy consumers. The store also scales with case churn
rather than run count (only *changed* cases upload), so it is not the
accumulation this rule addresses.

**The second rule is hygiene, not tiering.** A ~1.1 GB push goes up as a
managed multipart upload, and the writer role that cannot delete also cannot
abort its own parts, so a push interrupted mid-upload strands them. Orphaned
parts bill as storage and show up in no prefix-filtered view of the bucket, so
only the bucket can clean them: seven days is far past any push that will ever
complete.

**Versioning does not overlap it.** The bucket keeps versioning on and a
lifecycle rule expiring *noncurrent* versions after a recovery window. Neither
touches the other: content-addressed keys mean supersession writes a **new
key**, never a new version of an existing one, so an index object essentially
never becomes noncurrent — the noncurrent rule is there to reclaim an
accidental overwrite. That is precisely why the transition has to be age-based
on current versions.

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
cell's tooling, scanned by `run-ops` into a tooling digest, and read per run by
`collect` for its `used_corpus_query` line alone, which is the self-reported
side of the run PR's prior-availability note — the field asks whether the cell
*used* the CLI, and the note weighs that against what capture saw rather than
reading it as a verdict on the corpus; advisory, never gating.
`retrieval_log.json` is the harness-captured tool-call transcript the
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
`metrics/` artifacts (leaderboard, claim-scores, backtest, statpack, and the
court-facing docket pack) and `data/scope/scope.json`, the published
prediction-scope decision (`predict_eligible` / `predict_excluded` / reason /
`sample_weight`) for the already-public case set. Five of them — leaderboard,
claim-scores, backtest, statpack, and the scope manifest — refresh together in
the analytics workflow's `metrics-refresh` job, on its weekly schedule or on a
dispatch naming that mode. Three of the five are corpus-gated: backtest,
statpack, and the scope manifest run only with a corpus on disk, because
regenerating them without one would replace the real record with an empty pack,
while the leaderboard and the claim-score board read the committed pack and the
ledger and run either way. The docket pack alone is regenerated by hand and
PR'd. The scope manifest and the docket pack read opposite sources, so their
disclosure properties differ. The **scope manifest** (`fedcourts
scope-manifest`) is enumerated from the committed `data/cases` tree alone,
never a corpus scan, so it discloses only the already-public set and cannot
enumerate the wider ingested corpus. The `data/qp-topics/` artifacts are
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
five writer jobs across three workflows mutate it. A blob has no merge, so the
pointer is last-writer-wins: concurrent or divergent-base writers would silently
drop each other's rows. Two rules prevent that: **one lock** — every writer job,
in `run-pull` (pull, live, enrich), `run-seed` (historical) and `run-repair`
(the maintenance bench), shares the
repo-level `corpus-write` concurrency group (`cancel-in-progress: false`), so
corpus writers never run simultaneously even across workflows. run-repair's
ledger-only re-grade job joins the group as a sixth member without touching the
corpus: it commits to `main` on the same push path, so it serializes against the
pointer commits rather than racing them. Its selector-validation job is
deliberately outside the group — it holds no credential and writes nothing, so a
malformed dispatch is refused in seconds instead of queuing behind a walk to be
told about a typo — and **reset to
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
historical walk's per-chunk checkpoint and its sweeps, and every one of
run-repair's passes, by calling the script directly. It rebases onto any advance and retries a *transient* push failure (a
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
opens the pulled file, `ranged` resolves the pointer the read paths honor —
the out-of-band override when set, else the committed one — against
the out-of-band remote URL; writers never use this seam. Each ranged connection
reports its `GET`s and bytes fetched to stderr — the per-query egress evidence
retrieval logging and the integration check consume — and the transport is one
callable `(key, byte range) -> bytes` (boto3-against-S3; offline tests
substitute an in-memory stand-in) — and that callable is the one place remote
flakiness is absorbed: a *transient* fault (a 5xx, a throttle, a dropped
connection) is retried a bounded number of times on a short jittered backoff,
each retry announced on stderr as a `::warning::` naming the key and range so
the flake rate is countable from a run log, while a *permanent* one (a 403
from a role that cannot read the remote, a 404 from a drifted pointer) fails
immediately and loudly rather than being smeared over a retry budget.
Credit: michalc/sqlite-s3-query and
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
parity gate (`tests/test_provision_casestore.py`).

*Which* point in time the record is sourced at is the cell's declared moment,
not the corpus's newest read: where a forward cell names an event that declares
a moment, `provision-snapshot` places it at the day after that event opened,
cutting the snapshot's proceedings and the documents there, and records the
instant as `context.cutoff`. The terminal-refusal gates below run on the latest
payload first, before any cut — a disposition filed after the cutoff is exactly
what a cut would otherwise hide. See [cli.md](cli.md) for the flag, the two
provenances, and the moments the cut does not apply to.

The `casestore` backend has no query surface, so `query` / `stats` / `open-events` / scope reconcile read
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
decided. The age it reads is the **latest** payload's, before any cut, so it
never reads a placed cell's own `snapshot_date`: a `truncated` cell's
`snapshot_date` *is* its cutoff, which dates the moment rather than the pull,
and a cell placed weeks back is not thereby a stale one — how far its frozen
placement sits behind the day it ran is a separate measurement
(`integrity.context_lag_days`, owed beside any figure over placed forward
cells; the rule is the `salience-replay.json` bullet in
[metrics/README.md](../metrics/README.md)). Only then does the **textual scan**
ask whether the snapshot discloses **its own event's** outcome. A forward
prediction on a decided event would be a mislabeled back-test. The question is
keyed on the event
(`--event`), because one docket carries several events' outcomes at once: a
granted cert docket's grant order is a disclosed *cert* outcome and is also
what opens the merits proceeding, so the entry that must refuse a cert cell
is the merits cell's own record. On the merits event the test is therefore a
parsed merits judgment (and, record-side, the latched judgment); on every
other event it is any entry reading terminal, any entry carrying a
machine-readable disposition order, or — on an application docket — a legible
interim disposal. The predict matrix applies the same forecastability
questions one seam earlier (`predict-matrix` drops a listed event the corpus
records resolved, and any listed merits moment whose row fails the selection
predicate's row arms — latched judgment or termination, a grant that no
longer opens a merits proceeding, a stale unparsed grant — wherever the scope
gate consults the corpus at all; under `predict.scope: all` neither does), so
a stale trigger issue sheds its dead events at plan time instead of minting
cells. For the resolved, latched-judgment, and terminated classes this guard
then re-refuses whatever slips through one by one; for the gvr-re-resolved
and stale-grant classes the plan seam is the **only** guard — the forward
record gate does not read those columns — which is why the re-check exists. A refusal
(exit 3) is a legitimate outcome, not an error — and it **short-circuits the
cell**: the workflow withholds the agent token, the retrieval config, the
engine steps, and the event materialization, so a refused forward cell
produces nothing rather than a context-less prediction claiming a mode it
never had. The cell's status records `produced=false` and the collect census
warns per cell. The other non-zero provisioning exit — no snapshot in the
corpus at all — short-circuits the predict cell the same way, as does a
provisioning write that did not land complete (`assert-cell-record`, which
reads the record off disk rather than trusting the exit code): the provisioned
snapshot is every predictor's guaranteed-common input, so a cell that ran
without one would predict from priors and base rates alone while its output
claimed the shared baseline, and nothing downstream could separate the two.
An evaluate cell, whose provisioning carries no forward gate, keeps the
best-effort shape: it runs and records the gap under its prompt's headless
rule.

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
per-query egress in KBs, with `corpus-info --text-coverage` the one exception —
that flag walks the documents of every live-slice case, tens of thousands of
rows, so under the split it is a content-store manifest round trip each plus a
full text body per stored document, and belongs with the scan-heavy work
rather than with the lookups) and **a deliberate full pull** for scan-heavy
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

The **staging pair** (the lean real-slice corpus of
[security.md](security.md)'s staging-corpus runbook) is served by the same
read-only role — the maintainer's role-assumed flow; the contributor IAM
user stays scoped to production — and its URLs arrive as two more user-scoped
secrets, `STAGING_CORPUS_REMOTE_URL` and `STAGING_CASESTORE_URL`: the same
names the `staging` Actions environment carries for the refresh lane,
deliberately, since they hold the same URLs in a different config store.
`scripts/corpus-env` (invoked from the repo root) switches the whole env
contract between the pairs — both accepted spellings of the remote and
casestore URLs plus `FEDCOURTS_CORPUS_SPLIT` and the out-of-band corpus
pointer, together, because the `FEDCOURTS_`-prefixed aliases outrank the bare
names and a hand-rolled export of one spelling half-switches:
`scripts/corpus-env staging <command>` runs one command against staging (the
form that works from any shell, a coding agent's per-call shells included),
while `eval "$(scripts/corpus-env staging)"` flips an interactive shell and
`eval "$(scripts/corpus-env prod)"` flips it back. The pointer travels with
the pair because the staging index pointer is not committed: consumers
resolve the committed `corpus/corpus.db.ref`, whose digest names the
production blob, unless the out-of-band override (`Settings.corpus_pointer`)
names another published blob — and staging's arrives as a third user-scoped
secret, `STAGING_CORPUS_POINTER`, holding the seed run's published pointer
JSON verbatim (re-set it after each re-seed; the apply summary prints it —
the value is a delivery mechanism rather than a sensitive one: a digest and
a size, no URL or credential).
With the secret present the switch reaches **both halves** — casestore-path
reads of a seeded case's snapshots, events, and documents, and index reads: a
ranged `query`, `corpus-info --corpus-backend ranged`, `corpus-pull`. (A
staging `corpus-pull` is deliberate surgery: it overwrites the shared local
`corpus/corpus.db` with the slice, so re-pull production afterwards — prefer
the ranged backend, which touches no local file. The `local` backend never
consults the override at all; it reads whatever blob is on disk.) Absent
the secret, the content-store half still works, and a *ranged* read or
`corpus-pull` fails loudly as a missing key (the production digest against
the staging bucket).
The override passes the committed pointer's exact validation, key↔digest
binding included, so it only ever selects which already-published immutable
blob is read; writers never honor it — `corpus-push` refuses to run while it
is set, and `corpus-seed-slice` likewise refuses under it (that command's
source is pinned by its own `--source-*` options, so a flipped shell cannot
re-base what its rail refuses, nor — under the ranged backend — what it
reads; the `local` backend still reads whatever pulled blob is on disk, per
the surgery note above). The split flag rides along because the slice is payload-free by
construction: without it, payload reads bypass the casestore and find
nothing, silently.

That same silence is a standing trap on the **production** side too: a dev
shell without the split flag and casestore URL set is **casestore-blind** — a
payload living only in the content store (petition text, documents, the
snapshots the blob does not carry) reads as *absent* rather than
erroring, so a figure computed locally over payloads silently undercounts.
One surface says so on its own: `corpus-info --text-coverage` leads with a
`text source:` line naming the blob or the content store, ahead of every count
below it, and its `text frame:` line reports zero cases served where nothing
was readable. Everywhere
else there is no warning either way. Any figure derived from
petition text, documents, or content-store payloads must therefore come from
a writer-lane run or a shell `corpus-env` has pointed at a pair with the
split on — and must say which. Ledger-derived figures (`data/cases`) and
index-column reads are unaffected; they are in git and in the blob.

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
  ranked, defaulting to resolved cases and screening out the non-cert SCOTUS
  letter forms (`--include-applications` returns them).
  Semantic / embedding similarity lands on the same query seam once embeddings
  are stored.

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
- **Re-snapshotting named dockets:** re-opening a Term to refresh a known,
  enumerated set of rows pays for the whole serial range to reach a few of them,
  so run-seed's dispatch also carries `refresh_dockets` (Term-form numbers, one
  per line or space-separated): `fedcourts refresh-dockets --apply` re-serves exactly
  those and re-ingests each through the walk's own path, additive through the
  same latches. It moves **no cursor** — a targeted re-read is not a rewind — so
  it neither disturbs nor is disturbed by a walk of the same Term, and the
  walk's own rules still bound it: an undecided record is reported and skipped,
  and one whose case carries an open predicted event stays with the watchlist.
  Corpus-side on the repair case: the ingest seam records `outcome.json` only
  for an event still open, so a re-serve converges the row and leaves a
  committed ledger label to `converge-disposition-labels`. A number the corpus
  never held is onboarded outright, ledger included.
- **Maintenance sweeps:** after the loop, one window a day also runs seven
  converging sweeps in order — `fedcourts dedupe-live-rows --apply` (merging
  live-minted duplicate rows; a minted moment's committed event directory moves
  onto the survivor with its re-keyed row, so the lane must stage the moved
  `data/` paths in the same pointer commit — an uncommitted ledger half strands
  the directory under an id the corpus no longer carries, and no later pass
  re-detects it), `fedcourts reconcile-scope --apply` (the
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
- **What this lane does *not* carry:** a repair whose dry-run is a triage list
  a maintainer must read before an apply. Those have no scheduled moment to
  converge toward and fail by refusing rather than by not converging, which is
  the opposite of every sweep above, so they live on the `run-repair` bench —
  see *[Maintenance passes](#maintenance-passes)*. The walker's dispatch inputs
  are therefore the walk-configuration family alone: `refresh_terms`,
  `refresh_streams`, `refresh_dockets`.

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
     deterministically when the disposition is machine-readable, and record the
     owed grading on the evaluate backlog **when the ledger holds a prediction
     to score** (ground-truth recording is ungated; the evaluator fan-out is).
     No issue is filed for it — `run-evaluate` derives that backlog itself on
     its own schedule. Anything
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
     opened a merits proceeding, whose judgment is unlatched, whose
     proceeding is not recorded terminated, **and** whose grant is not stale
     (two Terms past with neither column latched reads as a decided docket
     the record never resolved, not a pending case — the shared bound
     `validate`'s stale-grant check reports on), so the granted docket queues
     a merits predict cell the way an application docket queues its interim
     one.
     The terminated arm is what separates the two: a case that ended with no
     disposition (a post-grant Rule 46 dismissal, a dismissal as moot, an
     abatement on the petitioner's death, a grant the Court vacated, a docket
     whose only terminal notation is the mandate) keeps its merits event open,
     because nothing
     resolves an event on a row carrying no judgment — but there is no longer a
     judgment to forecast, so the event stops earning cells and simply sits.

## Maintenance passes

The `run-repair` workflow is the maintainer's repair bench: the corpus and
ledger passes that fix what no channel corrects. It is `workflow_dispatch`
only — no schedule, no `run:*` label — and it joins the same `corpus-write`
lock the walker and the pullers hold, so a pass can never interleave with a
window's corpus push.

**Why it is not a lane on the walker.** The two have opposite failure postures.
A standing sweep is idempotent and non-blocking: it converges toward a state a
window can reach on its own, and a hiccup must retry next window rather than
redden a walk nobody is watching. A maintenance pass runs because a maintainer
read a dry-run ledger and decided; it fails by **refusing** — an apply without
its bound, a malformed cell id, a stamp the command declines — and a refusal is
the answer the dispatch was for. Absorbing one would report work that never
happened. Separating them also keeps the bench's growth off the production
workflow: a pass added here costs the walk neither a dispatch input nor a
`LOOP_BUDGET_SECONDS` conjunct.

**One pass per dispatch, dry-run first.** `repair` is a single choice, so no
two passes can arm each other, which makes the documented procedure structural
rather than a convention. The procedure is two dispatches: `repair_mode: dry-run` tees the
pass's ledger to the run summary and writes nothing, the maintainer reads the
count off it, and a second dispatch applies with that count in `repair_bound`,
for the passes that take one.
An apply run's own in-run dry-run is a receipt, not a reading — nobody reads it
before the write. Two passes skip it, and for the same reason: the distribution
re-derivation, whose plan *is* its write set, and the OCR recovery, whose apply
ledger already states the class it found before writing. In both, the receipt
would be bought with a whole extra full-population read of the content store —
the third, on an OCR apply, which already re-reads the class as its own write
witness. `repair` defaults to `none`, which
is refused outright: the form's initial state cannot start a corpus write.

**The five inputs.**

| Input | Shape | What it carries |
|---|---|---|
| `repair` | choice, default `none` | which pass to run |
| `repair_mode` | choice `dry-run`\|`apply`, default `dry-run` | write or not |
| `repair_bound` | string | the blast-radius bound: a positive integer, the count read off the dry-run ledger |
| `repair_target` | string | the pass's named subject — a parse label, or a cell list |
| `repair_options` | string | space- or comma-separated switches from the selected pass's closed vocabulary |

`repair_bound` and `repair_target` are separate fields because they are
different kinds of thing and no pass takes both: a bound is a count the
validation checks as an integer, a target is a subject with its own grammar.
Offering either to a pass that takes neither is **refused**, not ignored — a
number left over from the previous dispatch is exactly how a bound meant for
one pass silently reaches another. `repair_options` is a closed vocabulary per
pass, and an unrecognized switch is refused loudly rather than dropped: a
silently ignored switch would have the maintainer read a ledger for one
population and apply against another.

**What each pass accepts.**

| `repair` | Command | `repair_bound` → | `repair_target` | `repair_options` |
|---|---|---|---|---|
| `unlatch-overselected` | `unlatch-overselected` | — | — | — |
| `qp-backfill` | `backfill-questions-presented` | — | — | — |
| `rederive-distribution-parse` | `rederive-distribution-counts` | — (fixed in code) | parse label, **required in both modes** | — |
| `normalize-docket-markings` | `normalize-docket-markings` | `--max-rewrites` | — | — |
| `response-backfill` | `backfill-response-fields` | `--max-fills` | — | — |
| `ocr-recovery` | `ocr-recover-petitions` | `--max-cases` (a slice, not a ceiling — the step adds its own `--deadline-seconds`) | — | — |
| `merits-phantom-removal` | `remove-ungranted-merits-events` | `--max-removals` | — | `include-failed-attempts` |
| `disposition-convergence` | `converge-disposition-labels` | `--max-relabels` | — | `include-scored` |
| `sampled-frame-weight-repair` | `repair-sampled-frame-weights` | `--max-repairs` | — | — |
| `regrade-stale` | `stamp-cell --regrade` | — | cell list, **required in both modes** | — |

A bound is required on `apply` wherever the pass takes one, and refused before
the scan runs unless it is a positive integer — blank, zero, negative, decimal
and leading-zero alike. An unbounded apply would convert a widened predicate
into a mass rewrite rather than a loud refusal, and each of these populations is
finite, so a count above the one read means the predicate widened rather than a
dirtier corpus. **The OCR recovery's bound is the one that means something
else**: it is a *slice size*, and the pass takes the first that many candidates
rather than refusing above them. What bounds the others is blast radius, which
is why exceeding the read count is a refusal; what bounds this one is runner
minutes, since each case costs a re-fetch and a page-by-page recognition, so a
backlog is meant to clear across dispatches. The slice is self-advancing — a
recovered petition leaves the class — but only the recovered ones do. Anything
the slice reached and could not recover (a refused URL, a failed fetch, an
unreadable scan, a recognition cut short) stays, and stays at the *head* in
`case_id` order, so the next dispatch retries it first; the ledger names each
apart, because a class whose head is permanently unreadable turns a small bound
into a no-op and nothing else would show it. The bound is therefore the *spend*
cap and not the pass's safety mechanism: what keeps a heavy slice inside the
step's 30-minute cap is the **slice deadline** the step passes
(`--deadline-seconds`, sized in a comment beside the invocation from everything
that must still fit inside that cap once the pass stops taking work — the
witness re-read, the blob push, the pointer commit, and the work a started
candidate can run past the deadline). Before each candidate the pass estimates that candidate's cost
from the page count the stored row already carries and, where what is left will
not hold it, takes no more; a candidate already started is finished rather than
killed. Those it declines are reported **unreached** — untouched, unwritten, and
at the head of the next slice — which is a different fact from a failure and is
named as one, because page counts across the class vary several-fold and no
fixed bound is both safe against the cap and worth dispatching. Its ledger also
carries a denominator, the stored petitions the walk read at all, and the pass
refuses on it: zero candidates out of zero petitions is a blob whose documents
this process cannot read — a split-mode index with no content store configured
serves every case an empty document list — not a converged class, and the two
must not report the same way.
The distribution re-derivation is the exception that proves it:
its bound is fixed in code because the population's delta was measured before
the surface existed, so moving it is a code change with the new basis stated
beside it — which is why that pass *refuses* a `repair_bound` rather than
ignoring one.

The two targets have their own grammars, both checked all-or-nothing before
anything runs. The distribution re-derivation takes a **parse label** —
lowercase, `dist-v2` in shape; whether the label is *registered* is the
command's own refusal, since that registry lives in Python. The re-grade takes a
**cell list**: one `court/docket/event/run_id/actor` per line, whitespace-separated
so spaces work as well as newlines, as in

```
scotus/1119228/evt-petition-certiorari/20260624T103000Z/claude-judge
```

One re-grade per line, so a cell three judges graded is three lines — which
judge's evaluation is rewritten is not a thing to infer. A single malformed line
refuses the whole list (the input is maintainer-typed text entering a shell, and
a half-applied list is harder to reason about than a refused one), and so does
an empty one, in `dry-run` as much as in `apply`. The grammar admits no `.`, so
no field can be a `..` path segment.

Two options carry a decision rather than a flag. `include-scored` widens the
disposition sweep onto events already carrying committed predict/evaluate
output; an `evaluation.json` is stamped with a `correct` bit computed from the
outcome, so relabelling under one moves what a published standing was computed
from while the standing sits still. Setting it takes on a re-grade backlog, so
it demands `repair_bound` in **every** mode, `dry-run` included — a dry run that
widens the ledger is where that decision is actually made. `include-failed-attempts`
widens the phantom removal onto events whose only committed output is
`attempt.json` cell-failure records, deleting those records with the event: a
trade of failure history for a ledger with no dangling phantom paths. It does
**not** inherit the every-mode bound rule, because it takes on no backlog — what
it grows is the removal set, which the apply's own bound already sizes.

**One pass re-weights the frame rather than converging it.**
`sampled-frame-weight-repair` restores the derived sampling weight on grid
denials a certainty-asserting channel min-latched to 1. Where the other passes
move which bucket a row falls in, this one moves the **weights themselves**, so
every weighted denominator that admits IFP rows moves with it — the statpack's
and docket pack's weighted sections, the ops digest's always-deny floor, and one
committed prose figure in [outcome-decomposition.md](outcome-decomposition.md).
Its population, its direction and its expected magnitudes are therefore
pre-registered in [freeze-record.md](freeze-record.md), and the dry-run ledger is
read **against that entry** rather than on its own: the entry licenses
magnitudes, never membership, so a row the command reports as outside the
registered cells is a different population needing its own entry and the pass
leaves it alone. The apply witnesses itself — it re-runs its own selection over
the written corpus and exits non-zero if anything remains — because a direct
`UPDATE` of a column no downstream artifact recomputes moves the blob whether or
not it moved the right rows. Read the ledger, and dispatch the apply with the
count read off it — then finish the job: the weekly metrics refresh regenerates
the statpack, but `metrics/docket.{json,md}` is on demand (`fedcourts docket`)
and the whole-slice IFP-inclusive figure in
[outcome-decomposition.md](outcome-decomposition.md) is hand-written, so a stale
copy of either looks exactly like a current one. No scored number moves, and
that is a property of the population rather than a hope: every scored-segment
cut is gated on a paid serial and these rows are IFP.

**Prerequisites the bench brings along.** Every corpus pass is gated on a
`dedupe-live-rows --apply` prerequisite that runs first and must succeed: any
docket-number spelling that defeats the channels' identity join leaves a twin
pair, and a pass that reads a row's columns must read the merged row rather than
one half of a pair. It runs in `dry-run` dispatches too — the ledger a
maintainer reads has to describe the same deduped population the apply will act
on. `unlatch-overselected`
additionally brings `reconcile-scope --apply`, in both modes and for the same
reason: the overhang clear recomputes each pending cohort's selection, so it
must recompute over an in-scope corpus whether or not it goes on to write.

**So `dry-run` means the selected pass writes nothing — not that the dispatch
writes nothing.** The prerequisites apply either way, and each pushes the blob
and commits a pointer to `main` if it found anything: one such write on a
`dry-run` dispatch, two on an `unlatch-overselected` one. Both are idempotent
convergences the scheduled walker would have made anyway, so a dry run still
moves the corpus no further than a window does; what it never does is the pass
the maintainer is deciding about. Unlike their twins on the walker's schedule, both fail **hard** here: a
failed prerequisite means the dispatched pass cannot be trusted to read the
right rows, and a green run that quietly did nothing is the worst outcome a
repair bench can produce.


**One pass brings a binary.** The OCR recovery renders a page with poppler's
`pdftoppm` and reads it with `tesseract`, neither a Python dependency. They are
installed by a step gated on that selector alone, from the runner image's own
Ubuntu archive — no third-party repository and no added signing key — so the
other dispatches never pay for them and no scheduled lane grows the dependency.
That gating is the same reason the extractor takes its OCR call as an injected
seam rather than importing one. The resolved versions are echoed into the run
summary rather than pinned in the install: an exact apt pin goes stale the week
the runner image rolls, and would fail the pass for a reason that has nothing to
do with the corpus, so what a recovered text was read by is recorded by the run
instead of promised by the workflow. An apply refuses where the binaries are
absent, which is what keeps a failed install from reading as a converged class.
**Least privilege per pass.** The nine corpus passes run in a job holding the
read-write corpus role, the data App token and the content-store env pair.
`regrade-stale` runs in a separate job with none of those: it recomputes graded
fields out of committed artifacts and writes `evaluation.json`, touching no
corpus row, so it holds only the App token that pushes its `data/` commit. Both
jobs commit straight to `main` on the writers' rebase-and-backoff push path.

**Ordering between passes is the maintainer's.** Two pairs matter. The
distribution re-derivation must precede an overhang clear, never follow it in
the same sitting: anything that weighed incumbent-parse counts is stale
afterwards, and while the scope latch self-heals next window, the overhang clear
does not — its write erases the sticky set it recomputed. And a
`disposition-convergence` apply that moved a label under a committed grade owes
a `regrade-stale` dispatch naming the affected judge lines — three per event
rather than one per evaluation. One pass per dispatch makes that follow-through
a second dispatch rather than a silent second step, which is the point: the
backlog a relabel owes is a maintainer's to schedule.

**Dispatching.** Dispatch on `main`, in a dead zone between the scheduled
windows (`run-pull` at `:17` and `:47`, `run-seed` at `:31`). A *queued* repair
run can be silently evicted — GitHub keeps only the latest pending run per
concurrency group, so a scheduled window entering `corpus-write` behind the
dispatch cancels it, and a one-shot dispatch does not pick up where it left off.

```bash
# A bounded pass: dry-run, read the count off the run summary's ledger, then
# apply carrying that count — the number below stands in for what you read.
gh workflow run run-repair.yml --ref main \
  -f repair=normalize-docket-markings -f repair_mode=dry-run
gh workflow run run-repair.yml --ref main \
  -f repair=normalize-docket-markings -f repair_mode=apply -f repair_bound=214

# The OCR recovery's bound is a slice, so the number is how many candidates one
# dispatch may look at rather than the class the dry run printed. It is the
# spend cap only: the step's own slice deadline decides how many of them are
# actually started, so a bound above what a dispatch can fit costs nothing and
# the ledger reports what was attempted and what went unreached. Read the dry
# run's probe lines first: they say what supremecourt.gov served the writer's
# own fetch path.
gh workflow run run-repair.yml --ref main \
  -f repair=ocr-recovery -f repair_mode=dry-run
gh workflow run run-repair.yml --ref main \
  -f repair=ocr-recovery -f repair_mode=apply -f repair_bound=15

# A pass with an option. `include-scored` demands the bound in BOTH modes, so
# the dry run that decides the widening states it too.
gh workflow run run-repair.yml --ref main \
  -f repair=disposition-convergence -f repair_mode=dry-run \
  -f repair_options=include-scored -f repair_bound=31

# A pass with a target. The re-grade takes one cell per line, one per judge.
gh workflow run run-repair.yml --ref main \
  -f repair=regrade-stale -f repair_mode=dry-run \
  -f repair_target='scotus/1119228/evt-petition-certiorari/20260624T103000Z/claude-judge
scotus/1119228/evt-petition-certiorari/20260624T103000Z/codex-judge'

# The distribution re-derivation names its parse and takes no bound. Dispatch
# the INCUMBENT parse first as a control: it must report `changed = 0`.
gh workflow run run-repair.yml --ref main \
  -f repair=rederive-distribution-parse -f repair_mode=dry-run \
  -f repair_target=dist-v1
```

**After a pass that removes rows**, let the run's trailing verdict step finish.
It republishes the corpus-validation verdict, which is also the next run's
monotonic row-count baseline — so a phantom removal whose run died after the
deletion but before that step leaves run-seed's next verdict reading a
deliberate removal as a corpus shrink. Re-dispatch the pass (it is idempotent
and will find nothing to remove) to republish the baseline.

There is no guard job, unlike the walker's: that one exists because a scheduled
walk fails unwatched. Every run here was started by hand a moment earlier by the
person who wants to read its ledger.

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
`run-ops`'s run-health analytics. Four layers:

- **Schema conformance** — every git-ledger artifact under `data/` validates
  against its model (`fedcourts validate`, in the local gate and PR CI, and on
  the schedule to catch anything that bypassed the gate).

  The path that bypasses it is the **deterministic writers**: pull, live,
  enrich, and seed commit to `main` directly, with no PR and therefore no gate.
  So a writer that lands a malformed or orphaned artifact reddens the data
  stage on *every
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
  the cell never wrote fails rather than passing as a valid record). The rule
  runs both ways: the corpus→ledger direction requires every **minted** moment
  in the corpus to carry the `event.yaml` that defines it, so a moment is
  declared in git on the day it became forecastable rather than whenever a
  cell or a resolution next touches it.
- **Record completeness** — a row that should have resolved by now has. A cert
  grant that opens a merits proceeding and is more than two Terms old, carrying
  neither a parsed judgment nor a recorded termination, is a decided docket the
  record never captured rather than a pending case, and every row-keyed merits
  gate reads it as forecastable. Unlike the three layers above this one cannot
  fail on a well-formed corpus alone — it measures the sweeps' coverage — so it
  names the cases whose record needs mending.

The corpus-dependent layers run as `fedcourts validate-corpus`, **produced
where the corpus is already pulled** (a non-blocking trailing step on the
corpus-writer path, publishing the verdict alongside the live-frontier
readiness snapshot); `run-ops` — a corpus-free presenter — renders the
**data-health** section from the verdict and escalates a failure to a single
long-lived issue: loud, never blocking.

Not every count in the verdict is a failure. A check may **pass while counting
failures**, in which case the count is a known condition and rides on the
verdict, the command's `::warning::` lines, and `run-ops`'s _Monitored_ list —
without reddening anything. Two shapes qualify. **Baseline-gated**, where a
tolerated floor is accepted and only an excess fails (`case_dates_ordered`).
**Advisory**, where the defect is real but its remedy is a data pass rather
than a code fix, so failing would hold the verdict red for however long that
takes — and a verdict that stays red is one readers learn to ignore. A stored
docket number still carrying the Court's `*** CAPITAL CASE ***` marking is the
standing example: ingest strips it at the write site, so the population can only
shrink, and the check reports what is left. The defect there is the stored
spelling — every reader that parses a docket number strips the marking, so no
published cut is missing those rows. The shrinking is what licenses the
advisory, so it is enforced rather than assumed: each advisory carries a
**ceiling**, and a count above it is not a backlog but a write path that
stopped stripping — a code defect, and a failure like any other. Reserve the
advisory shape for exactly that — a defect no contributor's PR can clear.
Anything fixable in the code fails.

Because event definitions live in the
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
first-touch shape.

Which events that first-touch schedule governs is the **mint invariant**, and
it splits the event population in two. A stage's **case-level baseline** — the
cert petition's `evt-petition-disposition`, the interim application's
`evt-motion-disposition` — is derived from a docket's mere existence by the
ingest projection, so its corpus row lands at discovery and its ledger half
arrives later, at first touch or at resolution, exactly as above. Every other
declared moment (`pipeline.moments.minted_moment_ids`) is **minted**: it exists
only because a mint seam decided it does, and a mint owes both halves at once,
through `outcome.persist_moment_events` and never a bare corpus upsert. The one
writer that *moves* an existing minted row rather than creating one is the
dedupe merge's re-key onto a surviving twin, and it carries the row's committed
event directory across with it — restamping the case id inside — so the pair
stays whole through the move. So a
baseline row with no ledger file is the ordinary state of the corpus, while a
minted row with no ledger file is a defect.

The defect is not that the moment would go undefined forever — `materialize-event`
would project the corpus row at a cell's first touch just as it does for a
baseline. It is that **git is the pre-registration record**: a minted moment is
a decision that this case became forecastable on this day, so it belongs in the
committed tree at the mint, not at whatever later touch happens to occur — and
a moment that never earns a cell never gets that touch at all, since a refused
cell skips the materialization with it. `validate-corpus`'s corpus→ledger
check (`minted_moments_defined_in_ledger`) draws exactly that line; it needs
the corpus, so it runs on the scheduled verdict rather than in the offline PR
gate that `validate` carries.

An event definition also names its **stage** — the
decision standard that governs it (cert, interim, or merits) — carried from
the corpus row into `event.yaml` at that first materialization, so a cell and
its consumers read the standard from the record rather than inferring it from
the event id (a file older than the stage axis simply records none, which
reads as the null below). The field is nullable and
null means **no stage recorded**: either no Supreme Court standard governs the
event (a circuit appeal), or the writer does not classify one there yet;
consumers treat null as "no rule", never as a guess.
