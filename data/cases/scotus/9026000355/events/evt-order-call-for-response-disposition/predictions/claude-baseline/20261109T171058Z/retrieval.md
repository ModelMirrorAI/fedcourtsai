# Retrieval
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: printed the usage/help text instead of results; I did not pass a valid flag combination.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: returned 5 recent granted SCOTUS rows, none on point. `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
- Read `metrics/statpack.md`: the salience band table (sal-v8) and the relist-count cut.
- No CourtListener MCP calls and no web searches.
