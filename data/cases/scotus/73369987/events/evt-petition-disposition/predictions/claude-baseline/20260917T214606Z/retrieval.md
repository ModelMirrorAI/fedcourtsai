# Retrieval log

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --disposition denied`
  stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
  Returned recent denied emergency applications (26A-series) ranked by
  recency; no comparable pro se family-law cert priors surfaced. Not used in
  the forecast.

## CourtListener MCP

- `search` type=d court=scotus docket_number=19-356 (fields: caseName,
  docketNumber, dateFiled, dateTerminated, docket_id, absolute_url) — 0 results.
- `search` type=d court=scotus docket_number=23-1244 (same fields) — 0 results.
- `search` type=d court=scotus q="Samuel Collin Robinson" OR "Collin Robinson"
  — 0 results.

All three were attempts to confirm the disposition of the petitioner's two
earlier petitions in the same custody dispute, both of which predate the
snapshot. The index holds no rows for them; the petition's own statement that
both were denied is the source relied on.

## Web

None.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "SCOTUS cert petitions by Term", and
  "Segment base rate by salience band (sal-v4)" (baseline column, bracketed
  `reached` figures pooled over OT2017–OT2024).
