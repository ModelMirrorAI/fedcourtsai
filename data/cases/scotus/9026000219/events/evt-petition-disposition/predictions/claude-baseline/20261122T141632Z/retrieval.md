# Retrieval log

- Read committed `metrics/statpack.md` (modern cert dispositions, relist/CVSG/amicus cuts, salience band tables, per-Term table).
- `uv run fedcourts query --help` (usage).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — output was cut by my own pipe to the help tail; I did not see rows from it.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — stderr: `ranged corpus reads: 35 GET(s), 9043968 byte(s)`; returned five recent granted rows (e.g. Robinhood Markets v. Sodha; Mullin v. Refugee and Immigrant Center), none bearing on this case.
- No CourtListener MCP calls and no web searches.
