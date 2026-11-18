# Retrieval log

- `uv run fedcourts query --help` — read usage.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — returned a usage error (help text); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 33 GET(s), 8650752 byte(s)`; five recent granted rows (e.g. Robinhood Markets v. Sodha; Mullin v. RAICES; Goldman Sachs Bank USA v. Brown), none bearing on this petition. Not used in the forecast.
- `metrics/statpack.md` — salience-band table (sal-v8), relist-count cut, originating-court cut (cadc).
- No CourtListener MCP calls and no web searches.
