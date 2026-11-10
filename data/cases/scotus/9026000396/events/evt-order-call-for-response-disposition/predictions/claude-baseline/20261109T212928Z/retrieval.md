# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 25-818` — `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. Returned *Hargrove v. Healy* (CA6): filed 2026-01-12, one distribution, cert denied 2026-04-20, no CVSG.
- `uv run fedcourts query --court scotus --docket-number 25-5930` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned *Maxwell v. Dinis*: counsel list includes a court-appointed amicus in support of the judgment below (government not defending it).
- `uv run fedcourts query --help` (usage only).
- Read `metrics/statpack.md` (salience-band table, CVSG and amicus cuts).
- No CourtListener MCP or web searches.
