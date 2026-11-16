# Retrieval log

Beyond the provisioned inputs and `metrics/statpack.md`:

1. `uv run fedcourts query --help` — read the interface.
2. `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 6` — usage error (`modern` is not an era token); no rows.
3. `uv run fedcourts query --court scotus --docket-number 26-292` — returned the companion Havlish row (open, CVSG 2026-11-16, distribution count 2). `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` — five rows (25-1421, 26-5528, 25-442, 25-1348, 26-5123); generic, not used. `ranged corpus reads: 28 GET(s), 7274496 byte(s)`

No CourtListener MCP calls and no web searches.
