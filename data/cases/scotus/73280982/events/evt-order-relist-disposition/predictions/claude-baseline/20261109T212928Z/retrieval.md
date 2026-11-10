# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --limit 5`. Stderr: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`. It returned generic recent granted priors and did not shape the forecast.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`. This was a first attempt and printed only usage text (no rows). Its stderr was not captured separately.
- Read `metrics/statpack.md` for the relist, CVSG, and salience-band sections.
- I made no CourtListener MCP lookups and no web searches.
