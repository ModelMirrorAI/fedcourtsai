# Retrieval

- `uv run fedcourts query --court scotus --docket-number 25-107` — Gilliam v. Gerregano row: denied 2025-12-08, distribution_count 2, five amicus filers. stderr: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`. (Run twice; the second run's stderr was discarded.)
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3` — usage error (`Unknown era 'modern'`).
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3` — three recent granted rows, skimmed for shape only. stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`.
- Read `metrics/statpack.md` (salience-band, relist and CVSG cuts).
- No CourtListener MCP calls and no web searches.
