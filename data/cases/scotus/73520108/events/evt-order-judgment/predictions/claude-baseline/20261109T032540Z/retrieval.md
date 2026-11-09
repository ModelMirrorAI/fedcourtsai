# Retrieval
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: this was a usage error
  (no `--limit`/`--era` accepted in that form, so it printed help). No rows came back.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` printed
  `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. It returned five recent SCOTUS grants (this case first,
  then unrelated applications and petitions). None bore on the merits forecast.
- I read the committed `metrics/statpack.md` sections "The merits docket (granted cases)" and "Per-Justice merits votes".
- No CourtListener MCP calls and no web searches.
