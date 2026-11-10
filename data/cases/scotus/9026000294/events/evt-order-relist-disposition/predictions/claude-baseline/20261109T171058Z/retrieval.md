# Retrieval log
- `uv run fedcourts query --court scotus --disposition granted --era modern` — usage error (era must be a decade token). No transfer line.
- `uv run fedcourts query --court scotus --docket-number 26-292` — `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. Companion Havlish row: pending, matching the staged snapshot.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s` — `ranged corpus reads: 38 GET(s), 9961472 byte(s)`. Generic granted priors, skimmed only and not relied on.
- Read `metrics/statpack.md` (relist, CVSG and amicus cuts; sal-v8 band table).
- No CourtListener MCP or web searches.
