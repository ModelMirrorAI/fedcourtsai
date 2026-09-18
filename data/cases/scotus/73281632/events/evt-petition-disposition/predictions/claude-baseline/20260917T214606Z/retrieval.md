# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  - stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  - Returned four 2026 stay applications (26A-series) and four OT2025 plenary grants (25-246, 25-238, 25-566, 25-965); no topical overlap with FHFA or the Appropriations Clause, so it did not inform the forecast.
- Base rates: committed `metrics/statpack.md` (sal-v4 band table pooled over Terms 2017–2024; relist-count, CVSG, and originating-circuit cuts for shape).

## CourtListener MCP

1. `search` (type `o`, q `"Federal Housing Finance Agency" "Appropriations Clause" 4516`, filed after 2024-05-01): three hits, the Ninth Circuit opinion below (cluster 10768269) and two entries for *CFPB v. CFSA*, 601 U.S. 416. No other circuit decision on FHFA funding.
2. `search` (type `d`, court `scotus`, q `"Federal Housing Finance Agency" Appropriations`, filed after 2025-06-01): zero results, so no companion petition surfaced.
3. `get_endpoint_item` (clusters, 10768269): confirmed published status, date filed 2026-01-02, one sub-opinion (11234854).
4. `search` (type `d`, court `scotus`, q `"Saticoy Bay" OR "Haddad" OR "Federal Housing Finance Agency"`, filed after 2025-01-01): zero results.
5. `read_document` (opinion 11234854, chunks 0–1 of 7): panel Bennett, Sanchez, H.A. Thomas; opinion by Judge H.A. Thomas; no separate writing indicated; argued October 8, 2025; statutory background on 12 U.S.C. § 4516.

No web searches. Nothing retrieved disclosed this petition's disposition; it remains set for the September 28, 2026 conference.
