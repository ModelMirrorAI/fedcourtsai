# Retrieval log

- `metrics/statpack.md` — read the salience-band table (sal-v8), the relist-count, CVSG-status and amicus-count cuts, and the originating-court table.
- `uv run fedcourts query --help` — usage only.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — usage error (`modern` is not an era value); returned the help text, no rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5` — `ranged corpus reads: 7 GET(s), 1769472 byte(s)`. Returned five recent denials (Pavatt v. Oklahoma 26-6095 and 26A661, Schultz v. Gold 26A658, Schultz v. McCarthy 26A657, Jesenik v. United States); none bears on this question. Not used in the forecast.
- No CourtListener MCP calls. No web searches.
