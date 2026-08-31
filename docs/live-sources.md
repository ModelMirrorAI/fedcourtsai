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
- **A Term's numbering starts the July before the Term opens**, across all
  three streams: `26-1`, `26-5001`, and `26A1` were all docketed 2026-07-01,
  while `25-1432` (2026-06-30) closes the OT25 paid stream. A prober keyed to
  the Term's October opening misses the entire summer intake
  (`current_docket_term` carries the roll). The roll has a second edge: once
  the primary probe follows the incoming Term's numbers, the *outgoing* Term's
  streams stop advancing, so a late filing onto the old prefix goes unseen — and
  the historical walker does not recover it, since that walker advances its
  cursor over every served serial whether decided or not, so a serial it passes
  while still pending is never re-read: the tail is lost, not merely delayed.
  For `outgoing_term_grace_days`
  after the July roll (`live:` in `tracking.yaml`), discovery also probes
  `term - 1` from its own cursor — past a stale frontier — so that tail is
  caught at the source; the window, not the frontier stamp, retires the extra
  probe, because a drained stream is exactly the one a late tail lands on.
- Be a polite client: throttle to ~1 request/second, back off on errors, and
  poll on a cadence matched to the docket's rhythm (the shipped cadence is
  four live windows a day, covering the conference watchlist and frontier
  probing together) rather than hammering.

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
  replay redaction has two halves. Outcome-revealing keys — the derived,
  decision-only ones (`sJsonCreationDate`, `QPLink`, `disposition`, the decision
  dates) and the party/counsel blocks that accrue with every amicus filing (their
  size on a decided docket is a grant oracle) — come off by a **key-name**
  blocklist, so a new channel's snapshot shape must be checked against it. The
  proceedings entries are removed by **date** instead — content offers no
  rule separating a disposing order from a pre-decision entry, but an entry filed
  before a cutoff cannot record a decision that came after it. A new channel must
  therefore register its entries key in `PROCEEDINGS_KEYS` **and** expose a
  per-entry date, or its entries are unprotected; and the surviving entries are
  scanned for a disposition, falling back to removing them outright on a hit,
  because a disposing order that survives the cutoff means the cutoff itself
  cannot be trusted and the snapshot must show no trajectory at all.

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
preserve it); the refresh rotation leads with distributed *pending* petitions,
nearest conference first (a granted docket retained for its open merits event
rotates on staleness instead — its latched conference date is the one that
produced the grant, not a resolution about to happen); and **predict fires on
the distribution transition** — a
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

`capital_case` is a fourth column of this family — in practice live-channel
fed, since only supremecourt.gov serves the marking, though the ingest raise
is channel-agnostic by design — read not from the
proceedings but from the head of the payload: the `bCapitalCase` flag, OR-ed
with the `*** CAPITAL CASE ***` annotation upstream appends to `CaseNumber`.
Either alone under-reports, and the annotation has to be read anyway — ingest
strips it out of `docket_number`, because every reader that *parses* a docket
number reads the whole stored string and a marked number parses as nothing at
all. Those readers strip it too, so the cuts and the live channel's addressing
see a marked docket either way; what a stored marking costs is narrower — a
missed identity join for any consumer that does not normalize, a wrong value
wherever the column is displayed, and a trap for the next parse site that
forgets. It max-latches for the reason the other live columns do, and more
sharply: CourtListener serves the plain number and no flag, so every write from
that channel asserts a confident False. It is the one column of the family
**outside** `backfill_live_signals`, which fills the three proceedings-derived
columns only. A row still carrying the marking converges either by re-ingest — a
live-slice row on its next poll, one outside the slice on a targeted re-read — or
by `normalize-docket-markings`, the dedicated sweep that rewrites the stored
spelling and raises the flag without a fetch, which is what the backlog needs,
being overwhelmingly decided rows the rotation has left. Its apply half is
run-repair's `normalize-docket-markings` pass ([pipeline.md](pipeline.md)).
`validate-corpus` counts the remainder as an advisory check ([cli.md](cli.md))
rather than a failure, because rows written before the write site stripped the
marking carry one until something reaches them, and the verdict must not be red
for the whole interval.

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
manifest, and the predict prompt points agents at it. A cell can route around
an empty extraction — the prompt has it read the document as
content-unavailable rather than absent — but nothing in the fetch path repairs
one, so its size is a measured number rather than an impression: `fedcourts
corpus-info --text-coverage` counts the stored documents whose text is empty
or whitespace-only under the same predicate provisioning stamps as
`empty_text`, split on the salience gate's paid modern-cert segment, and names
whether the blob or the per-case content store served the reads, since a
blob-only read of a split corpus undercounts. The counts stay per kind because
the causes differ: an empty petition or brief in opposition is the scan, while
an empty derived questions-presented row is as likely to be a capture the
deriver would not vouch for. And the command reports the **absent** petition
beside the empty one, because that is the larger failure and a different
repair: a document never fetched has nothing to re-extract, so an empty-text
share read on its own would size the smaller of the two problems.
**The questions presented
are derived from the petition PDF, never from `QPLink`:** the `/qp/` page is
generated when certiorari is *granted* and opens with the grant order, so the
key is an outcome artifact — it is also stripped by replay redaction for the
same reason (verified live at implementation).

