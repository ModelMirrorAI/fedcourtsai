# Retrieval

- CourtListener MCP opinion search for `"Rico v. United States"`, limited to SCOTUS opinions filed before 2026-08-16. The server returned HTTP 429 (daily rate limit exceeded); no result informed the prediction.
- CourtListener MCP opinion search for `"Seven County Infrastructure Coalition" "Eagle County"`, limited to SCOTUS opinions filed before 2026-08-16. The server returned HTTP 429 (daily rate limit exceeded); no result informed the prediction.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '607 U.S. 609' --limit 1 --full` — returned no row and printed no `ranged corpus reads` line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '605 U.S. 168' --limit 1 --full` — returned no row and printed no `ranged corpus reads` line.
- `metrics/statpack.md`, “The merits docket (granted cases),” used for the strictly-prior grant-Term disturbed-rate anchor.
