# Retrieval

- Read `metrics/statpack.md`, "The interim docket (applications)" section (committed file).
- `uv run fedcourts query --court scotus --disposition denied --era roberts --include-applications --limit 8` failed with a usage error (bad `--era` value; it printed help). No rows came back.
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 8` returned 8 recent denied SCOTUS applications, mostly individual/pro se substantive ones.
  - `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
- No CourtListener MCP calls and no web searches.
