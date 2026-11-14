# Retrieval log

- Read committed `metrics/statpack.md`, section "The interim docket (applications)" and its "Substantive applications by applicant class" table.
- `uv run fedcourts query --help` (usage).
- `uv run fedcourts query --court scotus --era modern --disposition denied --include-applications --limit 8` — refused: unknown era token; printed the usage text.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 8` — `ranged corpus reads: 10 GET(s), 2555904 byte(s)`. Returned eight recent denied SCOTUS rows (a mix of cert petitions and substantive applications, including two pro se stay applications denied this Term). Generic context; did not move the number.
- No CourtListener MCP calls and no web searches.
