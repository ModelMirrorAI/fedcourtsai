# Retrieval log

- `uv run fedcourts query --help` — read the filter surface.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (`modern` is not an era token); nothing returned.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 6` — `ranged corpus reads: 36 GET(s), 9371648 byte(s)`; six recent granted SCOTUS rows, none on this question; not used beyond confirming the surface has no subject filter for SCOTUS rows.
- `metrics/statpack.md` — salience-band table (sal-v8), relist-count cut, amicus-brief-count cut.
- No CourtListener MCP calls, no web searches, no live-docket fetch.
