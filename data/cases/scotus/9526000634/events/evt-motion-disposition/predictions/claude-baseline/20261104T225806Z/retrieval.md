# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5` — usage error (printed help; flag combination rejected), no rows.
- `uv run fedcourts query --docket-number 26-6051` — usage error (needs --court), no rows.
- `uv run fedcourts query --court scotus --disposition denied --limit 5`
  - `ranged corpus reads: 5 GET(s), 1310720 byte(s)` — five recent OT2026 substantive applications (non-capital, unrelated); shape only.
- `uv run fedcourts query --court scotus --docket-number 26-6051`
  - `ranged corpus reads: 12 GET(s), 3145728 byte(s)` — companion cert petition, docketed 2026-11-03, capital, no disposition, 0 distributions.
- Read `metrics/statpack.md` (interim docket section) and `metrics/statpack.json` (`interim.terms` finer counts).
- No CourtListener MCP or web searches.
