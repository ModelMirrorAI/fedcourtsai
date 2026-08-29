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
  in [docs/data-pipeline.md](../docs/data-pipeline.md). In production (the
  corpus-split mode,
  `FEDCOURTS_CORPUS_SPLIT=1` on the prod environment) the writers keep it
  **payload-free**: the `snapshots`/`documents` tables stay empty and
  `cases.opinion_text` stays NULL (a `has_opinion` presence bit is retained),
  so the blob stays a small metadata index and its per-run push does not
  grow with the bulk. With the mode off (the default — dev environments, the
  fixture loop, offline tests) the same schema holds the payloads inline in a
  single self-contained blob.
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
  ```

  Document text leaves are content-addressed and dated snapshots immutable per
  day, so bulk content is never overwritten in place; the small manifests are
  versioned by the bucket rather than deleted. The `questions-presented` leaf is
  *derived* from the stored petition text rather than fetched, so a fixed
  extractor can be carried onto rows already stored (`fedcourts
  backfill-questions-presented`) under that same rule: the re-derivation writes
  a new leaf and re-points the manifest, and the superseded text stays
  readable. Its location comes from `FEDCOURTS_CASESTORE_URL`.

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
| `date_decided`        | date            |                                              |
| `disposition`         | text            | realized outcome label; null while unresolved |
| `judges`              | json array      | judge names (flat retrieval key)             |
| `panel`               | json array      | structured panel: `{name, seniority}` per judge |
| `parties`             | json array      | party names on the docket                     |
| `attorneys`           | json array      | attorney names of record                      |
| `counsel`             | json array      | structured counsel: `{party, attorney, role, counsel_of_record}` per docket block; `role` is the caption side (petitioner / respondent / other). SCOTUS live+historical only |
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
| `originating_court_name` | text         | raw `LowerCourt` name — keeps state courts identifiable where `originating_court` is null |
| `sample_weight`       | integer         | inverse inclusion probability (1 = kept with certainty, which is every row the walk now writes; 10 on a denial kept by the earlier sampled walk); null = no channel asserted a weight |
| `has_opinion`         | integer (0/1)   | presence bit for a linked published opinion — kept in the index so the scope classifiers still work when the split moves the `opinion_text` body to the content store |
| `salience_score`      | real            | the salience gate's deterministic score ([docs/salience.md](../docs/salience.md)); owned by the selection pass, never an ingestion channel |
| `salience_version`    | text            | the frozen scorer version the score was written under; null = unscored row |
| `salience_selected`   | integer (0/1)   | the one-way selection latch — a selected petition is never de-selected |
| `predict_queued_at`   | date            | the last date the live channel queued predict for this case (routing or selection sweep); the sweep's daily-retry debounce reads it |
| `evaluate_queued_at`  | date            | the last date the evaluate backlog deriver queued evaluate; its daily-retry debounce reads it the same way |
| `application_kind`    | text            | what an interim application asks for (`extension` / `substantive` / `unknown`); null = never application-parsed |
| `response_requested`  | integer (0/1)   | the Court requested a response to an interim application (the interim CVSG-analogue); null = never application-parsed |
| `referred_to_court`   | integer (0/1)   | the application was referred to the full Court rather than a Circuit Justice alone; null = never application-parsed |
| `amicus_briefs`       | integer         | amicus briefs on an interim application's docket, counted per entry; null = never application-parsed |
| `merits_judgment`     | text            | what the Court did to the judgment below on a granted case (the `Judgment` vocabulary), parsed from the docket's terminal entry by the shared parser — the live poll latches it at ingest, the backfill reconciles offline; null = no parsed judgment |
| `merits_decided`      | date            | docket date of the disposition entry `merits_judgment` was parsed from; null when that entry is undated |
| `merits_brief_filed`  | date            | when the respondent filed its brief on the merits (`pipeline.merits_signals.respondent_brief_date`; live channel only, fill-in latched) — opens the merits stage's second forecast moment; null = not yet filed, or a briefing shape the pattern misses (a coverage gap, never an observed absence) |
| `response_requested_at` | date          | when the Court or a Circuit Justice asked for a response to an interim application (live channel only, fill-in latched) — the interim stage's second forecast moment, and the dated sibling of `response_requested`; the two disagree only on an undated request |
| `response_filed_at`   | date            | when a response to the application was filed (live channel only, fill-in latched) — the interim stage's third forecast moment; a different event from the Court asking, since a respondent may answer uninvited and a requested response may never arrive |
| `merits_terminated`   | text            | why a granted case's merits proceeding ended **without** a disposition (the `MeritsTermination` vocabulary — a post-grant Rule 46 dismissal, a dismissal as moot, an abatement on the petitioner's death, a grant the Court vacated, a bare mandate notation), written by the backfill sweep alone; null = not known to have terminated |
| `capital_case`        | integer (0/1)   | the Court's `*** CAPITAL CASE ***` marking, read from the annotation upstream appends to the case number and latched here as ingest strips the number to its canonical spelling; max-latched, since only one channel serves the annotation — 0 = not marked by any channel that wrote the row, which on a CourtListener-only row is silence rather than a denial |

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
`seniority` is. A historical row serialized before the column existed also stays
empty until a re-walk re-serves it — the same legacy-row shape as
`sample_weight` below.

`last_pulled` is per-case **tracking state**, not a docket fact: `pull` stamps it
on every refresh and the budget governor rotates the oldest-`last_pulled`-first
slice of the unresolved set within the API budget (see
[docs/data-pipeline.md](../docs/data-pipeline.md)). `embedding[]` (semantic
retrieval) is a later upgrade and is not stored yet.

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
value — and `application_kind` gets the TEXT twin of that latch: a real reading
(`extension` / `substantive`) is never wiped by a degraded parse's confident
`unknown`, which only ever fills a genuine gap. The dated signals beside these
families (`response_requested_at`, `response_filed_at`, `merits_brief_filed`)
fill-in latch for `cvsg_date`'s reason instead: a missing parse leaves each null
rather than a confident sentinel, so no other writer may blank a date the live
channel stamped — which on `response_requested_at` would leave the max-latched
`response_requested` flag standing beside a null date, the shape reserved for a
genuinely undated request. `sample_weight` is
min-latched — an inclusion probability is only ever learned toward certainty —
so a weighted aggregate can multiply by it and count a denial the earlier
sampled walk kept at full strength; null means no channel asserted a weight. The
walk now keeps every decided petition, so the weight it writes is always 1 and
the column's remaining job is to keep those legacy rows honest until a re-walk
re-serves them. The merits pair (`merits_judgment`, `merits_decided`) moves as
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
snapshot against the fresh fetch to decide whether a case *changed* (the
`run:predict` trigger), and provisioning materializes a snapshot for the agent
to predict from (`fedcourts provision-snapshot`) — **which** snapshot being the
moment's question, not the table's: a forward cell is placed at the information
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

## Working with it locally

```bash
export CORPUS_REMOTE_URL="<your bucket url>"   # out of band, see SECURITY.md
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
the survivors by how much they share. `opinion_text` is omitted unless `--full`.
Semantic / embedding similarity is a later upgrade on the same query seam.
