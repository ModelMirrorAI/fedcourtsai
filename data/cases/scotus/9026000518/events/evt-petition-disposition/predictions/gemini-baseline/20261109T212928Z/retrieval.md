# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 5 recent resolved 2020s SCOTUS cert petitions with `disposition: "denied"` (`scotus/73500344`, `scotus/73500351`, `scotus/73500384`, `scotus/73522552`, `scotus/73523164`) for distribution and salience-band context.

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Stderr: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
   - Result: Returned 5 recent resolved 2020s SCOTUS cases with `disposition: "granted"` (`scotus/9526000560`, `scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`) for comparison of distribution counts and salience scores on granted petitions.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca11", docket_number="22-13410", fields=["caseName", "dateFiled", "citation", "docketNumber", "judge", "status"])`
   - Result: `count: 0, results: []` (no additional opinion record indexed under that search query; relied on the full text of the Eleventh Circuit's November 26, 2025 opinion and May 12, 2026 rehearing denial order reproduced in Appendix A and Appendix E of the provisioned `record/documents/petition.txt`).

## Web Searches

- None attempted.
