# Retrieval log

Beyond the provisioned inputs (snapshot 2026-06-23, `event.yaml`,
`record/context.json`, `record/documents/` — petition, brief in opposition,
questions presented — and the committed `metrics/statpack.md`):

## Corpus lookups

- `uv run fedcourts query --court scotus --citation "530 U.S. 640"` — 0 rows.
  stderr: `ranged corpus reads: 1335 GET(s), 349962240 byte(s)` plus a
  `note:` line stating only 159 of 590,419 in-scope rows carry citation data
  (the citation column is a known-case lookup, so the empty result is a
  coverage gap, not "no such precedent"). Not used for the forecast.

## CourtListener MCP lookups

- `call_endpoint docket-entries` for docket 73281042 (fields: date_filed,
  description) — 0 results; SCOTUS docket entries are not in RECAP.
- `call_endpoint dockets` id=73281042 (fields: id, docket_number, case_name,
  date_filed, date_terminated, date_last_filing) — confirmed docket 25-1002,
  `date_terminated: null` as of 2026-08-20 (case still pending; forward cell
  well-provisioned).
- `search` (opinions, court=scotus, filed_after=2024-01-01) for
  `"expressive association" antidiscrimination "Boy Scouts"` — 0 results;
  used as evidence that no intervening SCOTUS merits decision exists to GVR
  against (informed the `summary-disposition-route` claim).

## Web searches

None.
