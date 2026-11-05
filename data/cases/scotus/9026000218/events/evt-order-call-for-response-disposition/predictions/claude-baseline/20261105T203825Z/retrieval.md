# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error / help text printed (no `--limit`/`--era` value accepted in that form); no rows, no transfer line.
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` — same help-text output, no rows.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` — `ranged corpus reads: 34 GET(s), 8912896 byte(s)`; returned recent GVR rows (unrelated civil/federal cases), not used for the forecast.
- Read committed `metrics/statpack.md` (relist, CVSG and amicus-count cuts for the paid scored segment).
- No CourtListener MCP calls and no web searches.
