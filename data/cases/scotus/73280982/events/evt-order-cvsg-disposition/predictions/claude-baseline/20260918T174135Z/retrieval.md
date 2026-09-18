# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-06-02.json`,
`record/documents/documents.json`, `questions-presented.txt` (mis-cut; see flags),
`petition.txt` (QP page, reasons for granting, vehicle section), `brief-in-opposition.txt`
(introduction, QP page, vehicle section), and the committed `metrics/statpack.md`
(salience-band table, CVSG cut, relist cut, circuit cut).

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned four OT2026 emergency applications and four OT2025 plenary grants, none
  securities-related; no case-specific prior used.

## CourtListener MCP lookups

- `get_endpoint_item` dockets/73280982 (fields: id, case_name, docket_number, court_id,
  date_filed, date_terminated, date_last_filing, date_modified): case not terminated;
  `date_modified` 2026-06-01. Used to confirm the petition is still pending (forward cell).
- `call_endpoint` docket-entries, docket=73280982, newest first: 0 entries. Post-baseline
  docket state (whether the SG brief has been filed) could not be confirmed.
- `search` type=o, q="Sodha Robinhood", court=ca9: one result, *Sodha v. Golubowski*,
  No. 24-1036, filed 2025-08-29, status Published. Used to confirm the decision below is
  published.

No web searches.
