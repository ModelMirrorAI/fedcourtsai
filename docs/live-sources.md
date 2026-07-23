# Live sources: predicting genuinely pending cases

The design for the **live prediction** track: discovering cases while they are
still pending — minutes-to-hours fresh, not rotation-fresh — and provisioning
predictors with case *content*, not just docket metadata. It complements the
CourtListener channels in [data-pipeline.md](data-pipeline.md): those own the
historical corpus and the budget-governed refresh; this track owns the live
frontier the September cert task predicts on. Only predictions made while an
event is genuinely unresolved land in the **forward** stratum
([metrics/README.md](../metrics/README.md)) — the whole point of this design is
to make that stratum large and honest.

## Why the rotation is not enough

Forward-stratum prediction has two needs the budget-governed pull rotation
cannot meet:

- **Discovery latency.** The rotation discovers new filings within its request
  budget and window cadence — hours to days. A cert petition distributed for
  conference resolves on a known calendar; predicting it requires knowing it
  exists (and that it was distributed) *before* the conference.
- **Input richness.** Cert prediction leans on the questions presented, the
  petition and brief in opposition, and procedural signals (response requested,
  CVSG, distribution). CourtListener's SCOTUS docket records carry little of
  this; the underlying documents none of it.

Neither need is answered by a higher CourtListener tier — a bigger budget buys
faster polling of the same records, not fresher discovery or richer content.

## The SCOTUS live source: supremecourt.gov docket JSON

The Supreme Court's own site serves a structured JSON docket per case:

```
https://www.supremecourt.gov/rss/cases/JSON/<term>-<number>.json
```

Each record carries the full **proceedings list** as dated entries (petition
filed, response requested, briefs, "DISTRIBUTED for Conference of <date>",
disposition orders), **direct PDF links to every filed document** (all filings
are public on the docket since the 2017 e-filing mandate), a **questions
presented** link, the lower court and its docket numbers, parties, and counsel.
This is the authoritative record, fresher than any scrape of it, with **no API
budget** — the constraint that shapes the CourtListener channels simply does
not exist here.

Three access facts shape the client:

- Requests need a browser user-agent (the default programmatic UA is refused).
- There is no push feed and no "list new dockets" endpoint. **Discovery is
  sequential probing**: docket numbers are per-Term sequential (paid petitions
  from `25-1`, IFP from `25-5001`), so a poller probes the next unseen numbers
  and a 404/empty record marks the current frontier.
- Be a polite client: throttle to ~1 request/second, back off on errors, and
  poll on a cadence matched to the docket's rhythm (hourly for the conference
  watchlist, daily for frontier probing) rather than hammering.

These facts — and the channel's Term reach — are empirically verified by the
reachability probe (`fedcourts probe-live-terms`), which holds three standing
conclusions: **the Term floor for full JSON coverage is OT2017** (the e-filing
era — every number, paid and IFP, with a stable schema across served Terms;
document links are reliable only ~OT2021+, a rolling retention window);
**disposition orders ride as plain `ProceedingsandOrder` text readable by the
shared cert-order patterns** (`pipeline/cert_signals.py`), so every sampled
decided petition lands with a machine-readable cert label; and the probe is
**re-run to re-establish that resolver recall claim** after any pattern change
(and to confirm the document-window edge).

## Architecture: a third channel, the same corpus

The live source follows the replica guardrails exactly
([data-pipeline.md](data-pipeline.md), *The planned end-state*): it is a new
**channel**, never a new consumer surface.

- **Ingestion stays channel-agnostic.** The docket JSON maps onto the same
  normalized corpus row in the shared normalization layer (a third
  `CorpusSource`), and the raw JSON — proceedings and document links included —
  is stored as the case's dated **snapshot**, exactly like a REST pull. The
  proceedings list is the docket-entries analogue, so event extraction and
  resolution detection work unchanged. One caveat:
  replay redaction is a **key-name** blocklist, so the raw JSON's
  outcome-bearing keys (`ProceedingsandOrder`, `sJsonCreationDate`) sit on it
  alongside `docket_entries` — a new channel's snapshot shape must always
  be checked against that list.
