# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era roberts` — usage error (era must be a decade token); no corpus read.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 3` — `ranged corpus reads: 4 GET(s), 1048576 byte(s)`; returned unrelated capital/immigration applications, not used.
- Read `metrics/statpack.md` (salience-band table; relist-count cut).
- No CourtListener MCP or web calls.
