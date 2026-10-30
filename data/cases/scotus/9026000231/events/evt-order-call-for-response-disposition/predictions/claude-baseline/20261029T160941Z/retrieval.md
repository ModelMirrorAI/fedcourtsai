# Retrieval

- `uv run fedcourts query --court scotus --citation "593 U.S. 420" --limit 3`
  → `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. Returned no rows, with a
  note that the citation column is sparse (200 rows in scope).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`
  → refused as a usage error (unknown era), so nothing was read.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  → `ranged corpus reads: 24 GET(s), 6291456 byte(s)`. Returned five recent
  grants (applications and civil cases), none relevant to ACCA.
- Read the committed `metrics/statpack.md`: the band table, relist cut, CVSG cut
  and amicus cut.
- No CourtListener MCP calls and no web searches.
