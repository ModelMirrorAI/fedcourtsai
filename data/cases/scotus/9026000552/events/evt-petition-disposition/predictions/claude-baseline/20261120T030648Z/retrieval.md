# Retrieval log

- Read `metrics/statpack.md` (salience-band tables, originating-court cut).
- `uv run fedcourts query --help` — read usage.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (flag rejected); no rows.
- `uv run fedcourts query --court scotus --disposition denied --limit 5` — returned 5 recent denied rows (generic, not case-specific). stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`.
- No CourtListener MCP calls and no web searches.
