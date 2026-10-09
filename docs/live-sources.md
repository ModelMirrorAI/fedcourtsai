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
https://www.supremecourt.gov/rss/cases/JSON/<term>-<number>.json   # cert
https://www.supremecourt.gov/rss/cases/JSON/<term>A<number>.json   # application
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
  and `live.frontier_misses` consecutive 404/empty records mark the current
  frontier — a tolerance rather than a single miss, since an occasional serial
  is withheld mid-stream.
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
preserve it); and the refresh rotation's priority tiers are distributed
*pending* petitions, nearest conference first (a granted docket retained for
its open merits event takes the Term-then-staleness order below instead — its
latched conference date is the one that produced the grant, not a resolution
about to happen) and, within one conference, never-polled then stalest first;
then recent Terms first, then stalest. Staleness leads the Term inside a conference because the whole
distributed set must be re-read once its order list issues: Term first, the
newest Term's still-pending dockets (relisted, rescheduled) would take the head
of every cycle while an older Term's petitions on the same conference waited.

Each of those tiers is unbounded in size while the cycle's cap
(`live.max_cases_per_run`) is fixed, so a tier larger than the cap — the
long-conference distributed set, or a new Term's onboarded petitions — would
hold the head of every cycle and nothing behind it would be polled again. A
**staleness bound** sits ahead of all of them: a docket the channel last
polled more than `live.max_poll_staleness_days` ago leads the next cycle,
stalest first, so no polled docket goes unpolled longer than that bound plus
the cycles its overdue backlog takes to drain. The overdue tier takes at most
`live.max_overdue_per_run` of each cycle, so a large backlog drains over
several cycles while the distributed petitions, whose order-list results are
days away, keep the rest; an overdue docket past that share keeps its ordinary
place. A never-polled row has no stamp to age and keeps its ordinary priority-tier place.
The bound is set well above one sweep of the polled watchlist at the cap, so
it bites only when a tier is starving the rest and the priority tiers govern
otherwise.

**Predict fires on the distribution transition** — a fresh distribution or a relist's new date — the cert-calendar analogue of
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
being overwhelmingly decided rows the rotation has left. Its apply runs as a
standing sweep on run-seed's daily window and as run-repair's
`normalize-docket-markings` pass ([pipeline.md](pipeline.md)).
`validate-corpus` counts the remainder as an advisory check ([cli.md](cli.md))
rather than a failure, because rows written before the write site stripped the
marking carry one until something reaches them, and the verdict must not be red
for the whole interval.

