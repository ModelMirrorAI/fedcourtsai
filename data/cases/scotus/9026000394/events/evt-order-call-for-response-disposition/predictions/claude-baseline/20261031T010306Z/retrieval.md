# Retrieval log

- `uv run fedcourts query --docket-number 25-1013` → usage error (needs `--court`); no corpus read.
- `uv run fedcourts query --docket-number 23-675` → same usage error.
- `uv run fedcourts query --court scotus --docket-number 25-1013` → `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Bestwall (No. 25-1013): denied 2026-06-01, distribution_count 1, no CVSG.
- `uv run fedcourts query --court scotus --docket-number 25-1013` (re-run to parse fields; stderr suppressed) → same row.
- `uv run fedcourts query --court scotus --docket-number 23-675` → `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Bestwall (No. 23-675): denied 2024-05-13, distribution_count 1.
- Read `metrics/statpack.md` (relist, amicus and salience-band cuts).
- No CourtListener MCP calls and no web searches.
