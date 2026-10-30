# Retrieval

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: usage error, nothing returned.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`: returned 5 recent GVR priors, read for shape only.
  - `ranged corpus reads: 31 GET(s), 8060928 byte(s)`
- `uv run fedcourts query --docket-number 20-1369`: usage/help output, no row returned (tried twice).
- Committed `metrics/statpack.md` read for base rates (sal-v4 band table, relist/CVSG/circuit cuts).
- No CourtListener MCP calls and no web searches.
