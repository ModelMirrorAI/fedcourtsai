# Corpus — the unified raw-fact store

All *raw facts* live in the corpus: dockets, dated snapshots, judges, case
metadata and tracking state, and event definitions — written identically by
every ingestion channel through the shared seam in
[`fedcourtsai.corpus`](../src/fedcourtsai/corpus.py). Derived judgments live in
the git ledger under [`data/`](../data), not here (see the *Data model* section
of the [README](../README.md); pipeline design:
[docs/data-pipeline.md](../docs/data-pipeline.md)). This page is the store
internals and developer access.

## Format and tracking

The corpus has two halves:

- **The index** — a single **SQLite** database, `corpus/corpus.db`: the blob
  lives in the corpus remote (a private S3 bucket) at a content-addressed,
  add-only key and only the small `corpus.db.ref` pointer (key + size +
  sha256 + schema version; see
  [`fedcourtsai.corpus_remote`](../src/fedcourtsai/corpus_remote.py))
  is committed to git (the blob and its
  sidecars are gitignored). Every push adds a version and none is ever removed,
  so any commit's pointer stays pullable — the retention contract and the
  storage-class rule that pays for it are *Index retention: keep every version*
  in [docs/data-pipeline.md](../docs/data-pipeline.md). Under the corpus-split
  mode — an environment with the per-case content store configured — the
  writers keep it **payload-free**: the `snapshots`/`documents` tables stay empty and
  `cases.opinion_text` stays NULL (a `has_opinion` presence bit is retained),
  so the blob stays a small metadata index and its per-run push does not
  grow with the bulk. With no store configured (dev environments, the
  fixture loop, offline tests) the same schema holds the payloads inline in a
  single self-contained blob, the opinion record's writings' text aside, which
  is kept only in a store (`opinion_texts`, below).
- **The per-case content store** ([`fedcourtsai.casestore`](../src/fedcourtsai/casestore.py))
  — a browsable, write-once, access-gated S3 store holding the bulk payloads,
  keyed to mirror the ledger's `data/cases/<court>/<docket>/` shape:

  ```
  <court>/<docket_id>/
    case.json                                    # the CorpusRow
    events.json                                  # the case's events
    snapshots/<YYYY-MM-DD>.json                  # dated point-in-time docket payload
    documents/documents.json                     # manifest: kind -> current text leaf
    documents/<kind>/<YYYY-MM-DD>-<digest>.txt   # extracted text (content-addressed)
  scotus/opinions/OT<term>/<listing>-<digest>.json  # one opinion document's writings
  ```

  The last line is keyed by the Court's opinions listing rather than by case,
  since one document can decide several dockets; the per-opinion record's
  `opinion_texts` row points at it.

  A corpus write mirrors to production's store only inside a GitHub Actions
  job and only from the configured corpus file — and only production's writer
  jobs hold a role that may write there — so a local writer run or a temporary database never
  reaches the store (see [docs/data-pipeline.md](../docs/data-pipeline.md)).
  Document text leaves are content-addressed and dated snapshots immutable per
  day, so bulk content is never overwritten in place; the small manifests are
  versioned by the bucket rather than deleted. The `questions-presented` leaf is
  *derived* from the stored petition text rather than fetched, so a fixed
  extractor can be carried onto rows already stored (`fedcourts
  backfill-questions-presented`) under that same rule: the re-derivation writes
  a new leaf and re-points the manifest, and the superseded text stays
  readable. Its address is the casestore segment under the environment's
  corpus base URL ([`fedcourtsai.paths`](../src/fedcourtsai/paths.py)), or a
  content-store URL named on its own.

SQLite keeps the index a single artifact — one pointer, queryable with
plain SQL. The format is internal; the stable contract is the **row schema**
below, whose identifiers and `Disposition` vocabulary are shared with the
ledger models in `fedcourtsai.schemas`.

## Row schema (`cases`)

Each row is a normalized, **labeled** record. It carries the realized
`disposition`, so the corpus doubles as a back-testing set and a retrieval
source.

