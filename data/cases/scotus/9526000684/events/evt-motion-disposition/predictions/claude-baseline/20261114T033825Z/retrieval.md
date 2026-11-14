# Retrieval log

Provisioned inputs read: snapshot `2026-11-11.json`, `context.json`, `event.yaml`, `documents.json`,
`application.txt`. Base rates: `metrics/statpack.md`, "The interim docket (applications)" and its
applicant-class table.

Corpus lookups:

1. `uv run fedcourts query --help` — usage.
2. `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 5`
   — usage error (printed help; `modern` not accepted as given). No rows.
3. `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5`
   — `ranged corpus reads: 9 GET(s), 2293760 byte(s)`. Five rows: Pavatt v. Oklahoma (two rows,
   capital), Schultz v. Gold (26A658), Schultz v. McCarthy (26A657), Jesenik v. United States. The two
   Schultz rows are the same applicant's other applications.
4. `uv run fedcourts query --court scotus --docket-number 26A657`
   — `ranged corpus reads: 20 GET(s), 5242880 byte(s)`. Schultz v. McCarthy, from CA4 No. 26-2406,
   filed 2026-11-06, denied 2026-11-10; no response requested, not referred, 0 amicus.
5. `uv run fedcourts query --court scotus --docket-number 26A658`
   — `ranged corpus reads: 0 GET(s), 0 byte(s)`. Schultz v. Gold, filed 2026-11-06, denied 2026-11-11;
   no response requested, not referred, 0 amicus.

No CourtListener MCP calls, no web searches, no visit to the Court's docket page.