### How large the degradation is, and what is done about it

Measured on the blob the corpus pointer named on 2026-08-28 (`b16b856f…` — the
pointer is a content digest, which `corpus-info` does not print; its freshness
pair is a 2026-08-28 pull stamp and a 2026-07-13 newest stored snapshot, and
the documents were served by the per-case content store). Of the 9,231 stored
petitions, 271 carry no text: **2.94%** over both segments pooled, and **2.90%**
(192 of 6,613) over the cut the salience gate scores replay candidates on.
Those are stored documents, not cells. On the 242 cases queued for prediction —
where a missing petition costs a forward cell — **6** hold a petition that read
back empty, which the report does not print but its case-id ledger gives when
intersected with the rows carrying a `predict_queued_at`. Of the 271, 270 have
a page count and no text layer, the class optical character recognition can
repair, and one is a PDF the extractor could not open at all, which it cannot.
The 270 is an upper bound: a document whose text leaf never mirrored to the
content store reads back empty here too and is indistinguishable from a scan.
Briefs in opposition read empty on 34 rows (0.74% of the scored cut against
6.15% of the rest, on 244 rows), and the derived questions-presented rows on
37 — that column being structurally unable to carry a scan, since such a row is
written only where the petition has text.

The larger gap on the queued population is a different one: 29 of those 242
cases hold no stored petition at all — itself the recoverable-now cut of a much
wider stock of distributed rows nothing was ever fetched for. No extraction fix
reaches any of them; that is a fetch question, repaired in the fetch path or
not at all.

So the scanned-petition class is small on every population, and on this blob it
is a bounded 270 documents, each named in the report's case-id ledger alongside
the other kinds' empties. Six of the 271 empty petitions sit on cases queued
for prediction today; the rest pay off wherever the gate later mints a cell
over them. And the
degradation persists where it lands: a petition that reached the corpus as a
scan is unreadable for every cell minted over that case until the filing is
re-fetched at a new URL, and no other path repairs it. The decision is
therefore a **bounded local-OCR recovery pass** over exactly that class,
contracted below. Local tesseract only — at this share a metered OCR service
cannot be justified, and the pass's own cost is held down by the per-dispatch
bound in the contract rather than by a service bill.

Three residuals stay open by design. The unopenable PDF is not OCR's to repair
and stays counted as empty. The empty briefs in opposition stay out for a
structural reason rather than their share: a multi-respondent opposition is
stored as one combined row keyed on the whole set of fetched URLs, so text
recovered there is discarded the next time any co-respondent's brief is added
to that set — the recovery would not survive, which is not true of the petition
row. And recurrence: a scanned filing that arrives after a pass enters the
class and stays there until the next one. Nothing watches for that on its own —
the same `corpus-info --text-coverage` read is what sizes it, and the pass is
re-runnable over whatever it finds — so cadence is a dispatch decision taken
against a measured share, not a schedule.

### Contract for the recovery pass

Decided and specified here; not yet built. What a pass must hold to:

- **Where it runs.** As a pass on `run-repair` — a `repair` selector value, not
  a workflow of its own. The writer jobs are the only place a production corpus
  write can happen, and a pass whose dry run is a triage list a maintainer reads
  before an apply belongs on the bench by the standing rule (*Five writer jobs,
  one shared core* and *Maintenance passes* in
  [data-pipeline.md](data-pipeline.md)): it re-derives stored text with no
  upstream fetch, which is that lane's charter exactly. Tesseract is installed
  by that step alone, so no scheduled lane grows the dependency. Dry run by
  default, and bounded through `repair_bound` so a backlog clears in slices
  rather than in one long job; runner minutes are the whole cost.
- **What it reads.** Stored **petitions** whose text is empty or
  whitespace-only and whose page count is above zero. A zero-page row is either
  a PDF the extractor could not open or a derived section — `pages` carries
  both — and neither is OCR's to repair; a case holding no petition row is a
  fetch gap. Both stay out of the population. The coverage report's case-id
  ledger names the kinds that read back empty but not their page counts, so the
  pass re-derives that filter itself. The PDF is re-fetched by the row's stored
  URL, which for a petition is the single link that was fetched:
  supremecourt.gov, free and politeness-capped, so the pass spends none of the
  CourtListener budget.
- **What it does.** Walks the PDF's pages as the extractor does and OCRs a page
  **only** where that page's own text extraction yields nothing — a guard rather
  than a filter, since the population is documents that yielded nothing at all,
  but it keeps a mostly-digital filing with a few scanned exhibit pages honest.
  The same per-document text cap the fetching lane applies and the same
  truncation flag bound the result, so a recovered petition is bounded exactly
  like a fetched one. Additive by construction: text is written only
  where extraction stored none, so the pass cannot overwrite an extraction. Nor
  is a recovery overwritten later — the row keeps its URL, and both the poller
  and the Term walker re-fetch a kind only when its link changes; a genuinely
  superseding petition at a new URL is re-fetched and, if it too is a scan,
  re-enters the class.
