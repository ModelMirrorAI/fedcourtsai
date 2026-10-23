# Retrieval

- `uv run fedcourts query --court scotus --docket-number 26-159`
  - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Result: Protopapas v. Whittaker Clark & Daniels (from CA3), filed 2026-08-03, not distributed, no response requested; last live poll 2026-10-17.
- `uv run fedcourts query --court scotus --docket-number 26-263`
  - `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Result: Official Committee of Talc Claimants v. Whittaker (from CA3), filed 2026-09-08, not distributed; last live poll 2026-10-17.
- Read the committed `metrics/statpack.md`: the sal-v4 band table, the relist cut, and the CVSG cut.
- No CourtListener MCP calls and no web searches.