On a granted docket the same parse also lands the **merits decision record**
(`pipeline/decision_record.py`), over every grant — the GVR and the summary
reversal included, where the merits pair (`merits_judgment` / `merits_decided`)
reads only the grants that open a merits proceeding. `merits_argued` is the
date of the docket's last entry opening on its own verb — "Argued. For
petitioner: …" or "Reargued. …" — on or after the grant, so a reargued case
carries the reargument; the scheduling notice ("SET FOR ARGUMENT on …"), an
appointed amicus's invitation "to brief and argue", and a motion for divided
argument all name argument mid-sentence and stay unmatched.
`merits_decision_method` says how the case was decided, read from the same
last judgment-shaped entry the merits pair is parsed from, with its markup
dropped (the docket links the opinion: "Gorsuch, J., delivered the `<a …>`opinion`</a>`
of the Court"): a named Justice delivering the opinion — "of the Court", "for a
unanimous Court", or announcing the judgment of a fractured Court — is
`argued-signed` after argument; "Opinion per curiam." or an affirmance by an
equally divided Court is `argued-per-curiam`; a judgment riding the order that
grants (a cert-order label, or a judgment dated on or before the grant) is
`summary-opinion` where the entry carries an opinion and `summary-order` where
it does not, the ordinary GVR — whose "(per curiam)" is a citation of another
case's opinion, not one of its own; and a DIG is `dig`, argued or not. With no
argument on the record, a per curiam decided after the grant is
`summary-opinion`, while a *signed* opinion is left null on purpose — it almost
always means the argument entry was missed, not skipped — as is an argued
entry that recites neither form. Both columns fill-in latch: a payload that
yields no reading keeps the stored one, while a fresh reading (a reargument, a
decision) takes over — and so does a wrong one, since a payload served without
its argument entry can move the argued date back or read an argued per curiam
as a summary one, the exposure the dated live signals already accept. A stored row whose columns are null
is read from its newest stored live snapshot by `backfill-decision-record`,
which never overwrites; its dry run runs from a dev checkout or as run-repair's
`decision-record` pass, and its apply as that pass or as a standing sweep on
run-seed's daily window. Neither column reaches a cell: both are withheld from the
`query` retrieval rows ([corpus/README.md](../corpus/README.md)).

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

**What is selected, and under which kind.** Selection reads the *filing*, not
the docket form, so one function serves both lanes:

- **`petition`** — the case-opening filing, whichever writ it seeks. The Court
  opens a cert-form docket on any of seven entry shapes: a petition for a
  writ of certiorari, for certiorari *before judgment*, for *mandamus*, for
  *prohibition*, for *mandamus and/or prohibition*, for
  *habeas corpus* (whose entry omits the article — "Petition for writ of habeas
  corpus filed."), and a direct appeal's *statement as to jurisdiction*. They
  are one kind because they are one role — the document that asks the Court to
  take the case, fronting the questions presented under Rule 14.1(a), Rule 20.2
  or Rule 18.3 — and a kind per writ would fracture the coverage metric, the
  questions-presented derivation and the cell manifest across seven names for
  one thing. The match is anchored at the entry's start, because the same phrase
  runs mid-sentence in a motion *about* the petition. The link is taken by
  label, `Petition` or `Jurisdictional
  Statement`, since a direct appeal posts its opening filing under the second;
  an entry whose label is neither falls back to its first link, so an
  unforeseen spelling stays fetchable rather than being dropped.
- **`application`** — the **substantive** interim relief an application asks
  for, taken from the `Main Document` link on the entry submitting it to a
  Justice and from no other, since the covering `Written Request` and `Proof of
  Service` ride the same entry. Entry-keyed like the rest, so an application
  filed *into* a cert
  docket is selected there too, which is the right reading: the filing is real
  and the cell should read it. A separate kind, because an application is a
  different ask: it seeks
  relief rather than review and carries no questions-presented section, so
  folding it into `petition` would make the coverage metric mean two things and
  the QP derivation run over a document that has none. The ask is read
  **positively**, by the same predicate that gates the interim predict queue, so
  the selector fetches exactly the class that mints cells: an administrative
  application — more time ("to extend *further* the time", the renewal wording
  a plain extension phrase misses), more pages, more words — is not selected,
  and neither is an ask the classifier cannot read, which costs no cell because
  the same reading keeps that docket out of the queue.
- **`appendix`** — the appendix the case-opening entry, or the application
  entry, posts under its own `Appendix` link beside the filing, and no other
  link. One per docket. It carries the opinions and orders below, which is what
  a vehicle reading needs and what a petition with a separately filed appendix
  otherwise never provisions. A petition whose appendix is bound into the same
  PDF keeps it inside the `petition` row; both are cut by the appendix-aware
  rule below.
- **`brief-in-opposition`** — every non-amicus opposition brief **filed at the
  cert stage**, combined into one document. The respondent's brief is read in
  the Court's other spellings too: "Brief **for** the respondent(s) …", up to
  three words before the party word ("Brief of Federal Respondents filed.",
  "Brief for the Federal Respondents filed."), and the **response** the Clerk
  enters without the word "brief" ("Response of respondents … filed.",
  "Response to petition from respondent … filed."). The response form is kept
  off the collateral responses that share its opening — to a motion, an
  application, a rehearing petition, a letter, an order or a suggestion of
  mootness.
- **`cert-reply`** — the petitioner's **cert-stage** reply, the Rule 15.6 answer
  to the opposition and often the only filing that meets its vehicle and
  preservation objections. The first "Reply [brief] of/for … petitioner(s) …"
  entry filed before the grant and before any disposition entry, from its `Main
  Document` link alone. The merits reply arm reads the same words after the
  grant, so the grant date is what separates the two, and the docket order of
  the disposition keeps a reply filed after a denial (a rehearing paper) out.
  "In opposition" is no exclusion here — "Reply of petitioner to brief in
  opposition" is exactly this filing — while any reply naming a motion, an
  application, a letter or a suggestion of mootness (collateral practice,
  "in support of" it or "to the response to" it), replies supporting the other
  side, amici's replies and rehearing and supplemental papers are.
- **`sg-invited-brief`** — the **Solicitor General's invited brief**: the first
  brief for the United States as amicus curiae ("Brief amicus curiae of United
  States filed.", "Brief for the United States as amicus curiae filed.") entered
  **after** the Court's invitation to file one and before any disposition entry,
  in docket order, from its `Main Document` link alone. The filer must be the
  United States and nothing after it, so an amicus whose name merely opens with
  those words ("United States Conference of …") is not read as one, and the entry
  must say "amicus", so the United States filing as a party stays with the
  opposition. It is the one amicus filing any arm selects: the Court asked for
  it, and on an invited petition it is most often the filing that decides it.
- **`merits-brief-petitioner`** / **`merits-brief-respondent`** — each side's
  brief on the merits, one row per side and one URL per row, taken from the
  entry's `Main Document` link and from no other (a merits-brief entry posts its
  certificate of word count and proof of service beside the filing). Selected
  only on entries filed **after the cert grant**, because the Court writes a
  merits brief and a cert-stage response in the same words — "Brief of respondent
  United States filed." either way, with "on the merits" appearing on the
  scheduling order and never on the brief entry — so the grant date is the only
  thing that separates the two stages. That same bound is what keeps the cert
  slot above from swallowing a merits brief and pipe-joining it into the
  opposition. Per side rather than pooled: two adversarial briefs under one kind
  would share one extraction cap, so the second would be cut by however long the
  first ran. The first brief in docket order on each side — the first whose entry
  posts that link — is the opening one; the reply is a separate entry family
  ("Reply [Brief] of/for …") the two reply kinds below take, and the joint-appendix
  reprint is passed over because the opening brief precedes it. **One per side**
  is the
  accepted residual, and it is the opposite call from the opposition arm above
  on purpose: a case with several respondent groups files several merits briefs
  and only the first is stored, because combining them is exactly what the
  per-side kinds exist to avoid. The entry opens "Brief of …" or the Court's
  title form "Brief for the …" (often naming no party), either with an optional
  leading "Redacted" — the public copy of a brief filed under seal ("Redacted
  brief of petitioner … filed."). Every spelling is still anchored at
  the entry's start, so a filing *about* a brief ("Motion to file petitioner's
  brief on the merits under seal with redacted copies …", "Motion for an
  extension of time to file the briefs on the merits …") is not selected. On the
  respondent side the wider reading is the selector's alone: the briefed merits
  moment is still dated by the narrower "Brief of respondent …" reading, since
  which document a cell is given and when its moment opens are separate
  questions.
- **`merits-reply-petitioner`** / **`merits-reply-respondent`** — each side's
  *reply* on the merits, the last word on the argument and the one filing that
  answers what the other side actually argued. A distinct entry family ("Reply
  of X filed.", "Reply Brief of X filed.") that the opening-brief anchors never
  reach, read on exactly the terms those arms are: one per side, the first in
  docket order after the grant, `Main Document` only, and the same post-grant
  bound. That bound carries more weight here than anywhere else in the selector,
  because the **cert-stage** reply to a brief in opposition is spelled word for
  word the same and is a routine filing — an unbounded arm would store one as
  merits advocacy across a large part of the docket stock. Under Rule 25.3
  the petitioner is the side that ordinarily replies; the respondent arm reaches
  the postures where the last word is its own — a cross-petition, or a case the
  Court appointed an amicus to defend the judgment in. Two reply shapes are
  deliberately out of reach. A reply on a **collateral motion** is not merits
  advocacy: the unpartied form ("Reply on motion to intervene filed.") falls
  outside the anchor, and the partied one ("Reply of petitioners in support of
  motion for divided argument filed.") satisfies it word for word and is excluded
  explicitly — which matters more than the filing is worth, because each arm
  takes the first qualifying entry and then closes, so a motion reply filed
  before the briefs would occupy the side's slot and put its real merits reply
  out of reach. And a reply the Clerk recorded under counsel's own name rather
  than a party's is left unfetched rather than guessed at, since no party-word
  anchor can read it. The reply arms read the same two further spellings the
  briefs do ("Reply brief for the petitioner …", a leading "Redacted").

- **`questions-presented`** — derived from the `petition` text alone, never
  fetched and never derived from an `application`.

**Consolidated members read their merits filings off the lead docket.** When
the Court consolidates cases for briefing and argument it enters, on every
docket of the group, "Because the Court has consolidated these cases for
briefing and oral argument, future filings and activity in the cases will now
be reflected on the docket of No. 24-20." From then on the merits briefs and
replies are entered on the lead docket alone, and a member's own JSON never
shows them. So on a **member** — a docket whose entry names a number other
than its own `CaseNumber` — the fetch reads the lead's docket JSON as well (one
more paced GET through the same client and endpoint), and each of the four
merits kinds the member's own docket does not yield is taken from the lead's
selection. The rules:

- **The lead is read off the entry**, not off the Granted & Noted list: the
  entry is on the payload already in hand, names the lead explicitly, and is
  entered the day the Court consolidates. The lead's own docket carries the same
  words naming itself, which is how it is told apart. One hop only.
- **Merits kinds only.** The member's petition, opposition and derived
  questions presented stay the member's own; so does any merits filing its own
  docket carries, which is kept over the lead's.
- **Only the member's own filings.** A lead carries the filings of every docket
  in the group, so the first petitioner's brief on it is often another
  docket's — and in a cross-positioned group, a party that is the member's
  *respondent*. A lead entry is the member's only where its "(as to No. …)"
  mark names the member's number, or, unmarked, where the filer it names is a
  party on the member's own side list (`Petitioner` for a petitioner-side kind,
  `Respondent` for a respondent-side one), compared on name tokens. An entry
  naming no filer ("Brief for the petitioner filed.") cannot be placed on a
  lead and is not borrowed; neither is anything when no entry is the member's.
- **Provenance stays honest.** A borrowed row is stored under the member's
  `case_id` with the lead's PDF URL and the lead entry's date, so the manifest
  says where the text came from and a moment cut places it by the day it reached
  the record.
- **Timing.** A lead filing is borrowed only if it is dated after the
  **member's** own grant (as well as the lead's), so a member consolidated into
  an already-briefed lead does not read, at its grant moment, advocacy filed
  before it had a merits stage. A member whose grant cannot be dated borrows
  nothing. A replay or moment cut then applies by entry date exactly as to the
  member's own documents.
- **Contact scrub.** The staged-text scrub runs over a borrowed document exactly
  as over the member's own, keyed on the **member's** counsel blocks — which is
  right for the member's own pro se filings, since those are now entered on the
  lead. The lead's party blocks are not compared at provisioning (it reads one
  case's snapshot), so a lead whose party side reads as self-represented lends
  nothing, and the run log says so. A self-filing amicus on the lead's `Other`
  list does not block it: no amicus brief is staged but the Solicitor
  General's invited one (`sg-invited-brief`), which counsel for the United
  States files.
- **A lead that does not serve** is warned into the run log and read as no lead:
  the member's own documents are stored without it.

The **lead's own** selection reads the same attribution the other way round. A
lead docket — one whose consolidation entry names its own number — carries
every member's merits filings as well as its own, so a first match there can
store a member's brief as the lead's. Its merits kinds therefore prefer an entry
attributed to the lead (an "(as to No. …)" mark naming it, or a filer on its own
side list), fall back to an entry that names no placeable filer, and never take
one the Clerk marked for other dockets alone. Its cert-stage kinds are its own
docket's, as on any other.
**Implemented:** each lane fetches at the moment it queues prediction, which is
not the same moment for both. On a cert docket that is the **distribution
transition** (the
record-complete moment, and near filing time — links are a rolling ~5-Term
window upstream); a gate-deferred petition's transition fetches nothing, and
the selection sweep provisions its documents if it is ever latched. That sweep
is the lane a **merits** filing arrives on: the distribution transition
is a cert-stage trigger and a granted docket stops distributing, so the four
merits kinds are fetched when the sweep re-provisions a case carrying an open
merits event, never at the trigger that first filled its cert documents. A
granted, briefed case whose merits documents were never fetched — whatever the
state of its events — is also reached by `document-backfill`'s merits arm, the
maintenance pass that applies the current selector to the cases already past
their trigger ([data-pipeline.md](data-pipeline.md)). An
application docket is never distributed for conference, so its lane fetches on
**any change while the application is still pending, in scope, and substantive**
— the application rotation's own queue condition. Text is extracted with pypdf (born-digital filings under the
e-filing mandate; a scanned paper filing degrades to empty text), capped at
`live.document_text_cap` per document (one cap per row, so a separately linked
appendix, a reply or the invited brief each has its own and none is cut for
another's length), and stored as the case's document row in
the access-gated corpus — the per-case content store under the corpus split, the
blob's `documents` table on a self-contained one — never the git ledger.
`provision-snapshot` materializes it
into the cell's gitignored `record/documents/` with a `documents.json`
manifest, and the predict prompt points agents at it. Each manifest row carries
a one-sentence `kind_description` saying what the file is and how it was cut, so
a kind the prompt does not name yet still describes itself.

**The appendix-aware cut.** The `petition`, `application` and `appendix` rows
are not head-cut at the cap, because on a filing that carries an appendix a head
cut loses the wrong half: the cap lands inside the appendix, and everything
after its first long opinion — the short lower-court orders an application turns
on above all — is dropped. Those three kinds read every page and are cut so
that:

- **under the cap nothing changes** — the text is every page joined, as before;
- **the filing's own body is never cut for its appendix** — the body (every page
  before the appendix starts: an `APPENDIX` divider, the appendix's own contents
  page or its first folio, read from the fourth page on and never on a contents
  page of the filing itself) is kept whole, and only the appendix pays for the
  overflow; a body that alone fills the cap is head-cut with the appendix;
- **every appendix item keeps its opening** — the appendix is split into its
  items (by its own index, matched to the folio each page prints; else by its
  "Appendix A/B/…" headings; else by a running header that changes and holds),
  each keeps about a page, and the rest goes to the **court decisions** —
  opinions, orders, judgments — before record material such as complaints and
  briefs. On a petition the decisions are completed in appendix order, the
  judgment under review first; on an application they are completed shortest
  first, so an order under review printed after a sixty-page opinion is kept
  whole;
- **every cut is stated in the text**, on its own line, as `[pipeline note: N
  characters of … omitted here, from part-way through PDF page X to …, to fit the
  150,000-character text cap]`, beside the row's `truncated: true`.

Where a filing runs past ten times the cap, reading stops there and a last
note names the pages never read. A page that fails to extract costs that page
alone. The cut applies to rows stored from now on: fetching is idempotent per
kind and URL, so a petition or application already stored keeps its head cut
until its link changes, and the corpus holds both vintages side by side.

The OCR recovery pass keeps the plain head cut for the rows it recovers: the
appendix-aware cut reads every page, which on a scan means recognizing every
page, and a long scan would spend its whole document budget and be discarded on
every pass.

That staged copy is where the **contact-detail scrub** applies, and it applies
to the copy alone: the source PDF and the stored row keep the filing as filed.
A cell's prose lands in the public ledger, so the text it reads is a
republication surface as well as an input — and where the provisioned snapshot
serves a counsel block on either party side, petitioner or respondent, naming
nobody but the party to write to, the caption and signature block of what that
party filed are an individual's own. The docket JSON never says "pro se", so
the reading is upstream's own, in three arms, all of them read off a **served** block: a self-represented party
listed as its own attorney (compared on first and last name after a leading
"In re", "In the Matter of" or "Ex parte" caption is cut, since the two fields
disagree on the middle constantly; a title or honorific — "Professor", "Hon.",
"Dr.", "(Ret.)", "Esq." — is read through, and a `PartyName` naming several
people jointly, or a name followed by a comma-separated description
(", APC"), matches where the attorney is any one of the people it names), a block naming
no attorney at all,
and a prisoner register number on the block — the incarcerated filer, whose own
address a filing carries most reliably. The arms are the same on either side,
and any one qualifying block is enough, so a docket carrying a represented
co-petitioner beside a self-represented one is scrubbed, and so is a counselled
petition answered by a respondent filing in person. The `Other` list — amici
and other non-party filers — is read too, on the first two arms only: an
amicus served as its own attorney (in practice individual lawyers, law
professors and retired judges) or with no attorney named. The comparison is
the party sides' own, so a self-filing amicus served as "Professor …",
"Hon. … (Ret.)" or "… and …" with the bare name as `Attorney` reads as
self-represented. Each person a joinder names is compared on their own, and
no added reading joins the first name of one to the surname of another (the
as-served reduction is kept, so the change only widens), and a title is cut only as a whole
leading word ahead of a name, so an organisation served beside the attorney
("Professor … and … Law Center") qualifies through the person it names and an
organisation named for someone else ("Family Policy Foundation and The
Hartwell Center", against "Walter Hartwell") does not. On the pulled blob no organisation's block
qualifies on its own, since every one names a person as `Attorney`. The register-number
arm is not asked there, because `PrisonerId` on an `Other` block is not a
register number: on the pulled blob at pull stamp `2026-09-29` every populated
value on that list is an address-shaped string or a phrase on an organisation
served with separate counsel, which the arm would read as an incarcerated
filer. The residual is a represented amicus block that did carry a real
register number (none on that blob): it would stay as served, where a
party-side one is withheld whatever its `Attorney` says. A docket whose only
qualifying block is an amicus's gets the **value pass alone** (below): no
amicus's own brief is staged — the one amicus kind, `sg-invited-brief`, is the
United States' brief filed by its counsel — so what is staged there is counsel's
filings, and the shape pass would cost their text its misreads of legal prose —
a case name led by a street number, a regulation number in telephone shape —
where the staged filers are represented. The premise is about amici, whose
own briefs are never staged; a self-represented non-amicus `Other` filer (an
intervenor, say) whose own opposition is staged would get the value pass alone
too, so a detail of theirs spelled otherwise than the docket serves it would
stay (none on the pulled blob). Where no amicus value clears its
floor, nothing runs and the documents are staged as filed. On a docket read as
self-represented on a party side, every
document staged has its emails, telephone numbers, post-office boxes and
street addresses replaced by the fixed token `[contact detail withheld]`, which
keeps the document's structure and tells a reader that something was withheld
rather than that a line is missing. It runs as two passes. The **shape** pass
matches what a contact detail looks like, including an email address as a scan
fragments it (a blank beside the `@` or a dot, a letter-spaced local part,
`(at)`), and never takes a line break. The **value** pass looks for the
`Email`, `Phone` and `Address` strings on every served block of each side read
as self-represented (the filer's own, and any co-party counsel's on that side
— never a side whose blocks all name counsel; on the `Other` list, the
qualifying blocks' alone, since amici are not co-parties), however the scan spaced or
line-broke them, and puts back every line break it consumed; it runs only
where the docket serves a value specific enough to key on (an email with its
`@`, a telephone number of ten or more digits, an address with a digit and
eight or more significant characters). Both passes are matched against the
original text and overlapping matches are withheld as one span, so adding a
pass can only widen what is withheld. The manifest entry carries what happened: `contact_scrubbed`, whether
the scrub ran over this document's staged text; `contact_replacements`, how
many it withheld — so `true, 0` (scrubbed, nothing found) stays
distinguishable from `false, 0` (a represented docket's text, or the text of
an amicus-only docket whose amici serve no value specific enough to key on,
untouched — the run log says `not run` for the latter); and
`contact_scrub_passes`, which passes ran (`["value", "shape"]`, `["shape"]`,
`["value"]` on an amicus-only docket, or `[]` where the scrub did not run), so
a shape-only or value-only scrub is not read as the complete one. A filing by
the other side's counsel on a docket read as self-represented on a party side
is
scrubbed with the rest, since the reading is the docket's and taken once:
the cost is a firm's switchboard number a cell had no use for.

**A payload serving no block on a side is unknown on that side, not
unrepresented**, and is left alone. Nor does a served block read as naming
no attorney where upstream simply has not filled the field: no served block on
either side leaves `Attorney` blank (none of the 3,474 petitioner- and
respondent-side blocks across the 3,073 snapshots the pulled blob itself holds,
at pull stamp `2026-09-29`, newest snapshot `2026-07-13`) — so a docket
awaiting its opposition is not scrubbed on that account. The snapshots key space holds two payload shapes, and the
other one — a CourtListener REST docket, which carries no counsel blocks
anywhere — names nobody because it has nowhere to. Reading that as
self-representation would scrub on the strength of a payload shape rather than
of a fact about the docket, and over the stored payloads in the corpus it would
take 2,012 of 2,925 cases rather than 654 (pull stamp `2026-09-29`). So the scrub fires on evidence rather
than on the absence of it, and a docket whose counsel the corpus does not carry
stages its text as filed. What the scrub
reads is **representation**, which is a different fact from the **fee** class
the salience gate excludes at tier 0 ([salience.md](salience.md)) — that one is
read off the docket serial, this one off the counsel blocks — so a paid docket
can be self-represented, and the interim, replay and evaluate lanes sit outside
that gate entirely.

**What the scrub does not reach**, named so the section is not read as a covered
surface. No pattern spans a newline — that is what makes the structural claim
above true rather than aspirational, and it costs a detail the extractor broke
across two lines. The blank-separated telephone spelling (`202 555 0147`) is
deliberately not read at all: an appendix index and an OCR'd column emit exactly
that shape, and the scrubbed population is disproportionately the scanned one,
so reading it would delete legal text from the cells the scrub exists for. Nor
are a box spelled out in full, a number written with a slash or with no
separators, a bare city/state/ZIP line — that shape is also how the Court's own
address line is set — or an incarcerated filer's register number beside an
institution name, which has no shape at all.

**The staged snapshot gets the same withholding, by key rather than by shape.**
`record/snapshots/<date>.json` is the upstream payload, whose counsel blocks
carry `Address` / `City` / `Zip` / `Phone` / `Email` / `PrisonerId` as labelled
keys — on a self-represented docket the filer's own details in a more quotable
form than any signature block. On such a docket, every block on either party
side or the `Other` list that the trigger reads as naming nobody but its filer
— on a party side a block carrying a register number included, whatever its
`Attorney` says, so a counselled incarcerated party's block loses its
counsel's professional details — has each
populated `Address`, `City`, `Zip`, `Phone`, `Email` and `Title` (free text
nothing reads, which upstream sometimes fills with an inmate number) replaced
by `[contact detail withheld]`, and
a populated `PrisonerId` replaced by `[register number withheld]`: the number is
the personal datum, its presence is upstream's marker for an incarcerated filer,
which the trigger's third arm reads and a cell may reason from, so the marker
keeps the presence. On a qualifying `Other` block, where the key holds no
register number, a populated `PrisonerId` is withheld with
`[contact detail withheld]` instead. `PartyName`, `Attorney`, `State` and
every other block — a represented party's counsel on either side, a
represented amicus — stay as served, and an empty key stays empty. The copy is built beside the payload rather than in
place of it, so the cell context, the trigger and the document scrub all read
the payload as served; nothing scored or analytic reads the withheld keys (a
test pins both halves: no module outside the scrub names them as literals or
imports its key list, and every row, band, context and gate derived from a
scrubbed payload equals the one from the original). The provisioning step echoes the counts, never a value:
`snapshot contact scrub: N value(s) withheld on M petitioner-side block(s)`,
with `respondent-side`, `amicus-side` or a `/`-joined list such as
`petitioner/respondent-side` naming the lists read as self-represented (the
`Other` list is named `amicus`); the document scrub's line names them the same
way (`no attorney named for the petitioner`, `the respondent`, `the amicus`, or
`the petitioner/respondent`), with `passes: value` on an amicus-only docket.
Both files are gitignored, and no predict or evaluate cell uploads `record/`,
so what can reach public git from a cell is what its prose quotes, which is the
exposure [data-sources.md](data-sources.md) already names. The case-summary
lane's one-day `summary-stage` artifact does carry both staged files, scrubbed
as above ([case-summaries.md](case-summaries.md)). The scrub narrows what
reaches the ledger; it does not make a filing anonymous, and a cell with
retrieval rights can reach the same PDF and docket JSON upstream whatever was
withheld from its copy.

A cell can route around
an empty extraction — the prompt has it read the document as
content-unavailable rather than absent — but nothing in the fetch path repairs
one, so its size is a measured number rather than an impression: `fedcourts
corpus-info --text-coverage` counts the stored documents whose text is empty
or whitespace-only under the same predicate provisioning stamps as
`empty_text`, split on the salience gate's paid modern-cert segment, and names
whether the blob or the per-case content store served the reads, since a
blob-only read of a split corpus undercounts. The counts stay per kind because
the causes differ: an empty petition or brief in opposition is the scan; a
near-zero count on any of the four merits kinds is the shape of the granted
slice, since nothing selects them before a grant, rather than a coverage gap
(and the two reply rows are narrower again, bounded by the granted cases whose
docket carries a reply at all); and an empty
derived questions-presented row is as likely to be a capture the deriver would
not vouch for. And the command reports the **absent** petition
beside the empty one, because that is the larger failure and a different
repair: a document never fetched has nothing to re-extract, so an empty-text
share read on its own would size the smaller of the two problems. That absent
population is enumerated over the queued rows, not only counted: a petition can
be missing by several routes — a case that reached the queue without its
documents ever being provisioned, a fetch that failed, a link upstream no
longer serves — and only the case ids let a given case be assigned to one. The
queued gap is **keyed on the docket form's own primary document** and reported
as two counts with two ledgers, each against its own form's denominator: a
cert-form row against its `petition`, an
application-form row against its `application`. Neither is a floor — an
application docket that holds its application is as complete as a cert docket
that holds its petition — so the second count drains as the documents store
rather than standing forever as a structural exclusion, which is exactly why it
needs a denominator: a gap that drains says nothing without the population it
drains from. The wide `distributed`
stock stays petition-keyed and unfiltered, matching what it is. On the fetch
side the routes are recorded as they happen —
`documents.document_fetch_losses` counts what each pass lost, by reason — three
of them per document (a transport failure, a link the upstream did not serve, a
link that is not HTTPS on the Court's own host) and two per case (an opposition
whose every brief failed, and an opposition only *some* of whose briefs did) —
and each one is warned into the run log, so those causes stop leaving the same
trace, which is none. `off-host` is the one per-document reason that is not an upstream failing
to serve and is not repaired by re-attempting it; where it is the failure that
emptied or shortened an opposition, the case-level reason beside it inherits
that irreparability. `bio-partial` is the reason whose case still ends the pass
holding a `brief-in-opposition` row: some of a multi-respondent case's
selected opposition briefs fetched and some did not, so the
row exists and carries less than the docket's opposition, where `bio-empty`
writes no row this pass at all. It is counted at the outcome grain
because the per-document reason that shortened the row cannot say a row was
stored anyway, and it wants a maintainer's reading for the same
reason the back-fill gap class does: the short set heals only at the case's
**next provisioning fetch**, and the triggers for one are finite. Provisioning
fires on a distribution transition — a fresh distribution or a relist — and in
the cycle-end salience sweep while some enabled predictor is still owed a cell
on the case; the stored key records the briefs actually fetched, so it never
matches the selected set and the next such fetch re-tries the missing brief. A
case that takes no further transition and owes no further cell keeps the short
row, and `brief-in-opposition` is not a back-fill gap kind, so the repair pass
reaches it only incidentally — when the case is a candidate for some other
missing kind and the apply runs the whole selector over its payload.
**Every request the fetching client
makes is HTTPS on a supremecourt.gov host, and it enforces that rather than
assuming it**: a `DocumentUrl` is upstream text lifted verbatim out of docket
JSON and a `Location` header is upstream text too, so the client checks the URL
a fetch starts at, then walks any redirect chain hop by hop, refusing the first
one that leaves the host **before** making that request. Checking after httpx
had followed the chain would be too late — the bytes a document fetch returns
are stored and read by a cell as evidence, and the politeness pacing and the 403
retry posture are keyed to the intended host — so a single occurrence is worth a
maintainer's reading. (The reachability probe below keeps its own client, which
follows a redirect wherever it leads: it builds its own URLs and writes nothing
to the corpus, so where a body came from cannot enter the record.) A sixth
reason sits one step earlier and is the one loss those five cannot see:
`not-selected`, recorded per case where the docket JSON nominated no document,
so the class an upstream that publishes no PDF (a Rule 34.6 paper
filing) and a selector with no arm for the filing type both land in is counted
rather than silent.
**Both lanes that fetch for a case a cell can still be minted over report the
counts, not just the one that repairs.** A
counter and a `logger.warning` die with the runner, so a reason recorded and
never reported is a loss that happened and left nothing: `live-poll` — where the
ordinary provisioning fetch happens, and therefore where most of these losses
are incurred — closes each window with the whole reason
set, zero-filled, on stdout, plus a `::warning::` and a Markdown block on the
Actions step summary whenever the window lost anything; the document back-fill
prints the same set as its apply's ledger (`backfill-documents`, whose dry run
fetches no filings, so its copy of the ledger is structurally zero). The two
surfaces render
from one keying on the record itself, so a reason added to it reaches both or
neither. The per-document detail — which case, which link, and for `bio-partial`
how many briefs were selected against how many fetched — stays in the
`documents:` warnings; the summary carries the count, what the reason means, and
where that detail is. The **historical walker** is the third lane that fetches
(`historical-terms`, for ingested Terms from `document_floor_term` onward) and
the one that reports none of it: it records into the same counter and its run
report carries no ledger. That is a known residue rather than a claim about it —
every row it ingests lands already resolved, so a brief lost there costs a
replay cell's input and never a forecast, and no sweep re-fetches it.
**The questions presented
are derived from the petition PDF, never from `QPLink`:** the `/qp/` page is
generated when certiorari is *granted* and opens with the grant order, so the
key is an outcome artifact — it is also stripped by replay redaction for the
same reason (verified live at implementation).

### How large the degradation is, and what is done about it

Measured on the blob the corpus pointer named on 2026-08-28 (`b16b856f…` — the
pointer is a content digest, which `corpus-info` does not print; its freshness
pair is a 2026-08-28 pull stamp and a 2026-07-13 newest stored snapshot, and
the documents were served by the per-case content store). Every figure below
taken over the queued population is on the **stamp-only** denominator — the
rows carrying a `predict_queued_at` — which is what the report counted at the
time. It now counts the union of that with the cases the git ledger holds a
committed prediction for, because a schedule-derived mint leaves no stamp, so a
re-run today reports a wider denominator than these numbers were taken over. Of the 9,231 stored
petitions, 271 carry no text: **2.94%** over both segments pooled, and **2.90%**
(192 of 6,613) over the cut the salience gate scores replay candidates on.
Those are stored documents, not cells. On the 242 cases queued for prediction —
where a missing petition costs a forward cell — **6** hold a petition that read
back empty, which the report did not print but its case-id ledger gave when
intersected with the rows carrying a `predict_queued_at` (the reconstruction
that the widened denominator retires: it is the ledger's predicted set the
count now also spans). Of the 271, 270 have
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
wider stock of distributed rows nothing was ever fetched for. That 29 is
undifferentiated, and the report is not: it measures each docket form against
the document that opens it, counts the two classes apart and enumerates both,
so a read of the same population prints a cert-form gap, an application-form
gap, and the case ids in each. No extraction fix reaches any of them; that is a
fetch question, and the document back-fill contracted below is the fetch-path
answer to it — bounded, form-keyed, and reporting apart the part of the class no
fetch reaches. The report draws that second line itself, beside each gap: of the
cases in it, how many hold a stored docket carrying the opening entry with **no
document behind it**, which is a paper filing the Court posted no PDF for and a
structural floor. The rest is what the back-fill drains, so the headline stops
reading as an unexplained provisioning gap the moment it has been worked. A case
matching *no* opening entry is deliberately outside that floor and stays in the
unexplained remainder — on a modern docket it is a filing shape the selector
cannot see, which is a defect to fix rather than a floor to accept, and the
back-fill's own ledger names those cases.

So the scanned class is small on every population, and on this blob it is a
bounded 270 petitions and 34 briefs in opposition, each named in the report's
case-id ledger alongside the other kinds' empties. Six of the 271 empty
petitions sit on cases queued for prediction today; the rest pay off wherever
the gate later mints a cell over them. And the
degradation persists where it lands: a filing that reached the corpus as a
scan is unreadable for every cell minted over that case until it is
re-fetched at a new URL, and no other path repairs it. What it costs differs by
kind and the repair does not: an empty opposition leaves a cert cell with the
respondent's whole argument missing, which is the half of the case a forecast
is least able to guess, while the fetch and the recognition are the same work
on either. The decision is therefore a **bounded local-OCR recovery pass** over
the empty rows of every *fetched* kind, contracted below. Local tesseract only — at this share a metered OCR service
cannot be justified, and the pass's own cost is held down by the per-dispatch
bound in the contract rather than by a service bill.

Three residuals stay open by design. The unopenable PDF is not OCR's to repair
and stays counted as empty. A multi-respondent brief in opposition stays out
for a structural reason rather than its share: it is stored as one combined row
whose URL is the canonical join of every brief fetched into it, which is an
idempotency key and not a link to GET — recovering it would mean re-fetching
and re-combining a set, which is the fetching lane's work, not this pass's —
and text recovered there would in any case be discarded the next time a
co-respondent's brief joined that key. A lone opposition joins to itself, so it
stores one link and is recovered like any other filing. What that leaves
unsized is the combined row itself: its per-brief headings are text, so a
multi-respondent opposition of nothing but scans is not empty by the coverage
report's test and reads there as *covered* while carrying no argument at all —
and it is outside this pass on top of that. Neither surface counts it, and the
pass's `set_keyed` tally is the guard against a set key that somehow did read
empty rather than a measurement of the residual. And recurrence: a scanned filing
that arrives after a pass enters the class and stays there until the next one.
Nothing watches for that on its own — the same `corpus-info --text-coverage`
read is what sizes it, and the pass is re-runnable over whatever it finds — so
cadence is a dispatch decision taken against a measured share, not a schedule.

### Contract for the recovery pass

What the pass holds to. It is `fedcourts ocr-recover-petitions`, dispatched as
`run-repair`'s `ocr-recovery` selector value, whose step installs its two
binaries: tesseract, and poppler's `pdftoppm` for the page raster it reads —
shelled to the same way, so the pass adds no Python dependency on either side.

- **Where it runs.** As a pass on `run-repair` — a `repair` selector value, not
  a workflow of its own. The writer jobs are the only place a production corpus
  write can happen, and a pass whose dry run is a triage list a maintainer reads
  before an apply belongs on the bench by the standing rule (*Five writer jobs,
  one shared core* and *Maintenance passes* in
  [data-pipeline.md](data-pipeline.md)): it writes the corpus, which only a
  writer job may, and its dry run is exactly the triage list that bench exists
  for. It is one of the two passes there that fetch — the document back-fill
  below is the other — and the fetch is what keeps them in that lane rather than
  the pullers': supremecourt.gov is free and politeness-capped, so no budget is
  governed and no window's schedule is implicated. Both binaries are installed by that step alone, so no scheduled
  lane grows the dependency. Dry run by
  default, and bounded through `repair_bound` so a backlog clears in slices
  rather than in one long job; runner minutes are the whole cost. That bound is
  the *spend* cap. What keeps a slice inside the step's own wall clock is a
  **slice deadline** the step passes with it, sized from everything that must
  still fit inside that cap once the pass stops taking work — the writes it has
  in flight, the witness re-read, the blob push and the pointer commit. Before
  each candidate the pass estimates its cost from the stored page count and
  stops taking new ones once what is left will not hold it. Page counts across
  the class vary several-fold, so a fixed bound cannot do that job — a slice
  that draws three long filings is the same dispatch as one that draws three
  short ones. The estimate is a high reading of the ordinary cost rather than a
  ceiling on the possible one, so the step's cap stays the backstop for what
  runs past it.
- **What it reads.** Stored rows of a **fetched** kind — every kind a cell
  reads that arrived as a PDF: the petition, the application, the brief in
  opposition and the four merits filings, which is the text-coverage set less
  its one derived member — whose text is empty or whitespace-only, whose page
  count is above zero, and whose stored URL is one link. A zero-page row is
  either a PDF the extractor could not open or a derived section — `pages`
  carries both — and neither is OCR's to repair; a case holding no row of a
  kind is a fetch gap, or on an application docket no gap at all; a row whose
  URL is a set key is the multi-respondent opposition above. All three stay out
  of the population. The kinds differ in what a cell
  loses when one reads empty and in nothing the pass does: each is one stored
  row, one link, one re-fetch, one recognition. The coverage report's case-id
  ledger names the kinds that read back empty but not their page counts, so the
  pass re-derives that filter itself. The PDF is re-fetched by the row's stored
  URL — the single link that was fetched: supremecourt.gov, free and
  politeness-capped, so the pass spends none of the CourtListener budget. The
  population is walked case by case rather than
  queried, because under the corpus split the document text lives in the content
  store and the blob's `documents` table holds none of it — a SQL predicate over
  that table reports an empty class against the corpus production reads.
- **What its dry run also reads.** A sample of the population, three by default
  and spread evenly across it rather than taken off the head, so successive dry
  runs do not report the same three URLs — re-fetched through the writer's own
  fetch path — the same client,
  headers and retry posture the fetching lanes use — with each GET's status
  reported and nothing kept. The apply's whole premise is that supremecourt.gov
  serves a writer, and a cell's report of a 403 is evidence about a cell's fetch
  path, not this one; making the dry run answer it is what keeps a slice from
  being the experiment. Every status class is reported rather than raised, or
  the question would be settled on one data point.
- **What it does.** Walks the PDF's pages as the extractor does and OCRs a page
  **only** where that page's own text extraction yields nothing — a guard rather
  than a filter, since the population is documents that yielded nothing at all,
  but it keeps a mostly-digital filing with a few scanned exhibit pages honest.
  It is the extractor that walks them: `extract_pdf_text` takes the OCR call as
  an injected `ocr_page` seam, defaulted to none, so this pass is the only
  caller that supplies one and no fetching lane grows the dependency —
  and the same per-document text cap the fetching lane applies and the same
  truncation flag bound the result, because they are the same code. A recovered
  row is bounded exactly like a fetched one. Additive by construction: text
  is written only where extraction stored none, so the pass cannot overwrite an
  extraction. Nor is a recovery overwritten later — the row keeps its URL, and
  both the poller and the Term walker re-fetch a kind only when its link
  changes; a genuinely superseding filing at a new URL is re-fetched and, if
  it too is a scan, re-enters the class. A lone opposition recovered here is
  re-fetched and re-extracted the day a co-respondent's brief joins its key,
  which is the same rule reaching the same row: what survives a recovery is
  what the fetching lane has no reason to re-read. A candidate whose re-fetch fails, and
  one whose pages OCR to nothing, are counted and named and nothing is written
  for either: the stored row keeps its empty text, stays in the class, and
  re-enters the next slice. Neither is the pass going backwards, but neither
  advances it either, and both sit at the *head* of the class in `case_id`
  order, so the next dispatch retries them first: "self-advancing" means the
  recovered ones leave, not that a later slice starts further along. The ledger
  reports them apart from the candidates a slice never reached for exactly that
  reason — a class whose head is permanently unreadable makes a small bound a
  no-op, and the ledger is what shows it. The candidates a slice never reached
  are named there too, one by one, because the slice deadline is what leaves
  them: unreached is not failed, and a maintainer reading the ledger should see
  which of the two a dispatch produced. Three bounds keep one filing from
  costing the rest: a stored
  URL is refused unless it is HTTPS on the Court's own host (`DocumentUrl` is
  upstream text, and this pass is the only thing that GETs one back), a body
  past a size ceiling is refused as not-a-filing, and a document that outlives
  its recognition budget is abandoned unread — each costing its own candidate,
  which stays in the class. The slice deadline is the fourth and the only one
  above the filing: it costs no candidate at all, since it declines before the
  fetch. Each recovery is written as it is made rather than
  batched at the end, so a step that hits its wall-clock cap has banked what it
  recovered — under the corpus split, where the content-store write is itself
  the durable one; on a self-contained blob the pointer push at the end of the
  step is, and a cap hit loses the slice however it was written.
