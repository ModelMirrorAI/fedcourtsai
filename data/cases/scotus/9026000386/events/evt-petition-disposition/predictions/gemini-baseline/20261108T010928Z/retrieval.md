# Retrieval Log

## Corpus Queries
1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Returned 5 resolved 2020s SCOTUS priors (`scotus/9526000623`, `scotus/9526000634`, `scotus/9526000637`, `scotus/9526000644`, `scotus/9526000636`).

## CourtListener MCP Lookups
- None attempted (the Sixth Circuit's April 1, 2026 order, June 24, 2026 rehearing order, and the Eastern District of Michigan decisions were all provisioned in full inside `record/documents/appendix.txt`, and `record/documents/lower-court-docket.txt` already summarized CourtListener docket 70639487).

## Web Searches
- None attempted.
