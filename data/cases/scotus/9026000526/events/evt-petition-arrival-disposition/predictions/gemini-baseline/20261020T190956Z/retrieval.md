# Retrieval Log

## Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000526" --event "evt-petition-arrival-disposition" --role predictor`
   - Resolved cell paths (`scotus/9026000526`).
2. `uv run fedcourts query "double jeopardy judgment of acquittal compulsory process" --court scotus --limit 10`
   - Returned CLI usage error (no free-text positional argument supported).
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
4. `uv run fedcourts query --court scotus --citation "601 U.S. 87" --limit 5`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
5. `uv run fedcourts query --court scotus --citation "568 U.S. 313" --limit 5`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Mitchell v. Mississippi", fields=["caseName", "dateFiled", "citation", "court", "docketNumber"])`
   - Checked general prior opinions with similar captions; none corresponded to this case.
2. `mcp_courtlistener_search(type="o", court="scotus", case_name="McElrath v. Georgia", fields=["caseName", "dateFiled", "citation", "court", "docketNumber"])`
   - Verified citation and date for *McElrath v. Georgia*, 601 U.S. 87 (2024).
3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Evans v. Michigan", fields=["caseName", "dateFiled", "citation", "court", "docketNumber"])`
   - Verified citation and date for *Evans v. Michigan*, 568 U.S. 313 (2013).

## Web Searches

- None.
