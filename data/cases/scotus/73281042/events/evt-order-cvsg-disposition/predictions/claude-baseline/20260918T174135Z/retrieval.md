# Retrieval log

Beyond the provisioned inputs (snapshot `2026-06-23.json`, `context.json`, `event.yaml`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6`
   stderr: `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   Returned six recent grants (four OT2026 emergency applications 26A326, 26A274, 26A203, 26A124, plus 25-246 Jouppi v. Alaska and 25-238 Viramontes v. Cook County). No topical filter is available, so these were not similar priors and did not move the forecast.
2. `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 4`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned four recent denials (26A337, 26A332, 26A353, 26A305). Same caveat.

An initial attempt passed a free-text argument and was rejected by the CLI (it takes flags only); no corpus read occurred.

## CourtListener MCP lookups

1. `get_endpoint_item` on `dockets` id 73281042 (fields: dates, case name, docket number). Result: docket 25-1002, filed 2026-02-24, `date_cert_granted` and `date_cert_denied` null, `date_modified` 2026-06-22. No disposition.
2. `call_endpoint` on `docket-entries` for docket 73281042 with `date_filed >= 2026-06-22`. Result: 0 entries. Read as a coverage lag on CourtListener's SCOTUS docket feed, not as evidence about the docket.

## Web search

1. Query: `Saadeh v. New Jersey State Bar Association Supreme Court 25-1002 Solicitor General brief`. Results were the SCOTUSblog case page, the supremecourt.gov docket and filings (petition, BIO, reply, lodging letter), the States' amicus brief, and the Manhattan Institute amicus page. No Solicitor General brief and no disposition surfaced; nothing postdating the snapshot was learned.
