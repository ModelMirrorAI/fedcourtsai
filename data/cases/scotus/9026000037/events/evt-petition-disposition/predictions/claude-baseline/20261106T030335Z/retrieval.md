# Retrieval

- Read committed `metrics/statpack.md` (sal-v7 segment band table; relist-count and CVSG cuts).
- `uv run fedcourts query --help` (usage).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (`--era` value/flag combination refused); re-issued without `--era`.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. It returned recent granted SCOTUS dockets (mostly federal-government and application rows), none on point. Used only as general context.
- No CourtListener MCP or web searches.
