# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 26-6051`. This returned the linked
  cert petition row: filed 2026-11-03, CA11 26-14027, capital, 0 distributions, undecided.
  - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 8`.
  This was a usage error ("Unknown era 'modern'"). No rows came back.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --include-applications --limit 8`.
  This returned recent denied 26A applications, all non-capital and unrelated, and gave
  only the general shape.
  - `ranged corpus reads: 3 GET(s), 786432 byte(s)`
- I read `metrics/statpack.md` (interim section) and the `interim` block of `metrics/statpack.json`.
- No CourtListener MCP or web calls.
