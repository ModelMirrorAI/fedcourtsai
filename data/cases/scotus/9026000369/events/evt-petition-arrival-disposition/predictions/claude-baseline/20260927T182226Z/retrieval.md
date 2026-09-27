# Retrieval log

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 49 GET(s), 12713984 byte(s)`
   Returned mostly substantive application dockets (OT2025) plus a few granted cert
   petitions; no Rooker-Feldman or parental-rights prior surfaced. Not used for the
   number.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Returned recent denied OT2025 application/petition rows; not used for the number.

## CourtListener MCP lookups

1. `search` (opinions, court ca9, filed after 2026-01-01, q "Loop v. State of
   Washington Rooker-Feldman"): 0 results. The CA9 memorandum in No. 24-5020 is not
   indexed.
2. `search` (opinions, court scotus, q "T.M. University of Maryland Medical System
   Rooker-Feldman"): found No. 25-197, decided 2026-06-18 (cluster 10876934,
   opinion 11344435).
3. `search` (RECAP dockets, court wawd, docket 2:24-cv-00669): Loop v. State of
   Washington, filed 2024-05-15, terminated 2024-08-08, cause 42:1983, Judge
   Kymberly K. Evanson. Metadata only; no documents read.
4. `read_document` (opinion 11344435, chunk 0): the T.M. syllabus, to confirm its
   holding (Rooker-Feldman applies regardless of pending state appellate review).
   This decision predates the snapshot and is ordinary forward signal.
5. `search` (opinions, court ca9, docket_number 24-5020): 0 results.

## Committed base rates

- `metrics/statpack.md`: "Segment base rate by salience band (sal-v4)" Term table,
  pooled baseline bracketed `reached` over OT2017–OT2025 = 5.0% (n=12,720);
  relist-count, CVSG, originating-circuit (ca9: granted 2.1%, gvr 1.1%) cuts and
  the per-Term table read for shape.

No web searches. This case's own disposition was never sought.
