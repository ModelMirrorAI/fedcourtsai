# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 73281057 --event evt-order-cvsg-disposition --role predictor` — path resolution only.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned 8 rows, 4 of them emergency applications (26A-series) and 4 granted OT2025 cert petitions with no CVSG; no CVSG'd comparables surfaced.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 8`
  stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
  Returned 8 rows, all 26A-series applications. Not used for anchoring.
- `metrics/statpack.md` (committed): modern discretionary-cert disposition table; relist-count and CVSG-status cuts (paid scored segment); per-Term table; "Segment base rate by salience band (sal-v4)" table, pooled over OT2017–OT2024 for the `high` band's bracketed `reached` rate.

## CourtListener MCP

- `call_endpoint docket-entries` with `docket=73281057`, ordered by date descending — returned 0 entries (CourtListener carries no entries for this SCOTUS docket).
- `get_endpoint_item dockets 73281057` (fields: id, case_name, docket_number, date_filed, date_terminated, date_last_filing, date_modified) — docket 25-1018, filed 2026-02-24, `date_terminated` null, last modified 2026-06-22.

## Web

- Fetched `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1018.html` (forward mode; the case's own live docket) to check for post-snapshot entries. The Proceedings and Orders list ends at the June 22, 2026 CVSG; no Solicitor General brief, redistribution, or disposition appears. Content identical to the provisioned snapshot.

No other searches.
