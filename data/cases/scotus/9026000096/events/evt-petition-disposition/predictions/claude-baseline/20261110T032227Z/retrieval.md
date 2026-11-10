# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (`--era` value/limit form rejected; help text printed). No rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - stderr: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
  - Returned recent granted SCOTUS rows (several SG-represented). Used only as a sanity check; not decisive.
- `uv run fedcourts query --help`: usage reference.
- Read the committed `metrics/statpack.md` (modern cert disposition, relist, CVSG, amicus cuts; sal-v8 band table).
- No CourtListener MCP calls and no web searches.
