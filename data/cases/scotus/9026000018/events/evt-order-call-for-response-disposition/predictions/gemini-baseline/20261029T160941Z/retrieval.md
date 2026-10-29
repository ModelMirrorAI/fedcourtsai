# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 34 GET(s), 8716288 byte(s)`
   - Result: Returned 10 recent granted SCOTUS priors from the 2020s era (including paid cert petitions and substantive applications) for calibration context.

2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent SCOTUS GVR priors from the 2020s era (including Fifth Circuit GVR priors).

3. `uv run fedcourts query --court ca5 --citation "88 F.4th 1119"`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 0 rows (`note: citations filter: only 0 row(s) in scope (ca5) carry any reporter citation at all`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(citation="88 F.4th 1119", type="o", fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"])`
   - Result: Failed with HTTP 429 rate-limit error (`Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 7937 seconds.'}`). Fell back to the provisioned petition and Fifth Circuit appendix opinions, which discuss and quote *Smith v. Edwards*, 88 F.4th 1119 (5th Cir. 2023), at length.

## Web Searches

- None attempted.
