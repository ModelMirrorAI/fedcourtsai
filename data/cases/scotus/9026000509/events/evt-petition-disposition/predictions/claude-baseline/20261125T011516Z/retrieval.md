# Retrieval

- `uv run fedcourts query --help`: read the interface.
- `uv run fedcourts query --court scotus --disposition denied --era modern`: refused, `Unknown era 'modern'` (an era is a decade token).
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`: `ranged corpus reads: 4 GET(s), 983040 byte(s)`. Five recent denied rows (Buenaventura v. Buot, Overton v. Florida twice, Odom v. Oklahoma, Dennes v. Texas), none related; not used.
- `metrics/statpack.md`: salience band tables and originating-court table.
- No CourtListener MCP calls and no web searches.
