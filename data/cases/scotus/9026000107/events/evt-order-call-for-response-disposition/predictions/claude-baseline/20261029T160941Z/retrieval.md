# Retrieval log

- `uv run fedcourts query --court scotus --citation "594 U.S. 474" --limit 3`
  - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
  - Returned no rows. Its note says the citation column is sparse (200 SCOTUS rows).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
  - Refused as a usage error (`modern` is not an era token). No read line was printed.
- `uv run fedcourts query --court scotus --disposition summary-reversal --era 2020s --limit 5`
  - `ranged corpus reads: 899 GET(s), 235274240 byte(s)`
  - Returned no rows.
- Base rates: committed `metrics/statpack.md` (sal-v4 band table, plus the
  relist, CVSG and amicus cuts).
- No CourtListener MCP calls and no web searches.