| Column                | Type            | Notes                                        |
|-----------------------|-----------------|----------------------------------------------|
| `case_id`             | text (PK)       | `<court_id>/<docket_id>`                      |
| `court`               | text            | CourtListener court id                        |
| `docket_number`       | text            | the docket's number as upstream spells it, less the `*** CAPITAL CASE ***` marking the Court appends to some SCOTUS numbers, which ingest strips so the readers that parse the number can see it (the marking is preserved on `capital_case`). Matched by its words, not by the `*** … ***` shape — a consolidated circuit docket uses the asterisks as a separator, and a shape match would delete a whole number out of the column |
| `case_name`           | text            | case caption, e.g. `Doe v. Roe` (both ingestion paths) |
| `petitioner_title`    | text            | the petitioner's structured caption (supremecourt.gov `PetitionerTitle`, role suffix stripped; live channel only, fill-in latched) — the arrival-time party-class reading (`pipeline.caption`) |
| `date_filed`          | date            |                                              |
| `date_decided`        | date            | docket-level termination date. On a SCOTUS petition it takes the cert denial's date, since the order refusing the writ is the order that ends the docket; on a grant it stays null until the merits judgment (`date_cert_granted` is the petition's resolution, not the case's) |
| `disposition`         | text            | realized outcome label; null while unresolved |
| `judges`              | json array      | judge names (flat retrieval key)             |
| `panel`               | json array      | structured panel: `{name, seniority}` per judge |
| `parties`             | json array      | party names on the docket                     |
| `attorneys`           | json array      | attorney names of record                      |
| `counsel`             | json array      | structured counsel: `{party, attorney, role, counsel_of_record}` per docket block; `role` is the caption side (petitioner / respondent / other). SCOTUS live+historical only; latched — an empty incoming list keeps the stored one, a non-empty reading replaces it |
| `topic`               | text            | nature of suit / subject-matter topic         |
| `citations`           | json array      | reporter cites (`602 U.S. 137`), from the docket's opinion cluster |
| `citation_count`      | integer         | times the decision has been cited            |
| `precedential_status` | text            | Published / Unpublished / Errata             |
| `opinion_text`        | text            | opinion body — NULL under the split mode (the content store holds it; `has_opinion` retains the presence signal) |
| `summary`             | text            | short form for retrieval; the normalizer never folds an opinion body into it (that has its own column), though a stored row whose source served the body here keeps it until a re-serve |
| `last_pulled`         | date            | tracking state: when `pull` last refreshed it |
| `predict_eligible`    | integer (0/1)   | derived mirror of the prediction scope (`court == scotus`); see below |
| `predict_excluded`    | integer (0/1)   | out-of-scope latch, owned by the scope reconcile |
| `originating_court`        | text       | lower court this docket came from (`appeal_from`) |
| `originating_docket_number`| text       | docket number in the originating court (REST-only) |
| `date_cert_granted`   | date            | petition-stage cert grant date (SCOTUS)       |
| `date_cert_denied`    | date            | petition-stage cert denial date (SCOTUS)      |
| `last_live_polled`    | date            | tracking state: when the live channel last polled it |
| `distributed_for_conference` | date     | the conference this petition is currently distributed for (live-parsed) |
| `distribution_count`  | integer         | distinct conferences distributed for (relists = count − 1, floored at 0); null = never live-parsed, 0 = parsed, never distributed |
| `cvsg_date`           | date            | when the Court called for the views of the Solicitor General (live-parsed) |
| `call_for_response_at` | date          | when the Court called for a response to a cert petition — the first `Response Requested` entry before any disposition (`pipeline.cert_signals.call_for_response_date`); opens the cert call-for-response moment; distinct from `response_requested_at`, the interim request on an application; written by the live poll at ingest and filled on the rows it no longer polls by `run-repair`'s `salience-cert-backfill` pass, fill-in latched; withheld from the `query` retrieval rows; null = no call yet, or not parsed |
| `relisted_at` | date | when the Court first relisted a cert petition — the first petition distribution for a later conference, docketed within two weeks after the earlier conference sat on the petition, before any disposition (`pipeline.cert_signals.first_relist_date`); opens the cert relist moment, once per petition; narrower than the relist count `distribution_count − 1`, which also counts a reschedule; written by the live poll at ingest, fill-in latched; withheld from the `query` retrieval rows; null = no relist yet, or not parsed |
| `distributed_after_call` | integer | how many conferences a cert petition was first distributed for after the Court called for a response (`pipeline.cert_signals.distributions_after_call`): distinct conference dates named by petition distributions (the `dist-v2` reading `distribution_count` holds) filed after the first call, less any a distribution filed on or before the call, or undated, also names; the `sal-v5` relist count's input; written by the live poll's cert branch at ingest, fill-in latched; withheld from the `query` retrieval rows; null = no dated call for response, or not parsed — on a row the poll has not read since the column existed, until `run-repair`'s `salience-cert-backfill` pass (`fedcourts backfill-salience-cert-columns`) reads its stored snapshot |
| `opening_writ` | text | the writ a cert-form docket's opening "Petition for a writ of … filed" entry names, read past an extension application (`pipeline.cert_signals.opening_writ`): `certiorari` (certiorari before judgment included), `rule-20` (mandamus, prohibition or habeas corpus, and no certiorari), `ambiguous` (both) or `other` (neither); classified by the entry text, never by an "In re" caption, which a sealed certiorari petition carries too; the `sal-v5` scope input (`corpus.is_rule_20_writ`); written by the live poll's cert branch at ingest, fill-in latched; withheld from the `query` retrieval rows; null = no opening petition entry disclosed, or not parsed — on a row the poll has not read since the column existed, until `run-repair`'s `salience-cert-backfill` pass (`fedcourts backfill-salience-cert-columns`) reads its stored snapshot |
| `merits_brief_on_lead` | date | a consolidated member's own respondent brief on the merits as filed on the group's lead docket — the first lead entry after both the member's grant and the lead's that the member attribution reads as filed for it (`pipeline.documents.member_respondent_brief_date`); consolidation moves the member's later filings to the lead, so its own `merits_brief_filed` stays null; written by the live poll from the lead's newest stored live snapshot (no request), fill-in latched; read by no mint (the briefed moment still opens on `merits_brief_filed` alone); withheld from the `query` retrieval rows; null = not a consolidated member, not yet filed, the lead not stored, or a member that left the poll rotation before the column existed |
| `argument_transcript_at` | date | the argument day of the first oral argument transcript stored for the docket — the date the Court's per-Term transcript list gives beside the transcript link (`supremecourt.parse_transcript_listing`); opens the merits post-argument moment; written by the live poll's transcript pass (`pipeline.live.fetch_argument_transcripts`) when the transcript it stores carries text, fill-in latched, so a reargument never moves it; withheld from the `query` retrieval rows; null = not argued, no transcript listed yet, or not read |
| `sg_brief_filed`      | date            | when the Solicitor General filed the brief the CVSG invited — the first United States amicus brief after the invitation and before any disposition (`pipeline.cert_signals.sg_brief_date`); opens the cert sg-brief moment; written by the live poll at ingest, fill-in latched; withheld from the `query` retrieval rows; null = not yet filed, or not parsed |
| `originating_court_name` | text         | raw `LowerCourt` name — keeps state courts identifiable where `originating_court` is null |
| `sample_weight`       | integer         | inverse inclusion probability (1 where the corpus can show the row stands only for itself; 10 on a denial the earlier sampled walk kept whose block is still stored one row in ten); null = no channel weighted the row |
| `has_opinion`         | integer (0/1)   | presence bit for a linked published opinion — kept in the index so the scope classifiers still work when the split moves the `opinion_text` body to the content store |
| `salience_score`      | real            | the salience gate's deterministic score ([docs/salience.md](../docs/salience.md)); owned by the selection pass, never an ingestion channel |
| `salience_version`    | text            | the frozen scorer version the score was written under; null = unscored row |
| `salience_selected`   | integer (0/1)   | the one-way selection latch — a selected petition is never de-selected |
| `predict_queued_at`   | date            | the last date the live channel queued predict for this case (routing or selection sweep); the sweep's daily-retry debounce reads it |
| `evaluate_queued_at`  | date            | the last date any caller stamped the case at the evaluate seam; the deriver's daily debounce reads it — no standing lane writes it |
| `application_kind`    | text            | what an interim application asks for (`extension` / `substantive` / `unknown`); null = never application-parsed |
| `response_requested`  | integer (0/1)   | the Court requested a response to an interim application (the interim CVSG-analogue); null = never application-parsed |
| `referred_to_court`   | integer (0/1)   | the application was referred to the full Court rather than a Circuit Justice alone; null = never application-parsed |
| `amicus_briefs`       | integer         | amicus briefs on an interim application's docket — one per accepted-form entry, plus each distinct lead filer whose brief is still docketed as submitted; on a resolved application the *derivation* stops at the end of the disposition day, but the column max-latches, so a row polled before that date was readable keeps its unbounded value until a re-derivation; null = never application-parsed |
| `cert_amicus_briefs`  | integer         | amicus briefs on a cert petition's docket before its first disposition entry, in docket order (`pipeline.cert_amicus.cert_amicus_briefs`) — the interim count's per-entry reading over the cert stage, less the Court's orders on amicus motions, so a granted case's merits amici never reach it and a brief filed by motion counts once; written by the live poll's cert branch at ingest and filled on the rows it no longer polls by `run-repair`'s `cert-amicus-rederive` pass (`fedcourts rederive-cert-amicus-briefs`, the same count over each row's latest live snapshot), both under the max latch (the cut fixes a resolved petition's value, and an open petition's only grows); withheld from the `query` retrieval rows; null = not cert-parsed since the column existed, which is where a resolved row the poll rotation skips stays until that pass runs |
| `merits_judgment`     | text            | what the Court did to the judgment below on a granted case (the `Judgment` vocabulary), parsed from the docket's terminal entry by the shared parser — the live poll latches it at ingest, the backfill reconciles offline; null = no parsed judgment |
| `merits_decided`      | date            | docket date of the disposition entry `merits_judgment` was parsed from; null when that entry is undated |
| `merits_brief_filed`  | date            | when the respondent filed its brief on the merits (`pipeline.merits_signals.respondent_brief_date`; live channel only, fill-in latched) — opens the merits stage's second forecast moment; null = not yet filed, or a briefing shape the pattern misses (a coverage gap, never an observed absence) |
| `response_requested_at` | date          | when the Court or a Circuit Justice asked for a response to an interim application (live channel only, fill-in latched) — the interim stage's second forecast moment, and the dated sibling of `response_requested`; the two disagree only on an undated request |
| `response_filed_at`   | date            | when a response to the application was filed (live channel only, fill-in latched) — the interim stage's third forecast moment; a different event from the Court asking, since a respondent may answer uninvited and a requested response may never arrive |
| `merits_terminated`   | text            | why a granted case's merits proceeding ended **without** a disposition (the `MeritsTermination` vocabulary — a post-grant Rule 46 dismissal, a dismissal as moot, an abatement on the petitioner's death, a grant the Court vacated, a bare mandate notation), written by the backfill sweep alone; null = not known to have terminated |
| `merits_argued`       | date            | when the granted case was last argued — the docket's last `Argued.` / `Reargued.` entry on or after the grant (`pipeline.merits_signals.argued_date`), so a reargued case carries its reargument; written by the live poll at ingest and by `backfill-decision-record`, fill-in latched; withheld from the `query` retrieval rows; null = not argued, or not yet parsed — read it beside `merits_decision_method` |
| `merits_decision_method` | text        | how the Court decided a granted case (the `MeritsDecisionMethod` vocabulary: `argued-signed`, `argued-per-curiam`, `summary-opinion`, `summary-order`, `dig`), read by `pipeline/decision_record.py` from the last judgment-shaped entry, the grant date and `merits_argued` — over **every** granted row, GVRs and summary reversals included, unlike the merits pair; written by the live poll at ingest and by `backfill-decision-record`, fill-in latched; withheld from the `query` retrieval rows; null = unclassified (pending, terminated without a disposition, or an entry the reader cannot place) |
| `capital_case`        | integer (0/1)   | the Court's `*** CAPITAL CASE ***` marking, read from the annotation upstream appends to the case number and latched here as ingest strips the number to its canonical spelling; max-latched, since only one channel serves the annotation — 0 = not marked by any channel that wrote the row, which on a CourtListener-only row is silence rather than a denial |
| `opinion_enrich_attempted_at` | date    | tracking state: when the opinion-enrichment walk (`enrich-opinions`) last reached a verdict about this case (a body, no cluster, a refusal, a 4xx) — the walk's rotation key, read never-attempted-first then stalest-stamp-first, so the grants that can never converge (a GVR or DIG that publishes no opinion; a decided grant neither of the walk's two routes resolves) cannot hold the head of every run; null = never attempted. The rotation orders *within* the walk's priority groups: a case the git ledger holds a committed merits event for, whose `merits_judgment` has latched, comes first — grading a merits forecast is what the body is an input to, and the latch is what says the body exists (a pending case stays in the rotation, since promoting it would spend the run's cap on opinions that have not published) |
| `document_floor_probed_at` | date    | tracking state: when the document back-fill (`backfill-documents`) last read this case at one of its fetch floors — it fetched the docket and the selector found nothing fetchable behind any kind the case is missing; null = never floored. It is that pass's exclusion key, not a rotation key: a floored candidate is held out of the gap class while the stamp is no older than `last_live_polled`, so a floor costs one paced docket GET per poll of that docket rather than one per dispatch. The next poll releases it; a docket that has left the live rotation (decided, or below its Term floor) is never re-polled, which is the terminal reading for a closed docket the Court served no PDF on. Written on an apply only, never for a floor the pass's own modern-docket alarm fired on, and through a direct `UPDATE` rather than the row upsert — under the corpus split a row read off the payload-free index carries no opinion body, and re-mirroring it would delete the body from the store's `case.json` |

