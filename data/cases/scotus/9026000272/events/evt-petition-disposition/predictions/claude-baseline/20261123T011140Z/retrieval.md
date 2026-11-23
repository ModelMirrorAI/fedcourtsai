# Retrieval log

- `uv run fedcourts query --help` (usage text only).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (the `--era` value was not accepted); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: 5 rows returned (recent granted SCOTUS dockets, including two federal-petitioner matters). stderr: `ranged corpus reads: 35 GET(s), 9043968 byte(s)`. Used only as general context; no row bears on this question.
- `metrics/statpack.md`: salience-band table, per-Term band table (federal column), relist-count cut.
- No CourtListener MCP calls and no web searches.
