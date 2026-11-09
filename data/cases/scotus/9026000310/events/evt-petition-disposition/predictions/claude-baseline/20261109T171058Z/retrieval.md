# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — refused with a usage error (`--era` takes a decade token). No rows.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — 5 recent granted SCOTUS priors (generic; not case-specific).
  `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
- Read committed `metrics/statpack.md` (modern cert disposition, relist, CVSG, amicus cuts; sal-v8 band table).
- No CourtListener MCP calls and no web searches.
