# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5`: usage message only (I did not inspect which flag was rejected); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: returned 5 recent granted SCOTUS rows (unrelated cases; not used substantively).
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
- Committed `metrics/statpack.md` read for base rates (salience-band table, relist/CVSG/amicus/circuit cuts).

No CourtListener MCP calls and no web searches.
