# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --disposition gvr --era 2020s`
  stderr: `ranged corpus reads: 43 GET(s), 11272192 byte(s)`
  20 rows returned (June 29 and 30, 2026 GVRs; distribution counts 2 to 4; no
  `response_requested` set on any row). Used as a shape check only.
- Committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Cert petitions by relist count (paid scored segment)",
  "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by
  salience band", "SCOTUS cert petitions by Term", and "Segment base rate by
  salience band (sal-v4)" (anchor: `baseline` bracketed `reached` rate pooled
  over OT2017 to OT2024).

## CourtListener MCP

- `search` (opinions, court scotus, q "Jules Andre Balazs Properties",
  filed after 2025-12-01): 1 hit, cluster 10858761, decided 2026-05-14.
- `read_document` opinion 11326163 (Jules v. Andre Balazs Properties),
  chunks 0 to 7: syllabus and full opinion of the Court.
- `search` (dockets, court scotus, q "Burford German Funding financialright"):
  0 hits.
- `search` (opinions, court ca3, q "financialright"): 0 hits.
- `search` (opinions, q "Burford German Funding" OR "financialright claims",
  filed after 2025-10-01): 0 hits.
- `search` (opinions, court ca3, docket_number 24-3171): 0 hits.
- `search` (opinions, court ca3, q Burford 1782 arbitration "civil action",
  Oct to Nov 2025): 0 hits.

## Web fetches (supremecourt.gov docket PDFs for No. 25-1269; text extracted
## locally after the fetch tool's summarizer could not read the PDFs)

- Brief in opposition (submitted 2026-09-14): full text read.
- Supplemental brief for petitioners (filed 2026-06-16): full text read.
- Appendix to the petition: Third Circuit opinion and dissent (1a to 21a) read;
  district court opinion skimmed.

No search surfaced this petition's own disposition; the docket stands at the
brief in opposition as of the snapshot.
