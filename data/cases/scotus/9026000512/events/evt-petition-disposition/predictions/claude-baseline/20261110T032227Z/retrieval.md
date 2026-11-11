# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`. It failed with a usage error and printed the help text. It returned no rows.
- `uv run fedcourts query --court scotus --disposition denied --limit 5`
  - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`. It returned 5 recent denied priors, used for context only.
- Read `metrics/statpack.md`: the relist, CVSG, amicus and salience-band cuts.
- No CourtListener MCP calls and no web searches.
