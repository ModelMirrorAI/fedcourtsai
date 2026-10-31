# Document provisioning

How a court filing becomes text a cell reads: which filings are chosen, how
they are fetched, stored, cut and recovered, what is withheld before a cell
sees them, and how to measure how much of the set a cell actually got. This
page is the map. The rules themselves are specified where they are enforced,
mostly *Documents: from metadata to content* in
[live-sources.md](live-sources.md), and each step below links to them.

A cell's record has two halves. The **snapshot** is the docket as the cell's
moment saw it ([data-pipeline.md](data-pipeline.md), *Provisioning: how a cell
gets its record*). The **documents** are the filings' text beside it, under
`record/documents/`. This page covers the second half. Opinions are not
documents: `provision-opinion` stages a majority opinion in its own slot
(`record/opinion/`).

## The path, in order

| Step | What happens | Code | Specified in |
| --- | --- | --- | --- |
| Select | Each docket's proceedings entries are read for the filings of each kind below, by the filing's own wording. A consolidated member reads its merits filings off the lead docket. | `pipeline/documents.py`: `select_documents`, `consolidation_lead` | live-sources.md, *What is selected, and under which kind* |
| Fetch | `live.provision_documents` fetches when a lane queues a case for prediction: on the distribution transition, on a pending application's change, and in the frontier catch-up. The salience selection sweep fetches for selected cases, which is how the merits kinds arrive. Every live cycle ends with a freshness pass over the cases it polled. A `(kind, url)` already stored is never fetched again. Multi-respondent oppositions are combined into one row, and so are a docket's supplemental briefs and its party letters, one row per kind. Losses are recorded by reason. | `pipeline/documents.py`: `fetch_case_documents`; `pipeline/live.py`: `provision_documents`, `refresh_stale_documents` | live-sources.md, *Document freshness* |
| Transcripts | The argument transcript is linked by no docket entry, so each live cycle reads the Court's per-Term transcript lists and stores the transcripts a corpus case lacks, dated by the argument day. | `supremecourt.py`: `parse_transcript_listing`; `pipeline/live.py`: `fetch_argument_transcripts` | live-sources.md, *Argument transcripts* |
| Argument features | Not a document: a deterministic parse of the transcript a post-argument cell is staged counts each Justice's turns and words by the side of the advocate whose time it was, read from the segment headers, and reports what it could not attribute. Written beside the documents as `record/argument-features.json`, from the staged copy, so the counts describe the text the cell reads; a parse whose totals do not reconcile writes no file. | `pipeline/argument_features.py`: `parse_argument_features`; `provision.py`: `staged_argument_features`; `fedcourts argument-features` | live-sources.md, *Argument transcripts* |
| Back-fill | A dispatched pass fetches the selection for predict-relevant cases whose stored set is missing kinds. | `pipeline/document_backfill.py`; `fedcourts backfill-documents` | live-sources.md, *Contract for the document back-fill pass* |
| Extract | pypdf text, cut at the cap. Petitions, applications and appendices are cut around the appendix so the argument survives. A combined row of several filings is cut filing by filing, every filing's own text before any appendix, the cap shared between them. Each cut leaves a `[pipeline note: …]` line. The questions presented are cut from the petition text, from the QUESTION(S) PRESENTED heading (or a "Questions to/for Review" heading) to the next front-matter heading, at most 4,000 characters; a section cut at that cap is stored `truncated`, and `backfill-questions-presented` re-derives stored rows when the cutter changes. An argument transcript is cleaned of its line numbers, headers and word index before the plain cut. | `extract_pdf_text`, `extract_filing_text`, `extract_questions_presented`, `extract_transcript_text` | live-sources.md, *The appendix-aware cut* |
| Re-cut | A stored petition, application or appendix still under the plain head cut (truncated, not OCR-derived, no `[pipeline note:` line) is re-fetched by its stored URL and re-cut by the appendix-aware rule. run-repair's `recut` pass applies it a slice at a time. | `pipeline/document_recut.py`; `fedcourts recut-documents` | live-sources.md, *Contract for the re-cut pass* |
| Recover | A stored document whose text is empty though its PDF has pages is OCR'd locally (pdftoppm + tesseract) and marked `ocr_derived`. A standing sweep on run-seed's walker windows catches new scans, and run-repair's `ocr-recovery` pass clears a backlog. | `pipeline/ocr_recovery.py`, `pipeline/ocr_sweep.py`; `fedcourts ocr-recover-petitions` | live-sources.md, *Contract for the recovery pass*; data-pipeline.md, *Historical — the Term walker* |
| Cut at the moment | A document is kept only if its proceedings entry is dated before the cell's moment cutoff, so a grant-moment cell never reads the merits briefs. The argument transcript is kept only for a post-argument cell, and a stored-not-staged kind for no cell. | `provision.py`: `moment_cutoff`, `documents_for_moment`, `documents_before` | data-pipeline.md, *Provisioning: how a cell gets its record* |
| Scrub | On a docket with a self-represented side, contact details are withheld from the staged text and the staged snapshot. Where the shape pass ran, a residual detector re-reads the scrubbed text's opening and closing, and any match records the document as **not** scrubbed. The document is still staged. | `pipeline/documents.py`: `scrub_contact_details`, `contact_residual_matches`, `scrub_snapshot_contacts`; `provision.py`: `staged_scrub` | live-sources.md, from the paragraph introducing the contact-detail scrub through *What the scrub does not reach*; data-sources.md, *PII stance* |
| Stage | Each kept document is written to `record/documents/<kind>.txt`, with a manifest at `record/documents/documents.json`. | `provision.py`: `write_cell_record`, `document_manifest` | predicted-artifacts.md, *Where the files land*; cli.md, `provision-snapshot` |
| Companions | Not a document: a predict cell also gets the snapshot of each docket its placed snapshot links as `Vide`, cut by the date rule to its cutoff (or its own snapshot date where it has none) and redacted of undated outcome markers, under `record/related/` with a `related.json` listing every link. No filing text of a companion is staged. | `pipeline/vide_links.py`: `vide_docket_numbers`; `provision.py`: `place_related`, `related_manifest` | cli.md, `provision-snapshot` |

