# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 26-6095` — `ranged corpus reads: 737 GET(s), 193069056 byte(s)`; note: no row for 26-6095 in the corpus.
- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 5` — usage error (unknown era 'modern'), no rows.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --include-applications --limit 8` — `ranged corpus reads: 2 GET(s), 524288 byte(s)`; recent rows, mostly extension-type applications, not informative for a capital stay.
- Read `metrics/statpack.md` (interim docket section and applicant-class table).
- No CourtListener MCP or web searches.
