# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1217 --include-open`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: `scotus/73281701` (*In Re Justin Paul Dreiling*, No. 25-1217), filed 2026-04-24, distributed once (2026-06-18), denied 2026-06-22.
2. `uv run fedcourts query --court scotus --docket-number 26-9 --include-open`
   - Transfer: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Result: `scotus/9026000009` (*Justin Paul Dreiling v. United States*, No. 26-9, originating from CAFC No. 2025-2155), filed 2026-07-02, distributed once (2026-09-28), denied 2026-10-05.

*(Two initial invocations of `uv run fedcourts query` with positional text arguments exited with usage code 2 before any corpus read.)*

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Dreiling v. United States", fields=["caseName", "court", "docketNumber", "dateFiled", "citation", "cluster_id"], num_results=10)` — failed with HTTP 429 rate limit exceeded.
2. `mcp_courtlistener_search(type="o", case_name="Newman v. Moore", fields=["caseName", "court", "docketNumber", "dateFiled", "citation", "cluster_id"], num_results=10)` — failed with HTTP 429 rate limit exceeded.

## Web Searches

None.
