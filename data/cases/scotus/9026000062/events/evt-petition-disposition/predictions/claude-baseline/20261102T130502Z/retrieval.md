# Retrieval log

- `uv run fedcourts query --court scotus --disposition denied --era roberts --limit 5`: usage error ("Unknown era 'roberts'"). No rows and no ranged-reads line.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned five recent granted rows (government-party cases). None was on point, so I used them only as general context.
- Read `metrics/statpack.md`: the relist-count, CVSG and amicus cuts (paid scored segment) and the sal-v6 salience-band table.
- No CourtListener MCP calls and no web searches.