## What a cell can be given

These are the kinds, from `pipeline/documents.py`. Selection is per docket and
the moment decides by date, so a cell gets every kind below that its docket
carries and that was filed before its cutoff. The one exception is the argument
transcript, which only a post-argument cell is given.

| Kind | Filing | Docket |
| --- | --- | --- |
| `petition` | The case-opening filing on a cert-form docket: a certiorari petition, or a mandamus, prohibition or habeas petition, or a direct appeal's jurisdictional statement | Cert |
| `questions-presented` | The questions presented, cut from the petition text | Cert |
| `appendix` | The opening filing's or application's separately linked appendix | Cert, Application |
| `brief-in-opposition` | Every respondent's opposition, combined into one row | Cert |
| `cert-reply` | The petitioner's reply to the opposition | Cert |
| `sg-invited-brief` | The Solicitor General's brief when the Court called for it | Cert |
| `supplemental-brief` | Every party's Rule 15.8 supplemental brief while the petition is pending, combined into one row | Cert |
| `party-letter` | Every party's letter to the Clerk bearing on the case while the petition is pending (mootness, settlement, withdrawal, an intervening decision), combined into one row | Cert |
| `merits-brief-petitioner`, `merits-brief-respondent` | Each side's brief on the merits | Granted |
| `merits-reply-petitioner`, `merits-reply-respondent` | Each side's reply on the merits | Granted |
| `merits-amicus-united-states` | The United States' amicus brief on the merits, filed after the grant | Granted |
| `merits-brief-appointed-amicus` | The merits brief of a Court-appointed amicus defending the judgment, filed after the grant; stored, staged for no cell yet | Granted |
| `argument-transcript` | The oral argument transcript, from the Court's per-Term list rather than the docket | Argued |
| `decision-below` | The federal court of appeals' opinion under review, read from CourtListener and dated by the judgment below; stored, staged for no cell yet | Cert, Granted |
| `lower-court-docket` | A short record of that court's docket: panel, and whether rehearing en banc was sought, how it was disposed of and any dissent; stored, staged for no cell yet | Cert, Granted |
| `application` | The application to a Justice or the Court | Application |
| `application-response` | The first response to the application | Application |
| `application-reply` | The applicant's reply to it | Application |

A new kind is fetched and stored before any cell is given it. Which kinds a
cell reads is part of its information set, and the process digest does not see
it ([process-version.md](process-version.md)), so a kind is staged only in the
re-bless whose prompt tells cells about it. Until then
`provision.WITHHELD_KINDS` keeps it from every cell at every moment, and the
case-summary plan leaves it out of the record it reads. Three kinds are held
there now: `merits-brief-appointed-amicus`, `decision-below` and
`lower-court-docket`. One record input that is not a document is held back on the same rule:
the post-argument merits cell's `record/authorship-tally.json`, the Term's
tally of who has written from each argument sitting
(`provision.AUTHORSHIP_TALLY_WITHHELD`).

Amicus briefs other than the United States' and a Court-appointed amicus's are
never selected: the Solicitor General's invited brief at the cert stage, the
United States' brief on the merits after the grant, and the brief of an amicus
the Court appointed to defend the judgment below. A cell with retrieval rights can still reach the others
upstream.

## The settings that bound it

| Setting | Value | What it bounds |
| --- | --- | --- |
| `live.document_text_cap`, `historical.document_text_cap` | 150,000 characters | The stored text of one document |
| `live.document_freshness_per_run` | 10 | Cases the freshness pass fetches for in one live cycle |
| `live.argument_transcripts_per_run` | 5 | Transcripts the argument-transcript pass downloads in one live cycle |
| `historical.sweep_caps.ocr` | 10 | Documents the OCR sweep recovers in one walker window |
| `historical.document_floor_term` | 21 | The oldest Term whose historical petitions get documents fetched; the Court's document links reach back only about five Terms |

The values are the ones in [config/tracking.yaml](../config/tracking.yaml),
which overrides the code's defaults.

## Two files named `documents.json`

