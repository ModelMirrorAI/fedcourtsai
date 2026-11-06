# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` → usage error (`--era` value rejected or flag combination; printed help); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` → `ranged corpus reads: 31 GET(s), 8126464 byte(s)`; returned recent granted rows (mostly federal-government applications). Not on point; did not shape the forecast.
- Read the committed `metrics/statpack.md` (salience band table, sal-v7) to cross-check `cert_anchor`.
- No CourtListener MCP calls and no web searches.
