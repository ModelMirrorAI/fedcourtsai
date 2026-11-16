# Retrieval log

- `uv run fedcourts query --help` — read the interface.
- `uv run fedcourts query --court scotus --disposition granted --era modern` — rejected: unknown era token (usage message returned).
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — `ranged corpus reads: 33 GET(s), 8585216 byte(s)`; returned five recent granted dockets, none on point; not used in the number.
- Read `metrics/statpack.md`: modern cert dispositions, relist-count, CVSG, amicus-count cuts, and the sal-v8 band table.
- No CourtListener MCP calls and no web searches.
