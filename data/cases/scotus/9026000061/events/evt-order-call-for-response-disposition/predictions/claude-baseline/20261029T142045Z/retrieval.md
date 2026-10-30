# Retrieval log

- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — usage-level output only (help text; no rows printed in the captured tail).
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; returned recent granted SCOTUS dockets (none related to copyright); not used in the forecast.
- Committed `metrics/statpack.md` read for base rates (band table, relist/CVSG/amicus cuts, originating circuit).
- No CourtListener MCP calls and no web searches.
