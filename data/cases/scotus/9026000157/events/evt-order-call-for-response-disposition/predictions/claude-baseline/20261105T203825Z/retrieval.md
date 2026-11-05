# Retrieval

- `uv run fedcourts query --court scotus --docket-number 25-849`
  - `ranged corpus reads: 14 GET(s), 3670016 byte(s)` (first run); rerun printed `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Returned USCCB v. O'Connell: denied 2026-05-26, distribution_count 4, many amici.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3` — usage error (unknown era 'modern').
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3`
  - `ranged corpus reads: 20 GET(s), 5242880 byte(s)`; output not used beyond confirming the filter works.
- Read `metrics/statpack.md` (relist, CVSG, amicus cuts).
- No CourtListener MCP calls, no web searches.
