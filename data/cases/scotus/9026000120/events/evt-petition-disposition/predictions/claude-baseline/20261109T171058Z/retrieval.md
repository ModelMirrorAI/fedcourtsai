# Retrieval
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: rejected with a usage error (`--era` with this form); nothing came back.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
  - Returned 5 recent granted SCOTUS rows (e.g. Goldman Sachs Bank USA v. ..., DOJ v. McNutt). These were used as general context only; none is related to this case.
- Read `metrics/statpack.md`: the salience-band table, the relist-count cut and the amicus-count cut.
- No CourtListener MCP calls and no web searches.
