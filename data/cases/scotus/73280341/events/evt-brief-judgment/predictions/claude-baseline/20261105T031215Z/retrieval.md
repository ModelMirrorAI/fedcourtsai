# Retrieval log

- `uv run fedcourts query --court scotus --disposition reversed --limit 5` → usage error ("Unknown disposition 'reversed'"; cert vocabulary only). No transfer line.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` → `ranged corpus reads: 30 GET(s), 7864320 byte(s)`. Returned recent granted/application rows (e.g. Scanlan v. Coalition for Open Democracy, DOJ v. McNutt); not informative for this merits judgment.
- Read the committed `metrics/statpack.md` (merits docket section; per-Justice merits votes).
- No CourtListener MCP calls and no web searches.
