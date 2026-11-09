# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` → usage error ("Unknown era 'modern'"); re-issued with a decade token.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` → `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. Returned five recent granted SCOTUS rows, none on the ADA; used only as a shape check.
- Read committed `metrics/statpack.md` (modern cert disposition, circuit, relist, CVSG, amicus and sal-v8 band tables).
- No CourtListener MCP calls and no web searches.
