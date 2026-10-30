# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` — usage error (no `--era roberts` value accepted / help printed); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; returned five recent granted dockets (mostly federal-government applications/petitions), not analogous; not used in the forecast.
- Read committed `metrics/statpack.md` (salience-band, relist, amicus cuts).
- No CourtListener MCP lookups; no web searches.
