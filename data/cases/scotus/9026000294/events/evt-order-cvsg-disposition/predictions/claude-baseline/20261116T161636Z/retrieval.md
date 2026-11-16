# Retrieval log

- `uv run fedcourts query --help` — read usage.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (printed help; no rows).
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — returned 5 recent granted rows (Robinhood Markets v. Sodha; Mullin v. RAICES; Mullin v. Friends of the Ruidosa Church; Goldman Sachs Bank USA v. Brown; Scanlan v. Coalition for Open Democracy). None bears on this case. stderr: `ranged corpus reads: 33 GET(s), 8585216 byte(s)`.
- `metrics/statpack.md` — CVSG-status cut, relist-count cut and band table (grep/sed).
- No CourtListener MCP calls and no web searches.
