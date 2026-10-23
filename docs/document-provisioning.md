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
| Back-fill | A dispatched pass fetches the selection for predict-relevant cases whose stored set is missing kinds. | `pipeline/document_backfill.py`; `fedcourts backfill-documents` | live-sources.md, *Contract for the document back-fill pass* |
| Extract | pypdf text, cut at the cap. Petitions, applications and appendices are cut around the appendix so the argument survives; each cut leaves a `[pipeline note: …]` line. The questions presented are cut from the petition text. An argument transcript is cleaned of its line numbers, headers and word index before the plain cut. | `extract_pdf_text`, `extract_filing_text`, `extract_questions_presented`, `extract_transcript_text` | live-sources.md, *The appendix-aware cut* |
| Recover | A stored document whose text is empty though its PDF has pages is OCR'd locally (pdftoppm + tesseract) and marked `ocr_derived`. A standing sweep on run-seed's walker windows catches new scans, and run-repair's `ocr-recovery` pass clears a backlog. | `pipeline/ocr_recovery.py`, `pipeline/ocr_sweep.py`; `fedcourts ocr-recover-petitions` | live-sources.md, *Contract for the recovery pass*; data-pipeline.md, *Historical — the Term walker* |
| Cut at the moment | A document is kept only if its proceedings entry is dated before the cell's moment cutoff, so a grant-moment cell never reads the merits briefs. The argument transcript is kept only for a post-argument cell, and a stored-not-staged kind for no cell. | `provision.py`: `moment_cutoff`, `documents_for_moment`, `documents_before` | data-pipeline.md, *Provisioning: how a cell gets its record* |
| Scrub | On a docket with a self-represented side, contact details are withheld from the staged text and the staged snapshot. Where the shape pass ran, a residual detector re-reads the scrubbed text's opening and closing, and any match records the document as **not** scrubbed. The document is still staged. | `pipeline/documents.py`: `scrub_contact_details`, `contact_residual_matches`, `scrub_snapshot_contacts`; `provision.py`: `staged_scrub` | live-sources.md, from the paragraph introducing the contact-detail scrub through *What the scrub does not reach*; data-sources.md, *PII stance* |
| Stage | Each kept document is written to `record/documents/<kind>.txt`, with a manifest at `record/documents/documents.json`. | `provision.py`: `write_cell_record`, `document_manifest` | predicted-artifacts.md, *Where the files land*; cli.md, `provision-snapshot` |
| Companions | Not a document: a predict cell also gets the snapshot of each docket its placed snapshot links as `Vide`, cut by the date rule to its cutoff (or its own snapshot date where it has none) and redacted of undated outcome markers, under `record/related/` with a `related.json` listing every link. No filing text of a companion is staged. | `pipeline/vide_links.py`: `vide_docket_numbers`; `provision.py`: `place_related`, `related_manifest` | cli.md, `provision-snapshot` |

## What a cell can be given

These are the kinds, from `pipeline/documents.py`. Selection is per docket and
the moment decides by date, so a cell gets every kind below that its docket
carries and that was filed before its cutoff. The one exception is the argument
transcript, which only a post-argument cell is given. The kinds in the second
table below are stored and given to no cell.

| Kind | Filing | Docket |
| --- | --- | --- |
| `petition` | The case-opening filing on a cert-form docket: a certiorari petition, or a mandamus, prohibition or habeas petition, or a direct appeal's jurisdictional statement | Cert |
| `questions-presented` | The questions presented, cut from the petition text | Cert |
| `appendix` | The opening filing's or application's separately linked appendix | Cert, Application |
| `brief-in-opposition` | Every respondent's opposition, combined into one row | Cert |
| `cert-reply` | The petitioner's reply to the opposition | Cert |
| `sg-invited-brief` | The Solicitor General's brief when the Court called for it | Cert |
| `merits-brief-petitioner`, `merits-brief-respondent` | Each side's brief on the merits | Granted |
| `merits-reply-petitioner`, `merits-reply-respondent` | Each side's reply on the merits | Granted |
| `argument-transcript` | The oral argument transcript, from the Court's per-Term list rather than the docket | Argued |
| `application` | The application to a Justice or the Court | Application |
| `application-response` | The first response to the application | Application |
| `application-reply` | The applicant's reply to it | Application |

Three more kinds are **stored but not yet given to any cell**. Which kinds a cell
reads is part of its information set, and the process digest does not see it
([process-version.md](process-version.md)), so a new kind is fetched and stored
first and staged only in the re-bless whose prompt tells cells about it. Until
then `provision.WITHHELD_KINDS` keeps it from every cell at every moment, and
the case-summary plan leaves it out of the record it reads.

| Kind | Filing | Docket |
| --- | --- | --- |
| `supplemental-brief` | Every party's Rule 15.8 supplemental brief while the petition is pending, combined into one row | Cert |
| `party-letter` | Every party's letter to the Clerk bearing on the case while the petition is pending (mootness, settlement, withdrawal, an intervening decision), combined into one row | Cert |
| `merits-amicus-united-states` | The United States' amicus brief on the merits, filed after the grant | Granted |

Amicus briefs other than the United States' are never selected: the Solicitor
General's invited brief at the cert stage, and the United States' brief on the
merits after the grant. A cell with retrieval rights can still reach the others
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

- **A combined opposition is kept or dropped whole.** It is dated by its
  earliest brief, so a cutoff between two respondents' briefs admits the later
  one (`documents_before`).
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
- **A consolidated member is checked for freshness on its own docket.** A merits
  filing entered only on the lead is left to the selection sweep
  (live-sources.md, *Document freshness*).

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
- `fedcourts backfill-documents` and `fedcourts ocr-recover-petitions` each
  dry-run by default, listing the cases and documents they would fetch or
  recover.
- A single cell's manifest says what that cell got: `empty_text`, `truncated`,
  `ocr_derived` and the contact fields per staged kind.

The last measured empty-text figures, with their date and frame, are in
live-sources.md, *How large the degradation is*. Quote a figure with the vintage
`corpus-info` prints beside it.
