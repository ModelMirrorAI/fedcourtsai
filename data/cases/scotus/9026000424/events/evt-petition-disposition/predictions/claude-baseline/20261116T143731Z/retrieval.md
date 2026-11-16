# Retrieval log

- `uv run fedcourts query --help`: read the flag list.
- `uv run fedcourts query --court scotus --era modern --disposition denied --limit 5`: usage error (`Unknown era 'modern'`); no rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`: 5 rows (recent grants, e.g. Robinhood Markets v. Sodha; Goldman Sachs Bank USA v. Brown), none related to this case. stderr: `ranged corpus reads: 30 GET(s), 7798784 byte(s)`.
- `metrics/statpack.md`: modern cert dispositions, relist-count, CVSG, amicus-count and salience-band cuts, per-Term table, and the sal-v8 band table.
- No CourtListener MCP calls and no web searches.
