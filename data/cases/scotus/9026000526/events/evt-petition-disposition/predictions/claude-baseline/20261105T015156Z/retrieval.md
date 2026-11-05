# Retrieval log

- `uv run fedcourts query --court scotus --citation "568 U.S. 313" --limit 5`
  - `ranged corpus reads: 10 GET(s), 2621440 byte(s)` — no rows; note that the citation column is sparse (200 rows).
- `uv run fedcourts query --court scotus --era modern --disposition gvr --limit 3`
  - usage error: unknown era `modern` (vocabulary is decade tokens); no reads.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 27 GET(s), 7077888 byte(s)` — five recent granted dockets (mostly federal-government cases); not on point.
- Read `metrics/statpack.md` (salience band table, relist/CVSG/amicus cuts).
- No CourtListener MCP calls; no web searches.