- **What it records.** OCR output is *derived* text, lossy in a way pypdf output
  is not, so it must never read as a clean extraction. `CaseDocument.ocr_derived`
  is that marker: one flag per stored document, true where **any** of its text
  was read off a page image rather than out of the PDF's text layer. Per
  document rather than per page, because that is the unit a reader is handed —
  the flag tells a cell how to read the text it has, and a page-level ledger
  would say where a misreading is possible without making it locatable in the
  one string the cell holds. It rides three storage surfaces before
  provisioning, because a document crosses that many boundaries: the model; the
  `documents` column, with a constant default and `_migrate_documents` to
  back-fill an older blob — one DDL map drives both that migration and the
  writer's bound column list, so a column the writer binds cannot miss the
  migration; and the content-store manifest writer *and* reader, which serialize
  a document field by field — a field written on one side only reads back at its
  default on the offloaded path, which is the path production reads. Both
  readers tolerate what predates the marker rather than failing on it: a
  manifest without the key reads as an extraction, and the row read selects
  every column rather than naming this one, because the ranged backend serves a
  remote blob as-is and cannot be migrated — naming a column the blob predates
  would fail the whole document set rather than the one field. Provisioning then
  carries the whole row minus its text onto the cell manifest, so the marker
  lands beside `empty_text`. Still outstanding: the predict prompt's reading
  rule, which pairs with the manifest key — a bare key teaches an agent nothing
  — and moves the pre-registered prompt digest, so it rides a re-bless; and the
  coverage read's count of what was repaired. **A second reading rule rides the
  same re-bless**, for the same reason and with the same shape: an interim cell
  is now provisioned with `application.txt` — the text of the very filing it is
  forecasting on — while the prompt's interim section tells it to read the
  escalation ladder off the docket and says nothing about the document. The
  input arrives before the instruction does, which is the argument for pairing
  them on the next bless rather than letting either land alone. **A third rides
  with them**: the contact scrub stages text carrying
  `[contact detail withheld]` and three manifest keys (`contact_scrubbed`,
  `contact_replacements`, `contact_scrub_passes`) the prompt describes none
  of — it has `documents.json` listing what is present, pages and truncation —
  so until that re-bless a cell meeting the token has to account for it
  unaided, and the likeliest cost is a `data-quality` flag spent on it. **A
  fourth rides with them**: the `appendix`, `cert-reply` and `sg-invited-brief`
  kinds and the appendix-aware cut's `[pipeline note: …]` lines reach a cell
  before the prompt names them. Each manifest row's `kind_description` is what
  carries them meanwhile — the prompt already sends a cell to `documents.json`
  for what is present — and the prompt's list of provisioned files gains the
  three kinds, and a reading rule for the cut notes, at that re-bless.
