# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5` returned a usage/help output, possibly because of the `--era` value. No rows came back.
- `uv run fedcourts query --court scotus --disposition denied --limit 5` printed `ranged corpus reads: 8 GET(s), 2097152 byte(s)`. It returned recent denied SCOTUS rows used as general priors; none was on point.
- `uv run fedcourts query --help` (usage).
- Committed `metrics/statpack.md`: relist, CVSG, amicus and salience-band sections.
- No CourtListener MCP or web lookups.
