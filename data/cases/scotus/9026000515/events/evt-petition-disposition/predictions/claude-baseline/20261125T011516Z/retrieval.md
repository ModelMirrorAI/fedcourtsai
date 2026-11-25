# Retrieval log

- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (`Unknown era 'modern'`); nothing returned.
- `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5` — `ranged corpus reads: 4 GET(s), 983040 byte(s)`. Returned five recent denied dockets (Buenaventura v. Buot; Overton v. Florida, two rows; Odom v. Oklahoma; Dennes v. Texas), unrelated to this case; not used.
- `metrics/statpack.md` — relist-count, CVSG, amicus-count cuts (paid scored segment), the originating-circuit row for `cafc`, and the salience band table.
- No CourtListener MCP calls and no web searches.