- **What follows a recovery.** A recovered **petition** re-derives its
  questions-presented row through the existing deriver — the pass's one
  follow-on write, and petitions alone have it, since no other recoverable kind
  carries a questions-presented section — in the same write rather
  than a second dispatch — the ingest path derives it inline for the same
  reason, and a row left behind until someone remembers the backfill is a
  petition whose questions read as absent — since such a row is
  written only where the petition has text. On OCR text that derivation keeps
  the two outcomes it has now: no recognizable heading stores no row at all,
  and a heading whose capture the deriver will not vouch for stores the empty
  row. The derived row carries the petition's marker, on both the ingest and
  the backfill path: text cut out of an OCR reading is an OCR reading. One
  refusal rides with it, the convergence sweep's in a stricter form: an empty
  derivation never replaces a *stored* question, at any length rather than the
  sweep's character floor. A question stored beside a scanned petition came from
  a superseded filing, and emptying it is as likely to be this pass misjudging
  as a bad row — and unlike the sweep, whose whole subject is the derived row,
  this pass is here for the filing and has no business deciding that one. The
  recovered row's fetch date moves to the day it
  was re-fetched, because a fetch happened, and that is visible in one place
  downstream — provisioning places a document by its entry date and falls back
  to the fetch date where there is none, so such a row can fall outside a
  replay cell's window it previously sat inside. A cell then sees less, never
  more, which is why the honest date is the one kept.
