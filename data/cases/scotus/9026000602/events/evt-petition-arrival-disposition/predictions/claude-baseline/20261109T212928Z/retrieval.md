# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`: rejected with a usage error ("Unknown era 'modern'"; an era is a decade token). No rows returned.
- `uv run fedcourts query --court scotus --disposition denied --limit 3`: returned 3 recent denied priors (e.g. Jesenik v. United States). Used only as a format/coverage check, not for this case.
  - stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
- `uv run fedcourts query --help`: read the usage text.
- Read `metrics/statpack.md`: the salience-band table (sal-v8), the modern-cert disposition table, and the relist, CVSG and circuit cuts.
- No CourtListener MCP calls and no web searches.
