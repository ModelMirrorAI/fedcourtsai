# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`: usage error (the flag was refused), so I re-issued it without `--era`.
- `uv run fedcourts query --court scotus --disposition denied --limit 3`: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. It returned generic recent denials (Guardado applications, Lopez Jaime), none on point. Used only as a sanity check.
- Read `metrics/statpack.md`: the salience-band table (sal-v7) and the relist, CVSG and amicus cuts for the paid scored segment.
- No CourtListener MCP lookups and no web searches.
