# Retrieval log

- `uv run fedcourts query --help` (usage read).
- `uv run fedcourts query --court scotus --citation "489 U.S. 538" --limit 5`
  - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. Empty, with a note that
    the citations column is sparse.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`
  - Usage error, so no reads.
- `uv run fedcourts query --court scotus --disposition granted --limit 3`
  - `ranged corpus reads: 17 GET(s), 4456448 byte(s)`. Returned recent OT2025/26
    grants, none of them relevant priors.
- Read the committed `metrics/statpack.md` (salience band table, relist and CVSG cuts).
- No CourtListener MCP or web calls.
