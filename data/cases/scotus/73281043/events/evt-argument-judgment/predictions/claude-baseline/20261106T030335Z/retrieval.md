# Retrieval log

- `uv run fedcourts query --help`: read the usage.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
  - It returned five recent granted SCOTUS rows (election, DOGE and FCC matters). None was on point, and none shaped the forecast.
- Read the committed `metrics/statpack.md`, specifically the merits docket section and the per-Justice merits votes.
- No CourtListener MCP calls. No web searches.
