# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 26-1` — `ranged corpus reads: 12 GET(s), 3145728 byte(s)` — Sunoco v. Cline: cert denied 2026-10-05.
- `uv run fedcourts query --court scotus --docket-number 25-677` (run twice, the second time to read the row tail) — `ranged corpus reads: 1 GET(s), 262144 byte(s)` — City of Cleveland v. Pickett: pending, distribution_count 4, last distributed 2026-05-28.
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3` — usage error (era must be a decade token); no rows returned.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` — `ranged corpus reads: 25 GET(s), 6553600 byte(s)` — generic recent grants, none related; not used.
- `uv run fedcourts query --help` — read the help text.
- Read `metrics/statpack.md` (committed).
- No CourtListener MCP calls and no web searches.
