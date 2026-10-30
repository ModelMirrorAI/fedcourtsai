# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: failed with a usage error (the flag was not accepted), returned no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned recent (OT2025–26) granted applications and petitions. Not similar to this case and not used substantively.
- Read `metrics/statpack.md`, interim docket section (committed file).
- No CourtListener MCP or web calls.
