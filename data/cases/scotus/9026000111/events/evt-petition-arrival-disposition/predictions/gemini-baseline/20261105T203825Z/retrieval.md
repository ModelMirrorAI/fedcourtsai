# Retrieval Log

## Corpus Queries (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000111" --event "evt-petition-arrival-disposition" --role predictor`
   - Output: resolved `case_id scotus/9026000111`, `corpus corpus/corpus.db`, and event path.
2. `uv run fedcourts query --help`
   - Output: CLI usage and filter flags.
3. `uv run fedcourts query --court scotus --docket-number 25-417`
   - Transfer line: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Output: returned 1 row (`scotus/73278422`, *Francis Nielsen v. Kekai Watanabe*, docket `25-417`, `date_cert_granted: "2026-06-22"`, `disposition: "granted"`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Output: returned 10 recent granted SCOTUS petitions/applications from the 2020s era (including Solicitor General petitions such as `26-204`, `25-1103`, `25-1343`, `26-104`).
5. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Output: returned 10 recent GVR SCOTUS petitions from the 2020s era.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Nielsen v. Watanabe", fields=["caseName", "dateFiled", "docketNumber", "citation", "court"])`
   - Output: 1 result (1936 Utah Supreme Court decision; confirmed no SCOTUS merits opinion yet in `25-417`).
2. `mcp_courtlistener_search(type="o", case_name="Goldey v. Fields", fields=["caseName", "dateFiled", "docketNumber", "citation", "court"])`
   - Output: 3 results for *Goldey v. Fields*, 606 U.S. 942 (2025) (No. 24-809, decided June 30, 2025).
