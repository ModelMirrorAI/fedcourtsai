# Retrieval Log

## Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000157" --event "evt-order-call-for-response-disposition" --role predictor`
   - Output: resolved paths for `scotus/9026000157`.
2. `uv run fedcourts query --help`
   - Output: CLI usage documentation.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Output: 10 recent granted SCOTUS cases from the 2020s era (including `25-1131`, *Missionaries of Saint John the Baptist, Inc. v. Frederic*).
4. `uv run fedcourts query --court scotus --docket-number 25-849`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Output: 1 row (`scotus/73280351`, *United States Conference of Catholic Bishops v. David O'Connell*, No. 25-849, cert denied May 26, 2026 after 4 distributions).
5. `uv run fedcourts query --court scotus --docket-number 25-705`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Output: 1 row (`scotus/73279550`, *Carter Page v. James B. Comey, et al.*, No. 25-705).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Missionaries of Saint John the Baptist v. Frederic", fields=["id", "caseName", "court", "dateFiled", "citation", "snippet"])`
   - Output: 1 match (*Missionaries of Saint John the Baptist, Inc. v. Joel Frederic*, Kentucky Supreme Court, filed 2025-12-18).
2. `mcp_courtlistener_search(type="o", case_name="Missionaries of Saint John the Baptist v. Frederic", fields=["opinions", "cluster_id", "caseName"])`
   - Output: 1 match (`cluster_id: 10760784`, `opinion_id: 11227369`).
3. `mcp_courtlistener_search(type="o", case_name="Lutheran Church-Missouri Synod v. Christian", fields=["opinions", "cluster_id", "caseName", "dateFiled"])`
   - Output: 0 matches under exact full string.
4. `mcp_courtlistener_read_document(opinion_id=11227369, chunk_index=0, chunk_size=4000)`
   - Output: Read first chunk of *Missionaries of Saint John the Baptist, Inc. v. Frederic* (confirming it is a RLUIPA land-use case rather than a church-autonomy case).
5. `mcp_courtlistener_search(type="o", court="ca5", case_name="Christian", filed_after="2025-10-01", fields=["caseName", "dateFiled", "citation", "docketNumber"])`
   - Output: 2 matches (*Lutheran Church v. Christian*, No. 25-50130, filed 2026-06-04; *Domanic v. Christian Brothers*, No. 25-20486, filed 2026-09-30).
6. `mcp_courtlistener_search(type="o", court="ca5", case_name="McRaney v. North American Mission Board", fields=["caseName", "dateFiled", "citation", "docketNumber"])`
   - Output: 0 matches.

## Web Searches

- None performed.
