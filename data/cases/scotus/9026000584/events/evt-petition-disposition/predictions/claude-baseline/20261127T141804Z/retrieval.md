# Retrieval log

- Read committed `metrics/statpack.md` (relist-count, CVSG, amicus-count, salience-band tables; sal-v9 per-Term band table).
- `uv run fedcourts query --help` — usage text.
- `uv run fedcourts query --court scotus --docket-number 25-107` — returned the *Gilliam v. Gerregano* row (denied 2025-12-08, distribution_count 2, several amici). stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- `uv run fedcourts query --court scotus --disposition granted --era modern` — refused: unknown era `modern` (usage error; no transfer line).
- `uv run fedcourts query --court scotus --disposition granted --era 2020s` — returned recent granted rows (generic; none on point, not relied on). stderr: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`.
- No CourtListener MCP calls and no web searches.
