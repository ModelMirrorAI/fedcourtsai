# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --limit 5`
  - stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  - It returned generic recent SCOTUS rows (substantive applications), which did not bear on this petition.
- I read the committed `metrics/statpack.md`: the sal-v8 salience-band table, the relist-count cut and the CVSG cut.
- No CourtListener MCP lookups and no web searches.
