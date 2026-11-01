# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`: usage error (invalid flag/value). Re-issued without `--era`.
- `uv run fedcourts query --court scotus --disposition denied --limit 3`: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`. Returned three unrelated recent denials. Not relied on.
- `uv run fedcourts paths ... --role predictor`: path resolution only.
- Read `metrics/statpack.md` (salience-band table, relist-count cut).
- No CourtListener MCP calls and no web searches.