- **The corpus stays the system of record.** Live-ness comes from trigger and
  cadence, not from bypassing the corpus: a watchlist refresh that finds a
  changed docket ingests it and queues `predict` through the same seams the
  rotation uses. Replay integrity, fan-out comparability (every predictor reads
  the same snapshot), validation, and stratification all depend on this — a
  predictor never fetches the live site itself.
- **Identity is reconciled by docket number.** The corpus keys cases on
  CourtListener docket ids, which a petition first seen at supremecourt.gov
  does not have. The join key is the normalized Term-form docket number, which
  both sources carry: a live ingest first looks for an existing SCOTUS row with
  the same normalized number and enriches it; only a genuinely unseen petition
  mints a new row. The minted id is deterministic and
  permanent — `9,000,000,000 + term×1,000,000 + serial` (`25-1234` →
  `scotus/9025001234`), collision-proof against CourtListener ids and decodable
  back to the Term-form number — and is **never merged**: `case_id`
  immutability wins (the ledger and snapshots key on it), so when CourtListener
  later ingests the same docket, a symmetric guard on its discovery path
  enriches the live-keyed row by the same docket-number join instead of minting
  a duplicate. Implemented in `fedcourtsai.supremecourt` (client + identity),
  `pipeline/live.py` (poller), and the `live-poll` CLI cycle; the per-Term
  discovery cursor persists in the corpus like the other watermarks.

## The live cert watchlist and conference detection

The consumer this channel exists for: a maintained watchlist of pending cert
petitions, refreshed on a cadence, with **conference membership parsed from the
proceedings** ("DISTRIBUTED for Conference of October 10, 2025"). That yields,
continuously and for free, what the long-conference task needs: the set of
petitions before each conference, discovered while they are pending — so
predictions fire ahead of the conference and score against the order-list
outcome days later, all in the forward stratum.

**Implemented:** the latest distribution entry per petition lands as the
corpus's `distributed_for_conference` (a relist updates it; non-live writers
preserve it); the refresh rotation leads with distributed petitions, nearest
conference first; and **predict fires on the distribution transition** — a
fresh distribution or a relist's new date — the cert-calendar analogue of
`pull.predict_on_change_only`, for petitions the salience gate admits (a
deferred petition's transition only keeps it on the watchlist; the cycle-end
selection sweep queues what a later selection latches; a relist inside its
requeue cooldown is suppressed instead — see
[salience.md](salience.md)). The pending-before-conference set is readable via
`fedcourts conference-set` (grouped by conference date; the September
long-conference set is its largest bucket).

The same proceedings parse lands two more cert signals as corpus columns, the
raw material for relist and CVSG base-rate cuts: `distribution_count`
(distinct conferences distributed for; relists = count − 1, floored at 0 —
an upper bound on true relists, since a reschedule before first consideration
also adds a distribution entry — and 0 asserts *parsed, never distributed*
while NULL means *never live-parsed*) and `cvsg_date` (the "Solicitor General
is invited to file" invitation entry's date). The raw `LowerCourt` string is
kept as `originating_court_name` so state courts and other tribunals outside
the tracked-court id mapping stay identifiable. All three are live-channel
facts: non-live writers preserve stored values (`distribution_count`
max-latches — proceedings are append-only, so the count only grows), and rows
written before the columns existed are back-filled from their stored live
snapshots at the historical walker's start (`backfill_live_signals` —
deterministic, idempotent, correct across corpus-blob rollbacks).

## Documents: from metadata to content

The document PDFs linked from each docket are the step-change in input quality
— the questions presented and the petition/BIO are the signals cert prediction
actually turns on. Two rules govern their use:

- **The pipeline fetches; agents never do.** Document text is fetched and
  extracted at ingest/provisioning time and attached to what the cell is
  provisioned with, so the snapshot rule ("predict from the snapshot") holds
  and every predictor reads identical inputs.
- **SCOTUS documents are free; circuit documents are not.** supremecourt.gov
  serves all SCOTUS filings at no cost. Circuit-court documents come from the
  RECAP archive when already liberated, else the RECAP Fetch API purchases them
  from PACER at PACER prices — a later, costed extension.