- **The content store's** `documents/documents.json` holds one case's stored
  documents, each kind with its current text leaf ([corpus/README.md](../corpus/README.md)).
- **The cell's** `record/documents/documents.json` is the staging manifest: one
  row per staged kind, with `kind_description`, `pages`, `truncated`,
  `ocr_derived`, `empty_text` and the contact-scrub fields
  ([predicted-artifacts.md](predicted-artifacts.md)).

## What the set does not cover

Each of these is stated, with its reason, where the code makes the choice:

- **A petition raising the same question without a `Vide` link is not staged.**
  Only linked companions reach `record/related/`. `fedcourts same-question`
  lists the unlinked ones by questions-presented text similarity, cut to a date,
  and `fedcourts same-question-lists` builds a cert cell's list at its own
  cutoff, which provisioning stages as a forward cert cell's
  `record/same-question.json` (`pipeline/same_question.py`; the harness
  boundary `cert-same-question-list`).

- **A combined opposition is cut brief by brief, its page count estimated.**
  Each brief is placed by the docket date in its header, so a cell placed
  between two respondents' briefs reads the earlier one alone. The stored row
  keeps no per-brief page count, so a cut row's `pages` is the row's count
  scaled by the share of text kept (`documents_before`).
- **A corrected filing replaces the original.** The latest fetch of a kind wins,
  so a cell can read the text as later amended (`documents_before`), or lose
  the kind if the correction is dated after its cutoff (live-sources.md,
  *Document freshness*).
- **An unchanged link is never re-extracted.** A row stored under an older cut
  keeps that cut (live-sources.md, *Document freshness*).
- **A combined opposition is never OCR'd.** Its URL is a set key, not a link to
  fetch. An all-scan combined opposition still carries its per-brief headings,
  so the coverage report's per-kind cuts count it as having text. The report
  sizes it on a separate line, which reads it brief by brief (live-sources.md,
  *How large the degradation is*).
- **The residual check reads only part of a document.** The detector reads a
  document's opening and closing, not its middle, and does not run where only
  the value pass ran. A document it flags is still staged to the cell
  (live-sources.md, the contact-detail scrub).
- **A Rule 34.6 docket stages no party filings, and the record says why.**
  The Court's entry putting a docket's filings on paper only (Rule 34.6 and
  Paragraph 9 of its electronic filing guidelines; mostly immigration and
  detention cases) means nothing is posted behind them, so the selector finds
  no link. The cell's `record/context.json` freezes `paper_only_filings` from
  the placed payload, so a reader or grader can tell the empty
  `record/documents/` from a provisioning failure. The predict prompt does not
  name the field yet. The flag clears once the Court quotes the rule to call
  for electronic versions, after briefing and argument are scheduled
  (`pipeline/paper_only.py`).
- **A consolidated member is checked for freshness on its own docket.** A merits
  filing entered only on the lead is left to the selection sweep
  (live-sources.md, *Document freshness*).
- **The decision below reaches a cell only through the petition's appendix
  until a re-bless releases the two CourtListener kinds.**
  `fedcourts enrich-decision-below` joins a petition from a federal court of
  appeals to the lower court's docket on CourtListener and stores what upstream
  holds: the opinion on the judgment date as `decision-below`, and the docket
  record (panel, a petition for rehearing en banc, its disposition and any
  dissent noted) as `lower-court-docket` (`pipeline/decision_below.py`,
  [cli.md](cli.md)); `run-pull`'s live job runs it on six petitions each full
  window, four windows a day. The en banc reading is matched from entry text filed
  before the SCOTUS docketing, so a petition on remand cannot leak back. Both
  kinds are held in `provision.WITHHELD_KINDS`. A petition from a state court,
  a district court or a specialized tribunal gets neither, and a missing
  opinion is not bought through RECAP Fetch. `fedcourts decision-below`
  measures the match rate without storing anything: 18 of the newest 35
  circuit petitions matched an opinion in `run-analytics`'s `decision-below`
  run of 2026-10-30, on the corpus blob that run pulled.

## Measuring coverage

- `fedcourts corpus-info --text-coverage` reports how many stored petitions
  carry no text (scanned, or a PDF that would not open), how many distributed
  and queued cases hold no petition or application row at all, and the case
  ids behind each count. Its `text source:` line says whether it could read the
  content store, and its `text frame:` line says how many cases it read: read
  both before any count. It reads every stored document, so on a dev checkout
  run it where the corpus is pulled. The `run-analytics` dispatch's
  `text-coverage` mode produces the same report as an artifact
  ([pipeline.md](pipeline.md), *`run-analytics` — corpus analysis & derived metrics*).
- `fedcourts backfill-documents`, `fedcourts ocr-recover-petitions` and
  `fedcourts recut-documents` each dry-run by default, listing the cases and
  documents they would fetch, recover or re-cut.
- A single cell's manifest says what that cell got: `empty_text`, `truncated`,
  `ocr_derived` and the contact fields per staged kind.

The last measured empty-text figures, with their date and frame, are in
live-sources.md, *How large the degradation is*. Quote a figure with the vintage
`corpus-info` prints beside it.
