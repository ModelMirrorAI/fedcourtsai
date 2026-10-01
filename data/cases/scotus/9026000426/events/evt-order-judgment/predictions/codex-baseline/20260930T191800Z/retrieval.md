# Retrieval record

## Provisioned baseline

Read this cell's event definition, `record/context.json`, `record/snapshots/2026-09-29.json`, and `record/documents/documents.json` and `application.txt`. Read the prediction contract and output schemas. No other predictor output, outcome artifact, or topic-labeling artifact was consulted.

## Committed statistical context

Read the merits-docket section of `metrics/statpack.md`, including its exclusion and coverage rules. A preliminary heading search also surfaced nearby interim table rows; those were not used. Inspected only the top-level keys of `metrics/statpack.json`. Computed the 2015–2024 grant-Term pool from the merits table with Python: 360 disturbed, 516 parsed, 539 granted, and 56 excluded. Checked the statpack file's repository vintage with `git log -1 --format='%h %cI' -- metrics/statpack.md`: `808f812e9 2026-09-28T12:02:50Z`.

No `fedcourts query` or `open-events` call was made. There are no ranged-corpus transfer lines to report. `fedcourts paths --court scotus --docket 9026000426 --event evt-order-judgment --role predictor` initially failed on the default cache location and then succeeded with a writable temporary cache. This was path resolution, not a corpus lookup.

## Web attempts

Three direct `web.run` opens returned no usable content; no general web search was made:

- `https://www.law.cornell.edu/uscode/text/8/1252` — attempted statutory-text check; no content used.
- `https://www.supremecourt.gov/opinions/21pdf/20-322_m6hn.pdf` — attempted direct read of the 2022 *Aleman Gonzalez* opinion; no content returned.
- `https://www.supremecourt.gov/DocketPDF/26/26-426/425859/20260928154306895_Opp%20Stay%20v4%20FINAL.pdf` — attempted read of the September 28, 2026 opposition already linked in the snapshot; subsequently retrieved as described below.

## CourtListener MCP

1. `search(type="o", citation="596 U.S. 543", num_results=1)` returned *Garland v. Gonzalez / Aleman Gonzalez*, filed June 13, 2022, opinion ID `6349227`, cluster ID `6477116`.
2. `search_document(opinion_id=6349227, query="declaratory", snippet_size=1600)` returned passages including the majority's footnote 2 reserving the declaratory-relief question and the separate opinion's discussion of that distinction. These informed the uncertainty around extending the classwide-injunction holding. No search of this cell's case or subsequent history was made.

## Official pre-grant opposition

Used the exact opposition PDF address listed above, taken from the provisioned September 28 docket entry. An initial `curl` pipe failed because `pdftotext` was unavailable; curl reported a broken output destination. Then fetched the PDF into memory using Python `urllib.request` and extracted text with the installed `pypdf.PdfReader`, without saving any extra files.

Six successful reads of the same 42-page PDF extracted these zero-based page slices: `[0:6]`, `[14:19]`, `[19:23]`, `[23:27]`, `[27:31]`, and `[31:34]`. These cover the cover/contents and printed pages 1–4, then printed pages 13–32. Some long displayed outputs were truncated; I do not claim a complete read of the brief. The usable text supplies respondents' opposing arguments on remedies, channeling, statutory rights, due process, diplomatic assurances, and the limits of inferring merits outcomes from stays.

All successfully retrieved case-specific advocacy predates the grant and the baseline cutoff. No later disposition, later merits briefing, or decision coverage was requested or encountered.
