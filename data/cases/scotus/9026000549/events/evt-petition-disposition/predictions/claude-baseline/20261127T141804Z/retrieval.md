# Retrieval log

- `uv run fedcourts query --help` — read the flag surface.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (era value not accepted); returned help text only.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — stderr: `ranged corpus reads: 35 GET(s), 9175040 byte(s)`. Returned five recent granted SCOTUS rows (Robinhood Markets v. Sodha; Mullin v. RAICES; Mullin v. Friends of the Ruidosa Church; Goldman Sachs Bank USA v. Brown; Scanlan v. Coalition for Open Democracy). Generic; did not shape the forecast.
- `metrics/statpack.md` — relist-count, CVSG, and sal-v9 band tables.
- No CourtListener MCP lookups and no web searches.
