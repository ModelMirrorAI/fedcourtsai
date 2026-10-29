# Retrieval Log

## 1. Corpus CLI Lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`
   - Result: Returned 10 recent resolved/granted SCOTUS rows from the 2020s era (including OT2025/OT2026 grants) for general context on recent grant patterns.

2. `uv run fedcourts query --court scotus --citation "579 U.S. 261" --citation "584 U.S. 357" --citation "590 U.S. 45"`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 0 rows with the sparse-filter note (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="cafc"`, `case_name="Dolby Unified Patents"`, `num_results=5`, `fields=["caseName", "dateFiled", "citation", "docketNumber", "snippet"]`)
   - Result: Failed with HTTP 429 rate-limit error (`Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 13621 seconds.'}`).

2. `mcp_courtlistener_search` (`type="o"`, `court="cafc"`, `case_name="Ethanol Boosting Ford"`, `num_results=5`, `fields=["caseName", "dateFiled", "citation", "docketNumber", "snippet"]`)
   - Result: Failed with HTTP 429 rate-limit error (`Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 13621 seconds.'}`).

## 3. Web Searches

None attempted.
