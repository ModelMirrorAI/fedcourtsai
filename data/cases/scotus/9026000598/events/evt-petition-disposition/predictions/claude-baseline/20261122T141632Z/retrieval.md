# Retrieval log

- `uv run fedcourts query --help` (interface reference).
- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`: refused, usage error (`modern` is not an era token). Nothing returned.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 4`: returned 4 recent granted SCOTUS rows (Robinhood, two Mullin dockets, Goldman Sachs v. Brown); not on point, not used. stderr: `ranged corpus reads: 34 GET(s), 8781824 byte(s)`.
- Read `metrics/statpack.md`: salience band table (baseline column) and the relist-count cut (paid scored segment).
- No CourtListener MCP calls and no web searches.
