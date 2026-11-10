# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error, because `modern` is not a valid era value. No results.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
  - Returned recent grants, including DOJ v. McNutt (26-204), an SG petition granted at distribution_count 2.
- Read the committed `metrics/statpack.md`: the relist-count cut and the sal-v8 salience-band table.
- No CourtListener MCP calls and no web searches.
