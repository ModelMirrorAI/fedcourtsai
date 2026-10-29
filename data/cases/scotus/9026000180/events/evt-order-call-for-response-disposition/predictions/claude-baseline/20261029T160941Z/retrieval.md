# Retrieval log

- `uv run fedcourts query --help` (usage read).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
  printed help text, which I took to mean a usage problem with the flags, and returned no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
  - Returned recent granted SCOTUS rows (general context only; none on point).
- Read the committed `metrics/statpack.md` (salience band table, relist, and amicus cuts).
- Read the case's plain-language summary `data/cases/scotus/9026000180/summaries/2026-10-25.md`.
- No CourtListener MCP calls and no web searches.
