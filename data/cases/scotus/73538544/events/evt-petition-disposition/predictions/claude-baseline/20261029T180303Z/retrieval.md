# Retrieval

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` — usage error (refused; no `--era modern` value accepted as given), no rows.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` — 5 recent GVR priors (shape only).
  `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
- `uv run fedcourts query --help` — help text.
- Read committed `metrics/statpack.md` (salience-band and relist-count sections).

No CourtListener MCP calls and no web searches.
