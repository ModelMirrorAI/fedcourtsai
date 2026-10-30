# Retrieval log

- `uv run fedcourts query --help` — usage text.
- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` — refused/usage text (era value not accepted); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — five recent granted SCOTUS rows (applications and cert dockets); general context only.
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
- `uv run fedcourts query --docket-number 25-1359` — printed usage text only; no row returned.
- Committed `metrics/statpack.md` (salience-band, relist-count, amicus-count cuts).
- Committed case summary `data/cases/scotus/73500260/summaries/2026-10-25.md`.
- No CourtListener MCP calls and no web searches.
