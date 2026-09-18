# Retrieval log — claude-baseline, run 20260917T214606Z

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  Used for the shape of recent granted priors (counsel, government parties,
  amici), not for any case-specific fact.

## CourtListener MCP lookups

- `get_endpoint_item` on `dockets` id 73369988 (fields: dates, case name,
  docket number). Result: docket 25-1298, filed 2026-05-20, last modified
  2026-07-01, no cert grant or denial recorded, not terminated. Confirms the
  cell is a pending petition and that nothing has moved since the snapshot.
- `search` type `o`, query `Honeycutt JPMorgan Chase arbitration`, courts
  `calctapp`, `cal`. Zero results.
- `search` type `o`, query `"Honeycutt" "JPMorgan Chase"`, no court filter.
  Returned the 2018 published Honeycutt I opinion (25 Cal. App. 5th 909,
  B281982) and unrelated California arbitration cases. The 2025 unpublished
  opinion under review (B331199) is not indexed, so it was not read.

## Web searches

None.

## Base rates

Committed `metrics/statpack.md`: the sal-v4 "Segment base rate by salience
band" table (baseline band, bracketed `reached` figures, OT2017 through
OT2024), the relist-count and CVSG cuts of the paid scored segment, the
originating-court table, the per-Term cert table, and the modern
discretionary-cert disposition table.
