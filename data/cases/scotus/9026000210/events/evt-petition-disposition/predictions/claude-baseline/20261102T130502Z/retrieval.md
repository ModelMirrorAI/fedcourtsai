# Retrieval log

- Read `metrics/statpack.md` (relist, CVSG, amicus cuts; sal-v6 salience-band table).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. Usage error: "Unknown era 'modern'". No rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`. Stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned recent granted SCOTUS rows, several of them SG petitions (e.g. DOJ v. McNutt, FCC v. Brown). Used only as general context.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`. Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`. Returned unrelated 26A applications. Not used.
- No CourtListener MCP or web lookups.
