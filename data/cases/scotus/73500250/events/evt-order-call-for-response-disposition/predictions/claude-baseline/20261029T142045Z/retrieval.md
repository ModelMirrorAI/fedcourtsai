# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` — rejected with a usage error (`--era` value not accepted in this form); re-issued below.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
  - Returned recent granted SCOTUS rows (government-party and application dockets); none on § 242 or § 1519, so not used beyond confirming the surface.
- `uv run fedcourts query --help` (usage only).
- Read committed `metrics/statpack.md` for base rates.
- No CourtListener MCP calls and no web searches.
