# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned eight recent SCOTUS rows, ranked by recency (26A332, 26A353, 26A305, 26-5089, 26A306, 26A326, 26A296, 26A298). Mostly September 2026 applications; no comparable pro se state-court cert priors, so not used beyond confirming the query surface.

## CourtListener MCP lookups

1. `get_endpoint_item` on `dockets`, item 73374809, fields id, case_name, docket_number, court_id, date_filed, date_terminated, date_modified, date_last_filing.
   Returned docket_number 25-1301, court scotus, date_filed 2026-05-21, date_terminated null, case_name "Walter A. Bernard v. Philip Ignelzi, Individually and in His Official Capacity". The caption does not match the provisioned snapshot (Matsumura); see `flags.json`. No disposition was surfaced.

## Web searches

None.
