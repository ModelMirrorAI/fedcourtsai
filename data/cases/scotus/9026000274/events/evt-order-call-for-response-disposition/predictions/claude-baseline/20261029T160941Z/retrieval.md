# Retrieval

- `uv run fedcourts query --help`: read the usage.
- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5`: refused, because `roberts` is not an era token. No reads.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` returned 5 recent granted SCOTUS rows, none of them on this question. `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
- Read the committed `metrics/statpack.md` (salience band table).

No CourtListener MCP calls and no web searches.
