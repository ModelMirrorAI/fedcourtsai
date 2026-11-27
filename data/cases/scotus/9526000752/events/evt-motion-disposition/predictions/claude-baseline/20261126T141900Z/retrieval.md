# Retrieval log

- `uv run fedcourts query --help` — read usage.
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5` — returned usage/help text rather than rows (flag combination not accepted); no transfer line seen.
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5` — 5 rows (recent denied SCOTUS applications/petitions, incl. pro se substantive applications denied within days). stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.
- Read committed `metrics/statpack.md` (interim-docket section and applicant-class table) and `metrics/statpack.json` (`interim` per-Term `finer_*` counts).
- No CourtListener MCP calls, no web searches, no visit to the Court's docket page.
