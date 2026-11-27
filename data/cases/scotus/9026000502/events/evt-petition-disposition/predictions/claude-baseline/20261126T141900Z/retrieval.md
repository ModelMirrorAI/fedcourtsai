# Retrieval log

- Read committed `metrics/statpack.md` (modern cert dispositions, relist-count cut, amicus-count cut, salience-band table).
- `uv run fedcourts query --help` — usage text.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (flags not accepted as given); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 4` — stderr: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`; returned four recent granted petitions (Robinhood Markets v. Sodha; two Mullin v. … federal-petitioner cases; Goldman Sachs Bank USA v. Brown). Not analogous; not used.
- No CourtListener MCP calls and no web searches.
