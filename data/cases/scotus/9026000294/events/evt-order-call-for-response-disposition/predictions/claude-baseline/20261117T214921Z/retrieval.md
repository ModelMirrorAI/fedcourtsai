# Retrieval log

- `metrics/statpack.md` — read the "Cert petitions by CVSG status (paid scored segment)" cut and the "Segment base rate by salience band (sal-v8)" table.
- `uv run fedcourts query --help` — read usage.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — usage error (flag value rejected); returned help text only.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — `ranged corpus reads: 33 GET(s), 8650752 byte(s)`; five recent unrelated granted rows; not used in the forecast.
- No CourtListener MCP calls and no web searches.
