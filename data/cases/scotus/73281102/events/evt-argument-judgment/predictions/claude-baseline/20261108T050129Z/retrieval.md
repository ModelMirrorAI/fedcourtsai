# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. Refused with a usage error (`modern` is not an era token); no rows came back.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
  - Returned 5 recent granted SCOTUS rows, none on habeas cognizability. Not relied on.
- Read the committed `metrics/statpack.md` (merits docket section; per-Justice merits votes).
- No CourtListener MCP calls and no web searches.