- **Terms.** Unchanged. These are the Court's own public records, and OCR text
  lands in the access-gated corpus under the same no-republication posture as
  every other extraction ([data-sources.md](data-sources.md)).

### Contract for the document back-fill pass

The answer to the other half of the gap above — the queued cases holding a
document gap at all, which is a fetch question and repaired in the fetch
path or not at all. It is `fedcourts backfill-documents`, dispatched as
`run-repair`'s `document-backfill` selector value. It installs nothing: the
route is the provisioning path the live poller already runs, re-keyed off the
corpus row rather than off a poll.

- **Where it runs.** As a pass on `run-repair`, by the same standing rule the
  recovery pass above cites, and for the same two reasons: it writes the corpus,
  which only a writer job may, and its dry run is exactly the triage list that
  bench exists for. It is the second fetching pass there, and its fetches are
  the same free, politeness-capped supremecourt.gov requests — no budget is
  governed and no window's schedule is implicated. Dry run by default, bounded
  through `repair_bound` so a backlog clears in slices, and bounded again by a
  **slice deadline** the step passes, sized from everything that must still fit
  inside the step's cap once the pass stops taking work. The bound applies to
  the dry run as well, which is the one way this pass's contract differs from
  the recovery's: its dry run is not free.
- **What it reads.** Live-slice SCOTUS rows that are **predict-relevant** —
  queued for prediction, or selected by the salience gate and not yet queued.
  The selected arm is not redundant — a reserve-selected application has no
  distribution transition to be queued at and reaches the predict path through
  the selection sweep. Predict-relevant rather than the wide distributed stock,
  which is overwhelmingly pre-modern rows carrying no document links at all:
  each candidate costs paced round trips, and the rows that can mint a cell are
  the ones worth spending them on.

  Each such row is measured on **two arms**, and is one candidate for every kind
  it is missing. The **primary** arm reads its own docket form's opening
  document — form-keyed rather than petition-keyed, because an application
  docket structurally never holds a petition and a petition-keyed predicate
  would strand every application in the class forever and spend the bound on
  cases no fetch can drain. The **merits** arm reads each side's brief on the
  merits, and applies only to a **granted** row whose respondent has *filed* on
  the merits: granted-and-briefed rather than granted alone is what makes it
  drain, since a granted row carrying no briefing date has nothing for a fetch
  to find. The merits **replies** are deliberately not gap kinds — not every
  granted case is replied to, so keying the class on one would hold every
  un-replied case in it forever — but a reply the docket carries is fetched with
  the rest.
