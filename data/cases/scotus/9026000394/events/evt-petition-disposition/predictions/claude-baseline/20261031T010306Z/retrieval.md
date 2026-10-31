# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` → usage error (help text printed); no rows.
- `uv run fedcourts query --court scotus --docket-number 26A66` → `ranged corpus reads: 12 GET(s), 3145728 byte(s)`; returned the linked extension application row (scotus/9526000066), no new signal.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3` → usage error (help text printed); no rows.
- `uv run fedcourts query --court scotus --disposition denied --limit 3` → `ranged corpus reads: 5 GET(s), 1310720 byte(s)`; unrelated recent applications, not used.
- Read `metrics/statpack.md` (salience band table, relist and amicus cuts).
- No CourtListener MCP or web lookups.
