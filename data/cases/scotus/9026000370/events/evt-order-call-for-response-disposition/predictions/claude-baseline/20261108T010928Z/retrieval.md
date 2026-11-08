# Retrieval log

- Read `metrics/statpack.md` (modern cert, originating circuit, relist, CVSG, amicus, salience band sections; sal-v8 band table).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (no `--limit` on this surface as spelled with `--era`; printed help). No transfer line.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. Returned recent OT2025/OT2026 granted dockets (mostly federal-government petitions and applications); none on point, used only as a sanity check.
- No CourtListener MCP calls and no web searches.