- **What it fetches.** One docket JSON per candidate, addressed by the
  `(term, serial)` its stored docket number parses to, and fetched **fresh**
  rather than read from the stored snapshot — the question is whether the link
  is served *now*, and a stored payload can name a URL upstream has since
  withdrawn or predate the filing entirely. The dry run stops there and fetches
  no filings: running selection over that payload is the whole diagnostic, since
  it is what separates a case with a link waiting for it from one at a floor.
  The apply goes on through the same fetch the poller runs, so a recovered case
  is provisioned on exactly the terms a case provisioned at its trigger was —
  the opposition briefs and the derived questions-presented row land with the
  primary filing, and a merits reply lands with the merits briefs. A
  consolidated member missing a merits kind costs one more docket GET in either
  mode, for its lead's JSON, since its merits briefs are entered there (see *Consolidated members*
  above). Recovery is
  **leaving the class**, so a candidate that gained one of two missing merits
  briefs is a write and not a recovery, and stays at the head of the next slice.
- **What it reports as a floor rather than a failure.** Two readings, and
  keeping them apart is what stops a converged class reading as a permanent
  defect. A docket carrying an entry for a missing kind with **nothing
  fetchable** behind it is at the first floor: a Rule 34.6 paper filing the
  Court served nothing for, or — on a merits kind — a grant this reader cannot
  date, so the selector's stage bound places no entry on the merits side of it.
  A docket carrying **no such entry** for any missing kind is a legacy
  proceedings list holding no document links. The two counts are per candidate
  and partition the floored ones. Neither drains, so neither is re-walked: an
  **apply** stamps the candidate it read at a floor (`document_floor_probed_at`
  on the corpus row) and the class holds it out while that stamp is no older
  than `last_live_polled`, the live channel's own record of when it last read
  the same docket. A floor is then paid for once per docket version rather than
  once per dispatch, which is what lets a bounded slice reach the tail of a
  class whose recoverable head has drained. `standing_floors` on the ledger is
  the held-out balance, so the whole addressable class is still readable from
  one run.

  The **alarm** cuts across both counts, because it is per *kind*: a missing
  kind the selector found no entry for, on a docket modern enough to carry
  links, is a filing shape the selector has no arm for — the class this pass
  exists to stop producing — and those cases are **named** whichever floor they
  were counted at, so a granted case whose merits entries are on the docket and
  whose opening filing is unreadable is not silenced by the kind that matched.
  On a consolidated member the lead's entries count as the member's for this
  test, so a member whose briefs are on a lead the fetch served is a recovery
  or a floor, not an alarm — the floor where the lead lends nothing (every
  entry another docket's, or dated before the member's grant). A lead the fetch
  did not return is counted with the docket losses (`docket_unserved`,
  `docket_errors`), unstamped, so the member is retried.
  A floor the alarm fired on is also the one floor that is **never stamped**: it
  is a reading about this pass rather than about the docket, so holding the case
  out would bank an exclusion over a defect on our own side — and it is the
  shape an upstream payload that changed or degraded would take across a whole
  slice. Those candidates keep their place, and widening the selector recovers
  them.
