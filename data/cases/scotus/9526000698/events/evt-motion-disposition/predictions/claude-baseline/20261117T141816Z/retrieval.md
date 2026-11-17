# Retrieval log

- `uv run fedcourts query --help` — read the filter surface.
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5` — returned five recent denied cert-petition rows (Mizrahi v. United States; Khatibi v. Yip; Strickland v. Moritz; Novotny v. Moore; Farley v. MSPB); none an application analogue, not used. stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`.
- `metrics/statpack.md`, section "The interim docket (applications)" and its applicant-class table — base rates.
- No CourtListener MCP calls, no web searches, no live-docket lookup.
