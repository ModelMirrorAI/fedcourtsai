# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number "26-80"`
   - Transfer line: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Result: Returned 1 row (`scotus/9026000080`, *Felicia Scroggins v. City of Shreveport, Louisiana*, No. 26-80, originating from CA5 No. 24-30777, filed 2026-07-17, distributed once on 2026-09-28, cert denied 2026-10-05).

2. `uv run fedcourts query --court scotus --era 2020s --limit 5`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Returned 5 recent resolved SCOTUS priors in the 2020s era (`scotus/9026000002`, `scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9026000346`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Scroggins v. City of Shreveport", fields=["caseName", "court", "docketNumber", "dateFiled", "citation", "cluster_id", "id"])`
   - Result: Returned 1 match (`cluster_id: 10705997`, Fifth Circuit docket `24-30777`, filed `2025-10-17`, Petitioner's earlier appeal).

2. `mcp_courtlistener_search(type="o", case_name="Weber v. BNSF Railway", court="ca5", fields=["caseName", "court", "docketNumber", "dateFiled", "citation", "cluster_id"])`
   - Result: Returned 0 matches (`count: 0`).

## Web Searches

- None attempted.
