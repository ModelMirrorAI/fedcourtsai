# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number "26A276"`
   - Transfer stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 row (`scotus/9526000276`, an unrelated extension application sharing docket number `26A276`; the extension link for No. 26-518 is already documented in the provisioned snapshot `2026-10-27.json`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS granted petitions and substantive applications to review current-Term baseline grant patterns.

## CourtListener MCP / Web Retrieval

- None attempted beyond the provisioned inputs and corpus queries above.
