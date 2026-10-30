# Retrieval Log (`retrieval.md`)

## 1. Local CLI / Corpus Queries
- `uv run fedcourts paths --court "scotus" --docket "9026000339" --event "evt-order-call-for-response-disposition" --role predictor`
  - Resolved case, corpus, and event paths.
- `uv run fedcourts query --help`
  - Checked structured filter flags for `fedcourts query`.
- `uv run fedcourts query --court scotus --docket-number 26-339`
  - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
  - Returned the corpus row for `scotus/9026000339` (showing `salience_score: 0.0334`, `salience_version: "sal-v4"`, `distributed_for_conference: "2026-10-16"`, `distribution_count: 1`, `disposition: null`).
- `uv run fedcourts query --court scotus --disposition granted --limit 10`
  - `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
  - Returned 10 recent granted SCOTUS rows in the 2020s era for prior comparison.
- `uv run fedcourts query --court scotus --originating-court ca4 --era 2020s --limit 15`
  - Failed with usage error (`No such option: --originating-court`).
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 10`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm local corpus service cache)
  - Returned 10 recent denied SCOTUS rows in the 2020s era.

## 2. CourtListener MCP Calls
- `mcp_courtlistener_search(type="o", case_name="FS Medical Supplies v. Tanner Pharma", fields=["caseName", "citation", "dateFiled", "docketNumber", "id", "cluster_id", "opinions"])`
  - Returned error: `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 12220 seconds.'}`
- `mcp_courtlistener_search(type="d", docket_number="3:25-cv-00102", fields=["caseName", "court_id", "docketNumber", "dateFiled", "dateTerminated", "docket_id"])`
  - Returned error: `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 12220 seconds.'}`

## 3. Web Searches
- None attempted.
