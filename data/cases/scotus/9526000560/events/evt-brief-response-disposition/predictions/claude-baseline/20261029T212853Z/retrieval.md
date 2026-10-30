# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --include-applications --limit 10`
  rejected with a usage error ("Unknown era 'modern'"). No corpus read.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --include-applications --limit 12`
  stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned 12 recent
  OT2026 applications (26A574–26A599), mostly extension-style grants. Not
  informative for a government stay application, so not used in the forecast.
- Read the committed `metrics/statpack.md` interim-docket section for the base rate.
- No CourtListener MCP calls and no web searches.
