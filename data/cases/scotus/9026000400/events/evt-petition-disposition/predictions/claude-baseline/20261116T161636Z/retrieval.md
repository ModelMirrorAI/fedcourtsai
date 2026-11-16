# Retrieval log

- `uv run fedcourts query --help` (usage).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (era value not accepted); nothing returned.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — five recent granted rows (Robinhood Markets v. Sodha; two Mullin matters; Goldman Sachs Bank USA v. Brown; Scanlan v. Coalition for Open Democracy). `ranged corpus reads: 33 GET(s), 8585216 byte(s)`. Not specific to this case; not relied on.
- `metrics/statpack.md` — salience-band table (sal-v8), relist, CVSG and amicus-count cuts.
- No CourtListener MCP calls and no web searches.