- **What it records.** OCR output is *derived* text, lossy in a way pypdf output
  is not, so it must never read as a clean extraction — and the stored document
  carries no derivation marker today. Adding one is three surfaces, not one:
  the document model, an additive `documents` column with a constant default
  and the migrator to back-fill it (the `cases` and `events` tables carry that
  pattern; `documents` does not yet), and the content-store manifest writer and
  reader, which serialize a document field by field — a field added to the model
  alone reads back at its default on the offloaded path, which is the path
  production reads. It regenerates `schemas/` like any model change.
  Provisioning then carries the marker onto the cell manifest beside
  `empty_text`, and the predict prompt gains the reading rule that pairs with
  it, since a bare manifest key teaches an agent nothing; the coverage read can
  then count what was repaired.
- **What follows a recovery.** A recovered petition re-derives its
  questions-presented row through the existing deriver, since such a row is
  written only where the petition has text. On OCR text that derivation keeps
  the two outcomes it has now: no recognizable heading stores no row at all,
  and a heading whose capture the deriver will not vouch for stores the empty
  row.
- **Terms.** Unchanged. These are the Court's own public records, and OCR text
  lands in the access-gated corpus under the same no-republication posture as
  every other extraction ([data-sources.md](data-sources.md)).

## The historical Term set: per-Term history through the same channel

The docket JSON serves decided petitions all the way back to OT2017 (the
e-filing era — the probe's Term floor above), so the cert **back-test set** is
built through the identical client, mapping, identity, and ingest seams as the
forward task — the dry run validates the actual instrument, not a proxy. `fedcourts historical-terms` (the `run-seed`
workflow) walks each configured Term's two numbering streams
sequentially from persisted cursors (`historical-paid` / `historical-ifp` in
the same cursor table as the forward frontier's, disjoint names so the walkers
never collide) and **ingests every decided petition**, denials included. The
walk has already fetched the payload by the time it can read the disposition, so
declining to store one saves no request; it only drops a row the corpus can then
recover solely by re-walking the whole Term. Every row records its **inverse
inclusion probability** as `sample_weight` (1 for anything kept with certainty,
which is now everything the walk writes), min-latched so a weight can only ever
be learned toward certainty. The column stays because the corpus still holds
denials an earlier sampled walk kept at weight 10: a weighted aggregate
multiplies by it so that legacy frame cannot bias a base rate, and each such row
regresses to 1 as a re-walk re-serves it — correctly only where the re-walk
enumerates the whole block, so that the nine petitions the weight stood for
arrive with it. A row regressed while its neighbours did not arrive leaves them
represented by nobody, which under-counts that block's denials rather than
over-counting them.
Weights land exactly at ingest time; the backfill for pre-capture rows
recovers them by rule (`legacy_denial_sample_weight`: denied + serial on the
sample grid + walker cursor covers the serial + the block it would stand for is
not already stored row by row). The last conjunct is what the first three cannot
supply: landing on the grid below the cursor proves the serial was *probed*, not
that only one in ten was *kept*, and those coincided during the legacy sampled
walk and not after it — so without it a denial from a fully-walked range would
stand for ten petitions, nine of which the corpus is separately counting at 1.
A weight of 10 is a checkable claim about nine specific neighbouring serials, so
`sampled_block_is_enumerated` checks it: it counts how many of the serials within
nine either side are stored in the live slice, and a count in the enumerated
range means those petitions are observed rather than passed over. The read is **per row**, not per
Term, because the enumerating walk resumes from the sampled walk's persisted
cursor — one Term can carry a sampled prefix and an enumerated tail, and a
whole-Term verdict would hand one regime's answer to the other's rows.

The criterion between the two error directions is that over-weighting fabricates
an observation while under-weighting only forgoes a correction. The enumeration
check is a **deny-list**, so the rule's default is the sampled weight — the
fabricating side — and both known residuals land there: a pre-capture
poller-resolved denial inside a *sampled* range reads as sampled, and a block
only partly stored (the walk's grant-family keeps, or a neighbourhood straddling
the resume boundary) stays sampled until enough of it is present. What bounds
them is where the threshold sits rather than the shape of the rule: measured
across the corpus's grid denials a sampled block holds at most six stored
neighbours and an enumerated one at least ten, and the cut is placed at the low
edge of that empty band so the slack goes to catching enumeration. Only the
reverse misclassification — a genuinely sampled block read as enumerated — fails
safe.
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
invisible to the live refresh rotation. (The one row that stays visible is
the one whose ingest *itself* resolves a tracked open petition as granted:
the grant mints the open merits event, exactly as the watchlist path would,
and the rotation keeps that genuinely-live merits proceeding — see
[data-pipeline.md](data-pipeline.md).)

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