`judges` and `panel` describe the same bench from different angles: `judges` is the
flat name list retrieval matches on, while `panel` carries the structured detail.
`counsel` stands to `parties`/`attorneys` as `panel` stands to `judges`, and it
carries the one fact the flat lists cannot: which side each name appears for. The
flat lists are deduplicated and sorted, so an attorney's side is unrecoverable
from them — and the side is what separates opposite signals. The Solicitor
General appears as counsel for the *respondent* on a large share of criminal
petitions, opposing certiorari; "the United States is the petitioner" is a
different fact.

The role also separates a stable fact from a moving one. The `petitioner` and
`respondent` blocks are fixed when the petition is docketed and do not move as
the docket progresses — unlike `distribution_count` and `cvsg_date` they are
arrival-time, which is what makes them usable in a prospective score. `other` is
the opposite: it accumulates amici over the docket's life and overwhelmingly
after a grant, so counting it on a decided docket is a grant oracle. The flat
`attorneys` list mixes the two with nothing to tell them apart.

The multi-valued sibling facts (`panel`, `parties`, `attorneys`, `counsel`) are
filled by whichever channel carries them; a bulk-shaped source supplies them
through the shared normalizer, `fedcourtsai.pipeline.ingest.from_bulk_row`. One
carve-out at the storage seam: the bulk export's docket↔opinion-cluster join is
misjoined on the circuit slices, so `to_corpus_row` withholds the
cluster-derived fields (`summary`, `opinion_text`, `precedential_status`,
`judges`, `panel`, `citations`, `citation_count`)
from a bulk circuit row — a replica-shaped source with a sound join must
revisit that predicate, which keys on the channel (`source == bulk`), not on
any particular export. `opinion_text` is in that set for a second reason as
well: the only other channel that fills it is the SCOTUS-scoped opinion
enrichment (`fedcourts enrich-opinions`), so keeping the bulk join out of the
column is what makes a populated body on a non-SCOTUS row impossible rather
than merely unlikely. The
CourtListener REST path reports no side, so `counsel` is empty there, exactly as
`seniority` is — and because every writer asserts the column, that empty list
would erase a live reading if the same docket ever took a REST or bulk write.
The upsert therefore latches it: an empty incoming list keeps the stored one,
and a non-empty reading (the live channel's re-read) replaces it, so a
corrected parse still lands. A row last written before the column existed
stays empty until a live re-poll, a re-walk or `refresh-dockets` re-serves it —
the same legacy-row shape as `sample_weight` below. A decided docket leaves the
live rotation (a granted docket stays in it until its judgment), so on a
decided row that re-serve does not come on its own.

`last_pulled` is per-case **tracking state**, not a docket fact: `pull` stamps it
on every refresh and the budget governor rotates the oldest-`last_pulled`-first
slice of the unresolved set within the API budget (see
[docs/data-pipeline.md](../docs/data-pipeline.md)).
`opinion_enrich_attempted_at` is the same kind of column for a different walk:
the opinion enrichment stamps it on every case an applied run reached a verdict about, and
rotates never-attempted-first then stalest-first over it.
`document_floor_probed_at` is a third, and the one that is not a rotation key:
the document back-fill stamps it where a case sits at a fetch floor, and reads
it against `last_live_polled` to hold that case out of its gap class until the
docket is polled again. All three are fill-in latched, so a writer carrying no
stamp preserves the stored one — on the floor probe the latch is the only thing
that does, since it is written by a direct `UPDATE` that no other writer
repeats.
`embedding[]` (semantic retrieval) is a later upgrade and is not stored yet.

The live-parsed signal family (`distributed_for_conference`,
`distribution_count`, `cvsg_date`, `originating_court_name`) is supplied only by
the supremecourt.gov channel; every other writer preserves the stored values
(fill-in latches, except `distribution_count`, which max-latches — proceedings
are append-only, so the count only grows). `distribution_count` doubles as the
family's parse-coverage sentinel: null means the proceedings were never
live-parsed, 0 asserts *parsed and never distributed*. The interim-application
family (`application_kind`, `response_requested`, `referred_to_court`,
`amicus_briefs`) is the same shape for the live channel's application branch:
supplied only there, null everywhere else (the never-application-parsed
sentinel, with `application_kind` playing `distribution_count`'s coverage
role). The three escalation signals max-latch — each is monotone over an
application's life, so a degraded parse's confident 0 never regresses a stored
value — as does the cert branch's `cert_amicus_briefs`, monotone under its own
cut at the petition's first disposition entry — and `application_kind` gets the TEXT twin of that latch: a real reading
(`extension` / `substantive`) is never wiped by a degraded parse's confident
`unknown`, which only ever fills a genuine gap. The dated signals beside these
families (`response_requested_at`, `response_filed_at`, `merits_brief_filed`,
`sg_brief_filed`, `call_for_response_at`, `relisted_at`, `merits_brief_on_lead`,
`argument_transcript_at`), the opening petition's `opening_writ`, the
`distributed_after_call` count,
and the merits decision record (`merits_argued`, `merits_decision_method`),
fill-in latch for `cvsg_date`'s reason instead: a missing parse leaves each null
rather than a confident sentinel, so no other writer may blank a reading the live
channel stamped — which on `response_requested_at` would leave the max-latched
`response_requested` flag standing beside a null date, the shape reserved for a
genuinely undated request. `sample_weight` is
min-latched — an inclusion probability is only ever learned toward certainty —
so a weighted aggregate can multiply by it and count a denial the earlier
sampled walk kept at full strength; null means no channel asserted a weight. The
walk keeps every decided petition, but what it writes is a reading of the corpus
rather than its own certainty: `ingest_live_payload` re-derives an asserted
weight of 1 through `legacy_denial_sample_weight`, so a legacy row regresses only
once a re-walk has enumerated the block it stands for — re-serving the kept
serial alone leaves the nine petitions behind it represented by nobody. The merits pair (`merits_judgment`, `merits_decided`) moves as
a **pair**, written by two writers through one parser: the live poll latches it
at ingest on a granted cert docket, and `backfill-merits-judgments` reconciles
offline over stored snapshots. The upsert keys both columns on the incoming
judgment — a writer carrying no parse (a CourtListener enrichment, a bulk row,
a degraded payload) keeps both stored values, while a fresh parse takes both,
its null `merits_decided` included, since a date kept from a different entry's
parse would fabricate a mismatched pair. Merits outcome detection reads these
columns, so the pair is a scoring input, not only a statistic.
`merits_terminated` sits beside the pair and deliberately outside it: a granted
case can end with no disposition at all — voluntarily dismissed under Rule 46
after the grant, dismissed as moot, abated on the petitioner's death, left with
its grant order vacated, or carrying a bare mandate notation and nothing
else — and
recording that as a seventh `Judgment` would put a non-disposition into the
parsed slice the merits base rate is pooled from, scored as though the judgment
below had survived. So the sweep stamps its own column instead, only where no
judgment shape matched anywhere in the snapshot. The effect is on *pendency*,
not on scoring: the forecast admission and the provisioning gate refuse a
terminated row exactly as they refuse a latched one, while the statpack sees a
row with no parsed judgment, which is what it is. No ingestion channel has one
to assert, so the upsert keeps the stored value rather than clearing it.
One consequence is accepted rather than fixed: a terminated case that already
carries a minted merits event keeps that event **open forever**, because
resolution keys on `merits_judgment` and there is no judgment to record. The
event stops earning cells (the forecast admission refuses it) and provisioning
refuses any that slip through, so this is rotation cost and open-event noise,
never leakage — but it is why the open-event census counts more merits events
than the forecast stream contains.

`predict_eligible` is a **derived convenience mirror** of the prediction scope
(`court == 'scotus'`): every scope seam reads the court predicate directly, so
the column is queryable but never the source of truth. Only the agentic
predict/evaluate stages are gated; ingestion stays full-coverage. The
lower-court link (`originating_court` / `originating_docket_number`) is
retrieval context, never a scope trigger. See the prediction scope in
[docs/data-pipeline.md](../docs/data-pipeline.md).

## Predictable events (`events`)

The things the pipeline predicts about a case are raw facts too, so they live
in the corpus, not as per-case files. The deterministic event-definition stage
(`fedcourtsai.pipeline.events`) records one or more events per docket by
classifying its entries; see [docs/data-pipeline.md](../docs/data-pipeline.md).
Every docket carries a case-level **baseline** event: the appeal's disposition
off SCOTUS; at SCOTUS, the cert petition's (`kind = petition`, `stage = cert`)
on a `YY-NNNN` docket, or the application's (`kind = motion`, `stage =
interim`) on a `YYAnnn` application docket — a stay or injunction application
is a motion under the interim standard, not a cert petition.

| Column            | Type        | Notes                                       |
|-------------------|-------------|---------------------------------------------|
| `case_id`         | text (PK)   | `<court_id>/<docket_id>`                     |
| `event_id`        | text (PK)   | `evt-<kind>-<slug>`; unique within a case    |
| `court`           | text        | CourtListener court id                       |
| `kind`            | text        | motion / petition / appeal / order          |
| `stage`           | text        | decision standard (cert / interim / merits); null where none is recorded |
| `moment`          | text        | which forecast moment of the stage this event is; null where unrecorded, read downstream as the stage's first moment |
| `title`           | text        |                                             |
| `description`     | text        |                                             |
| `docket_entry_id` | integer     | docket entry the event is pinned to; null for case-level |
| `decision_target` | text        | what is predicted (default `disposition`)   |
| `opened_at`       | date        | when the event became predictable           |
| `resolved`        | integer     | 0 while open, 1 once resolved               |

## Cursors and watermarks

Per-court discovery watermarks (`discovery_watermarks`: `court`, `last_filed`)
are dormant in production (`pull.discover_new_filings` is off — the live
channel onboards SCOTUS filings). The live channel's and the historical
walker's per-(Term, stream) cursors share one `live_discovery_cursors` table
with disjoint stream names and the same only-moves-forward semantics. Beside
each cursor's `last_serial` sits a nullable `frontier_serial` — where the
stream's end (consecutive 404s) was last observed; `frontier_serial =
last_serial` reads as *walk complete at the current cursor*, and the cursor
pair yields an exact per-Term filings census by fee class (paid serials number
from 1, IFP from 5001) without ingesting every serial.

## Dated snapshots (`snapshots`)

Each ingestion channel stores the full point-in-time docket payload it fetched
(the REST docket + entries, or the supremecourt.gov docket JSON) — the raw fact
a normalized `cases` row cannot fully capture. `pull` diffs the latest stored
snapshot against the fresh fetch to decide whether a case *changed* (what routes
it onto the predict queue), and provisioning materializes a snapshot for the agent
to predict from (`fedcourts provision-snapshot`) — **which** snapshot being the
moment's question, not the table's: a cell is placed at the information
set the event it forecasts declares, so it reads the payload the docket served
then (or the latest one truncated to that cutoff), and only a cell with no
declared moment reads the latest snapshot as stored (the `provision-snapshot`
row in [docs/cli.md](../docs/cli.md) carries the placement rules). In production
the payloads live as the content store's `snapshots/<date>.json` objects and
this table stays empty; with the split mode off they live inline:

| Column          | Type      | Notes                                          |
|-----------------|-----------|------------------------------------------------|
| `case_id`       | text (PK) | `<court_id>/<docket_id>`                        |
| `snapshot_date` | text (PK) | pull date; one snapshot per case per day        |
| `payload`       | text      | full-docket JSON (sorted keys for stable bytes) |

## Per-opinion record (`opinions`)

One row per opinion in a decided case: the Court's opinion and every separate
writing, read from the documents the Court's per-Term opinions listing links
(`pipeline/opinion_record.py`). Like the case row's decision columns, this is
a historical record held corpus-side; no outcome is written to the git ledger
for a case the pipeline never forecast. Written only by
`fedcourts backfill-opinion-record` (run-repair's `opinion-record` pass, and its
standing sweep on run-seed's daily window over the current and previous Term),
which is fill-only: a document is recorded
whole or not at all, and a recorded row is never changed. So a new version of
the counting rule or of a reader reaches stored rows only through a pass built
to replace them, which does not exist yet; `word_rule` and `lineup` say which
version each row was read under. Its readers outside its writer are `fedcourts merits-lineups`,
which derives each decision's per-Justice votes from it, and `fedcourts authorship-tally`,
which reads each lead opinion's author against its argument sitting, and the statpack's authorship
and per-Justice votes sections, which roll it up per Term; it is read by no `query`
retrieval row, outcome, mint or scoring gate, and provisioning reads it only for
the tally a post-argument merits cell would be given, which is held back from
every cell (`provision.AUTHORSHIP_TALLY_WITHHELD`), and to pick the decisions whose
writings `provision-opinion --writings` stages into a pilot round's evaluate cell;
a test pins which modules may name it. It is metadata, not payload, so it stays in the index blob under the
corpus-split mode and has no content-store mirror; the writings' text, which
is payload, goes to the content store instead (`opinion_texts`, below). The source, the cross-check
and the word-counting rule are in [docs/data-sources.md](../docs/data-sources.md).

| Column           | Type          | Notes |
|------------------|---------------|-------|
| `term`           | integer (PK)  | October Term, four-digit |
| `listing_number` | text (PK)     | the listing row's number (`66`, `D1`): one document |
| `position`       | integer (PK)  | the opinion's order in the document, from 1 |
| `docket`         | text          | the listing's docket cell as printed |
| `dockets`        | text (JSON)   | every docket number in that cell; the listing prints only a consolidated case's lead docket |
| `case_id`        | text          | the corpus case row of the first docket, by the corpus's docket-number reconciliation (`norm_dn`; the lowest docket id where two rows match), as of the read; null where no row carries it. A convenience link: the dedupe pass (`dedupe-live-rows`) does not re-point it, and the listing key is the row's identity |
| `case_name`      | text          | as the listing prints it |
| `decided`        | date          | the listing's decision date |
| `argued`         | date          | the syllabus's printed argument date (the latest); null for a per curiam or where none is printed |
| `kind`           | text          | the `WritingKind` vocabulary: `opinion-of-the-court`, `plurality`, `per-curiam`, `concurrence`, `concurrence-in-part`, `concurrence-in-judgment`, `concurrence-in-part-dissent-in-part`, `dissent`, `statement` |
| `author`         | text          | roster surname; null only for a per curiam |
| `coauthors`      | text (JSON)   | the other signers of a jointly written opinion |
| `joins`          | text (JSON)   | `[{justice, qualifier}]`; `qualifier` is a partial join's printed limit ("as to Part II-B", "except as to Part III-B"), null for a join in full. A lead opinion's joiners come from the syllabus, which a per curiam does not print, so a per curiam's are empty |
| `scope`          | text          | a lead opinion's own limit ("except as to Part II"); null otherwise |
| `words`          | integer       | the word count under `word_rule`, footnotes included |
| `footnote_words` | integer       | the footnotes' share of `words` |
| `word_rule`      | text          | `<rule>/<version>` of the counting rule (`scotus-opinion-words/1`) |
| `lineup`         | text          | `<reader>/<version>` the writings were read by: the syllabus grammar, or the header reader for a per curiam |
| `source_format`  | text          | `slip` or `preliminary-print` |
| `document_url`   | text          | the supremecourt.gov PDF read |
| `header`         | text          | the opinion's header sentence as printed, normalized (spacing and split words closed up) |
| `read_at`        | timestamp     | when the row was written |

## Who sat (`opinion_benches`)

At most one row per signed decision the per-opinion record holds, keyed as
`opinions` is: the bench the syllabus reader seated and the Justices it says took no part.
It is the one fact a decision's writings do not carry — a Justice who took no
part signs nothing, and so does one the record has not placed — and the one the
merits lineups (`fedcourts merits-lineups`, `pipeline/merits_lineups.py`) need
beside the writings to tell the two apart. Written only by
`fedcourts backfill-opinion-record`, fill-only, in the transaction that inserts
the document's opinion rows, or on a later pass for a document recorded without
one; that row is null unless the re-read writings are the stored ones. The lists
are read only off a complete syllabus lineup that agrees with the listing, the
lineup the merits vote source stamps from, and are null otherwise: a null row
says the document was read and its participation not observed, never that
nobody was absent. A per curiam takes no row, since its headers do not say who
sat. Held on the same terms as `opinions`: corpus-side, read by no `query` row,
provisioning step, outcome, mint or score, and kept in the index blob.

| Column           | Type         | Notes |
|------------------|--------------|-------|
| `term`           | integer (PK) | October Term, four-digit |
| `listing_number` | text (PK)    | the listing row's number: the document |
| `bench`          | text (JSON)  | roster surnames the reader seated for the decision date; null where participation was not observed |
| `took_no_part`   | text (JSON)  | the bench members the syllabus says took no part; null with `bench` |
| `lineup`         | text         | `<reader>/<version>` of the syllabus grammar the bench was read with |
| `read_at`        | timestamp    | when the row was written |

## The writings' text (`opinion_texts`)

At most one row per document the per-opinion record holds, keyed as
`opinions` is: the pointer to the content-store object
(`scotus/opinions/OT<term>/<listing>-<digest>.json`) that holds each of its
writings' text, cut under the text rule in
[docs/data-sources.md](../docs/data-sources.md) and held to the stored word
counts. The text is payload, so the object is the store's and the row is
only its key, digest and size. Written only by
`fedcourts backfill-opinion-record`, fill-only, after the object is stored, in
the transaction that inserts the document's other rows, or on a later pass
for a document recorded without one; that pass stores the text only where
the re-read writings, with their word counts and headers, are the stored
ones, and otherwise writes a row whose
pointer is null, which also ends the re-reading. A write with no content
store addressed stores no text and writes no text row for a document whose
text it would store, so the document stays owed.
Held on the same terms as `opinions`: corpus-side, read by no `query` row,
outcome, mint or score. One provisioning step reads it: `fedcourts
provision-opinion --writings`, which stages a decided case's writings into a
pilot round's evaluate cell and no other. The text is the Court's, but it
reached the store through the parse job's plan, whose check is only that the
text recounts to its own word counts, so a reader takes the object only when
its bytes match the row's digest (`casestore.read_pinned`) and treats it as
data, never as instructions.

| Column           | Type         | Notes |
|------------------|--------------|-------|
| `term`           | integer (PK) | October Term, four-digit |
| `listing_number` | text (PK)    | the listing row's number: the document |
| `object_key`     | text         | the stored object's key; null where the re-read writings were not the stored ones |
| `digest`         | text         | the object's sha256; null with `object_key` |
| `bytes`          | integer      | the object's size; null with `object_key` |
| `text_rule`      | text         | `<rule>/<version>` the text was cut under (`scotus-opinion-text/1`) |
| `read_at`        | timestamp    | when the row was written |

## Argument sittings (`argument_sittings`)

One row per argument sitting, as the Court heads it on its transcript list for
the Term ("Argument Session: October 06, 2025 - October 15, 2025",
`supremecourt.parse_argument_sittings`). Written by the live cycle's transcript
pass on every list it reads, the Term today falls in and the one before it,
each heading upserted by its Term and first day, so a sitting the Court later
widens takes its new last day. A heading the Court drops or re-dates is not
deleted, and can overlap its replacement. A Term the pass has never listed has
no rows.
Its one reader is `fedcourts authorship-tally` (`pipeline/authorship.py`), which
groups a Term's argued cases by sitting, and the same tally a post-argument
merits cell would be given in `record/authorship-tally.json`, which is held back
from every cell until a re-bless (`provision.AUTHORSHIP_TALLY_WITHHELD`); it is
read by no `query` retrieval row, outcome, mint or scoring gate. Kept in the
index blob.

| Column    | Type          | Notes |
|-----------|---------------|-------|
| `term`    | integer (PK)  | October Term, four-digit |
| `start`   | date (PK)     | the sitting's first day, as headed |
| `end`     | date          | its last day, as headed |
| `read_at` | date          | the day the heading was last read |

## Working with it locally

```bash
export CORPUS_BASE_URL="<the corpus estate's base url>"   # out of band, see SECURITY.md
# The index remote sits one segment below it. Where you hold that half's own
# URL instead, export CORPUS_REMOTE_URL with it and skip the base.
fedcourts corpus-pull    # fetch corpus.db from the remote (checksum-verified)
fedcourts corpus-info    # show the location, row count, and how fresh the blob is
fedcourts corpus-info --text-coverage   # also: which stored documents carry no text, per kind
```

`--text-coverage` is opt-in because it reads every live-slice case's documents
(a content-store round trip each under the split), and it answers the other
question worth asking of a blob before quoting it: not how old the documents
are but whether they carry text at all.

Without remote access, build a tiny **synthetic** corpus instead — a handful of
cases across several courts, a mix of resolved and open, with their events and
snapshots — so the read commands (`provision-snapshot`, `query`, `open-events`)
work offline. It is deterministic and never a substitute for the real corpus:

```bash
fedcourts make-fixture-corpus    # writes the synthetic corpus to corpus/corpus.db
```

Between those two there is a third corpus, which nobody builds locally: the
**staging pair** — a lean slice of real cases copied into its own private
bucket/prefix pair by `fedcourts corpus-seed-slice`, from the dispatch-only
`staging-corpus-refresh` workflow that alone holds the credential to write it.
It carries the same two-store shape and the same access terms as production,
and exists so orchestration and the read/write seams can be exercised against
real content without anything gaining write access to the corpus described
here. A reader reaches it by re-pointing the env contract —
`scripts/corpus-env staging <command>`, which also supplies the pair's index
pointer out of band, since only production's is committed (*Developer access*
in [docs/data-pipeline.md](../docs/data-pipeline.md)). Provisioning and
operating it: *The staging corpus (provisioning
runbook)* in [docs/security.md](../docs/security.md).

## Precedent retrieval

At prediction time a model pulls a handful of *relevant* priors rather than the
bulk set. `fedcourts query` (and the `corpus.retrieve_priors` library API) takes
structured filters — exact match on `--court` / `--topic` / `--disposition`,
overlap match on repeatable `--judge` / `--citation` — and prints the priors as
ranked JSON lines, most relevant first, decided cases only unless
`--include-open`:

```bash
fedcourts query --court ca9 --topic "civil rights" --judge smith --citation "410 U.S. 113"
```

Each given filter must match (the filters AND together); judges/citations rank
the survivors by how much they share. A `citation` filter is served off the
partial index over the rows whose `citations` is non-empty — that is the whole
candidate set, since an empty column cannot overlap a non-empty filter — and
where that population is small the command says so on stderr before the rows
come back, so an empty result reads as a thin column rather than a missing case.
`opinion_text` is omitted unless `--full`.
Semantic / embedding similarity is a later upgrade on the same query seam.