- **What it writes.** Each case's documents as they are made rather than batched
  at the end, so a step that hits its cap has banked what it recovered — under
  the corpus split the per-case content-store write is itself the durable one.
  Additive by construction: the fetch is idempotent against the stored
  `(kind, url)` mapping, so a case already holding a document at the selected
  URL is not re-fetched and nothing it touches loses what it had. What re-enters
  the next slice depends on why a case did not recover: one whose docket or
  filing the fetch did not return keeps its place at the head of the class,
  while an applied floor is stamped out of it until its docket is polled again.
  The stamps are the pass's one **index** write — a column, through a direct
  `UPDATE`, so a row hydrated from the payload-free index can never re-mirror a
  body-less `case.json` over a stored opinion — and they are durable only once
  the lane pushes the blob, where the documents are already banked per case.
  Because the documents' durable write is the content store's rather than the
  pointer's, the step re-walks the class afterwards on an **empty slice** —
  which costs no round trip — and requires exactly what the apply's ledger said
  it would leave behind.
- **Terms.** Unchanged. These filings are the Court's own public records, fetched
  from the Court's own host, and their text lands in the access-gated corpus
  under the same no-republication posture as every other extraction
  ([data-sources.md](data-sources.md)).

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
inclusion probability** as `sample_weight` — 1 where the corpus can show the row
stands only for itself, min-latched so a weight can only ever be learned toward
certainty. The column stays because the corpus still holds denials an earlier
sampled walk kept at weight 10: a weighted aggregate multiplies by it so that
legacy frame cannot bias a base rate, and each such row regresses to 1 once a
re-walk has **enumerated its block**, so that the nine petitions the weight stood
for arrive with it. Regressing it on the re-serve of the kept serial alone would
leave those nine represented by nobody, which under-counts that block's denials
rather than over-counting them.

