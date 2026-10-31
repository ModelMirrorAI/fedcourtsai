# Retrieval log

- `uv run fedcourts query --court scotus --citation "540 U.S. 398" --limit 3` — stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No rows; the note says the citation column is sparse.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 3` — usage error (the era value was not accepted); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 3` — stderr: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`. Three recent granted rows, none on point. Used only as a sanity check.
- Read the committed `metrics/statpack.md` (salience-band table, relist, CVSG and amicus cuts).
- No CourtListener MCP calls and no web searches.
