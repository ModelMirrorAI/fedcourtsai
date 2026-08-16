# Retrieval

- CourtListener MCP search: RECAP collection, First Circuit docket `26-1774`, filed before `2026-08-16`. The server returned HTTP 429 (daily rate limit exceeded); no result informed the forecast.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --include-applications --limit 20`
  - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - Consulted for recent application priors; the returned rows did not provide a response-request-conditioned comparison.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court ca1 --include-open --limit 20`
  - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - Consulted for the lower-court matter; the target docket did not appear in the returned rows.
- `metrics/statpack.md`, “The interim docket (applications),” for the registered strictly prior-Term base rate and escalation-shape counts.
