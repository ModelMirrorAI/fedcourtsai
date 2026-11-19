# Retrieval log

Corpus lookups (all via `uv run fedcourts query`):

1. `fedcourts query --help`: read the flag surface.
2. `fedcourts query --court scotus --docket-number 25A326`: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Returned Noem v. National TPS Alliance, substantive application, granted 2025-10-03, 4 amicus briefs.
3. `fedcourts query --court scotus --docket-number 24A1059`: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned Noem v. National TPS Alliance, substantive application, granted 2025-05-19, 4 amicus briefs.
4. `fedcourts query --court scotus --docket-number 26-48`: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned Mullin v. National TPS Alliance, disposition gvr, cert granted 2026-10-05.
5. `fedcourts query --court scotus --disposition granted --include-applications --era modern`: usage error (unknown era `modern`); not retried.

Base rates: `metrics/statpack.md`, "The interim docket (applications)" section and its applicant-class table.

No CourtListener MCP calls and no web searches.
