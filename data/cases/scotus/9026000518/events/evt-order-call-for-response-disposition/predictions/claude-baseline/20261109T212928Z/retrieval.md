# Retrieval

- `uv run fedcourts query --help`: usage read.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: printed usage help (the era value was not accepted).
- `uv run fedcourts query --court scotus --docket-number 26-518`: this docket's own corpus row. Last polled 2026-11-09, distribution_count 1, no disposition. The two commands ran in one shell call, which printed one line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`: five recent granted priors, none on point. `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
- Read `metrics/statpack.md` (modern-cert, circuit, relist, CVSG, amicus and salience-band sections).
- No CourtListener MCP calls and no web searches.
