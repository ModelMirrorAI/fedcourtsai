# Retrieval

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`: usage error (the help text printed, and `--era modern` was probably not a valid value). No ranged-reads line was captured.
- `uv run fedcourts query --court scotus --disposition denied --limit 3`: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`. It returned three generic recent denied rows (Louisiana v. Devon Energy; Griffin v. Isaac; Monte v. United States), none of them relevant.
- Read `metrics/statpack.md` (the relist-count and amicus-count paid-segment cuts).
- No CourtListener MCP calls and no web searches.
