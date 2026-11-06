# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   - Result: Returned 10 recent 2020s granted SCOTUS rows (including cert grants and substantive applications) for comparison on salience bands, distribution counts, and counsel/amicus participation.

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 recent 2020s denied SCOTUS rows from the warm local corpus cache.

## CourtListener MCP and Web Searches

- No CourtListener MCP calls or external web searches were attempted beyond the provisioned inputs and local `metrics/statpack.md` / `metrics/statpack.json`.