**So a channel does not get to assert the certainty; it is checked.** Every
live-channel write that lands a SCOTUS payload — frontier discovery, the cert
and application rotations, the selection sweep, and the walker's own ingest —
reaches the corpus through `ingest_live_payload`, and a caller asserting weight
1 there has that assertion re-derived through `legacy_denial_sample_weight`
(density guard included) before it is written. (The rotations also write bare
poll stamps directly, but each re-upserts the row it read, so it echoes the
stored weight and can never lower one.) Touching a row is not observing the
block it stands for: a grid denial whose neighbours are still stored one in ten
keeps its sampling weight however many times the walk re-serves it alone. That
is what makes a re-weighting of the legacy frame durable — the min-latch keeps
the smaller of stored and incoming, so a repaired 10 would otherwise be erased
by the next re-serve's 1. A caller asserting any weight *other* than 1 is
claiming knowledge the corpus cannot reproduce, and that value is written as
given. The derivation is affordable per row because the density guard's read of
the live slice is served by `idx_cases_live_docket`, a covering partial index
over exactly that slice; every other outcome is settled on the row's own columns
and one cursor lookup.

Weights land exactly at ingest time; the backfill for pre-capture rows recovers
them by the same rule (`legacy_denial_sample_weight`: denied + serial on the
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
history must never feed forward prediction: the loader writes **no queue files
at all**, records with no readable disposition are skipped (pending
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
