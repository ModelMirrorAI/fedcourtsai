# Retrieval log

Beyond the provisioned inputs (and the committed `metrics/statpack.md`):

1. `uv run fedcourts query --help` — read the interface.
2. `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — usage error (`Unknown era 'modern'`); run three times while diagnosing. No rows.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` — `ranged corpus reads: 33 GET(s), 8585216 byte(s)`. Five recent granted rows (Robinhood, Mullin v. Refugee…, Goldman Sachs v. Brown, two applications); none on point, used only as a sanity read.
4. `uv run fedcourts query --court scotus --docket-number 25-819` (twice; the second to extract fields) — `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. *Hedgepeth v. Britton*: disposition denied, distribution_count 2. Used as the nearest prior (same circuit, neighbouring Pickering question).

No CourtListener MCP calls and no web searches.
