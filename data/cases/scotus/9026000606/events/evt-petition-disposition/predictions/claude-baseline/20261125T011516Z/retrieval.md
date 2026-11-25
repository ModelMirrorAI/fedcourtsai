# Retrieval log

- `metrics/statpack.md` — read the relist-count, CVSG-status and amicus-count cuts (paid scored segment) and the "Segment base rate by salience band" table.
- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — usage error (`modern` is not an era token); no rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5` — returned 5 recent denied rows (Buenaventura v. Buot, Overton v. Florida twice, Odom v. Oklahoma, Dennes v. Texas), none related to this question. stderr: `ranged corpus reads: 4 GET(s), 983040 byte(s)`.
- No CourtListener MCP calls and no web searches.