**Implemented:** the live poller fetches the petition and the brief in
opposition on the same **distribution transition** that queues prediction (the
record-complete moment, and near filing time — links are a rolling ~5-Term
window upstream); a gate-deferred petition's transition fetches nothing, and
the selection sweep provisions its documents if it is ever latched. Text is extracted with pypdf (born-digital filings under the
e-filing mandate; a scanned paper filing degrades to empty text), capped at
`live.document_text_cap` per document, and stored in the access-gated corpus's
`documents` table — never the git ledger. `provision-snapshot` materializes it
into the cell's gitignored `record/documents/` with a `documents.json`
manifest, and the predict prompt points agents at it. **The questions presented
are derived from the petition PDF, never from `QPLink`:** the `/qp/` page is
generated when certiorari is *granted* and opens with the grant order, so the
key is an outcome artifact — it is also stripped by replay redaction for the
same reason (verified live at implementation).

## The historical Term set: per-Term history through the same channel

The docket JSON serves decided petitions all the way back to OT2017 (the
e-filing era — the probe's Term floor above), so the cert **back-test set** is
built through the identical client, mapping, identity, and ingest seams as the
forward task — the dry run validates the actual instrument, not a proxy. `fedcourts historical-terms` (the `run-seed`
workflow) walks each configured Term's two numbering streams
sequentially from persisted cursors (`historical-paid` / `historical-ifp` in
the same cursor table as the forward frontier's, disjoint names so the walkers
never collide) and **samples deliberately rather than ingesting the sequence**:
a Term is overwhelmingly denials, so every decided petition is ingested except
denials, which are kept when their serial is a multiple of the configured
sampling interval — deterministic per serial, so resumed runs keep the same
sample, and the committed `historical:` config section documents the set's
construction. Every row records its **inverse inclusion probability** as
`sample_weight` (1 for anything kept with certainty — grants, dismissals,
forward-poller rows — and the sampling interval for a kept denial),
min-latched so a weight can only ever be learned toward certainty; a weighted
aggregate multiplies by it so the denial sampling cannot bias a base rate.
Weights land exactly at ingest time; the backfill for pre-capture rows
recovers them by rule (denied + serial on the sample grid + walker cursor
covers the serial), whose one residual — a pre-capture poller-resolved denial
inside a walker-covered range reads as sampled — is bounded and conservative.
When a stream's end is observed (consecutive 404s), the walk persists
`frontier_serial` beside the cursor — `frontier_serial = last_serial` is the
per-Term **walk complete** signal, and the cursors alone give an exact filings
census per Term and fee class (paid serials from 1, IFP from 5001) even for the
serials the sample never ingested. Each kept petition lands through `ingest_live_payload` already
**resolved** (machine-read label, dated raw-JSON snapshot, its cert event
latched closed) with filed documents provisioned for OT2021+ (the links'
retention window), so it provisions replay cells like any other case. Decided
history must never feed forward prediction: the loader files **no handoff
queues at all**, records with no readable disposition are skipped (pending
matters are the forward poller's charter), and resolved rows are structurally
invisible to the pending refresh rotation.

## Later: push for the circuit courts

CourtListener's **webhooks** (docket alerts fire within seconds of PACER
filings; search alerts batch ~5 minutes; retries + idempotency keys built in)
are the right liveness mechanism for the *circuit* dockets the pipeline tracks
— the Big Cases bot (`freelawproject/bigcases2`) is a running reference of
exactly this pattern. Adopting them needs two things this project does not have
yet: a public HTTPS receiver (GitHub Actions cannot receive webhooks, so a
minimal relay converts the webhook into a `repository_dispatch`) and an
organizational agreement with Free Law Project, which belongs in the same
conversation as the database replica. Until then, circuit liveness stays on the
rotation; SCOTUS — where the September task lives — does not wait on it.

## Terms

supremecourt.gov docket data and filings are public records of the U.S. federal
courts, served by the Court itself — no third-party license attaches (contrast
the CourtListener CC BY-ND terms in [data-sources.md](data-sources.md), which
cover Free Law Project's curation, not these records). The same
no-republication posture still applies to the packed corpus as a whole.
