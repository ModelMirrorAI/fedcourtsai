# Retrieval Log

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Stderr transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 5 recent 2020s SCOTUS denied rows (mostly October 2026 substantive applications).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Stderr transfer line: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   - Returned 5 recent 2020s SCOTUS granted rows (including OT 2026 cert grants `26-12`, `26-204`, and `25-1103`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Johnson v. NPAS Solutions"`, `num_results=10`, `fields=["caseName", "dateFiled", "citation", "court", "docketNumber", "status"]`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 12896 seconds.'}`

2. `mcp_courtlistener_search` (`type="o"`, `case_name="Scott v. Dart"`, `num_results=10`, `fields=["caseName", "dateFiled", "citation", "court", "docketNumber", "status"]`)
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 12896 seconds.'}`

## 3. Web Searches

None attempted.
