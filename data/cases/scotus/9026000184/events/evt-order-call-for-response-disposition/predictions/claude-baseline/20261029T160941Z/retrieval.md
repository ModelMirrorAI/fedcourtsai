# Retrieval log

- `uv run fedcourts query --help` — usage text.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — five recent granted SCOTUS rows (general context only).
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 26-184` — this docket's own corpus row (open; no CVSG; no cert disposition).
  `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-184.html` — the Court's live docket. Showed the same entries as the snapshot plus: 10/14/2026 motion to extend time to respond to 11/25/2026; 10/15/2026 granted. No amicus briefs; no disposition.
- Committed `metrics/statpack.md` (base rates).
- No CourtListener MCP calls.
