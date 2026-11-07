# Retrieval

- `uv run fedcourts query --help` (usage only).
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`: usage error (`modern` is not an era value).
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 3`
  - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - It returned unrelated recent applications (Guardado v. Florida, etc.), which were not informative.
- Read the committed `metrics/statpack.md` (salience band table, sal-v7).
- No CourtListener MCP or web calls.
