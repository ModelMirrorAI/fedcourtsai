# Retrieval log

## Corpus (fedcourts, via the cell's corpus service)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
  Returned 8 rows: two cert dockets (25-1131, 2 distributions; 25-1349, 1 distribution, docketed
  2026-06-03) and six emergency applications. Used only to notice 25-1349 as a long-conference
  neighbour.
- `metrics/statpack.md` (committed): "Modern discretionary-cert petitions by disposition",
  "by originating circuit", "by relist count", "by CVSG status", "by salience band", "SCOTUS cert
  petitions by Term", and "Segment base rate by salience band (sal-v4)" (federal column pooled over
  OT2017 to OT2024).

## CourtListener MCP

- `search` (type `o`, court `ca4`, q `Ozurumba`): one result, Izuchukwu Ozurumba v. Pamela Bondi,
  No. 24-2070, filed 2025-09-02, published, cluster 10665527, opinion 11132114.
- `search` (type `d`, court `scotus`, docket_number `25-1343`): no results.
- `read_document` opinion 11132114, chunks 0-3 and 4-11 (full text of the majority and dissent).

## Web fetches (forward mode)

- https://www.supremecourt.gov/docket/docketfiles/html/public/25-1349.html — neighbouring docket
  (Marschner v. Marschner, N.D. Sup. Ct.); shows "Petition GRANTED" dated October 1, 2026 after
  the 9/28/2026 conference. Used to date the long-conference grant tranche.
- https://www.supremecourt.gov/docket/docketfiles/html/public/25-1343.html — this case's own
  docket as of 2026-10-03; no entry after the 8/19/2026 distribution. No disposition surfaced.

No other web searches were run. Nothing under `data/qp-topics/` was read.
