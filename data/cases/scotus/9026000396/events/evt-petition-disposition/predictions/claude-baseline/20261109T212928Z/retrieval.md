# Retrieval log
- `uv run fedcourts query --docket-number 25-818` (without `--court`): usage error; it requires `--court`.
- `uv run fedcourts query --docket-number 25-5930` (without `--court`): same usage error.
- `uv run fedcourts query --court scotus --docket-number 25-818 --include-open`: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. Hargrove v. Healy: denied 2026-04-20, distribution_count 1, amicus coalition counsel listed.
- `uv run fedcourts query --court scotus --docket-number 25-5930 --include-open`: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Maxwell v. Dinis: counsel list shows a court-appointed amicus defending the judgment below.
- `uv run fedcourts query --help`: reading the help text, not a retrieval.
- Read `metrics/statpack.md`: the relist-count and CVSG cuts, and the sal-v8 band table.
- No CourtListener MCP or web searches.
