# Retrieval Log (`scotus/72408073` — `evt-brief-response-disposition`)

## 1. `fedcourts` CLI Lookups
1. `uv run fedcourts paths --court scotus --docket 72408073 --event evt-brief-response-disposition --role predictor`
   - Returned case, corpus, and event paths.
2. `uv run fedcourts query --help`
   - Inspected structured query flags.
3. `uv run fedcourts query --court scotus --docket-number 16-8909 --decided-before 2017-08-11`
   - `ranged corpus reads: 663 GET(s), 173539328 byte(s)`
   - Returned 1 row (`scotus/66643039`, docket `16-8909`, `date_filed: "2017-04-27"`, `originating_court: "ca5"`, `disposition: null` as masked at `2017-08-11`).
4. `uv run fedcourts query --court scotus --era 2010s --decided-before 2017 --limit 10`
   - `ranged corpus reads: 225 GET(s), 58982400 byte(s)`
   - Returned 10 pre-2017 substantive application priors (`16A632`, `16A646`, `16A620`, `16A557`, `16A545`, `16A569`, `16A570`, `16A548`, `16A559`, `16A497`), including several December 2016 capital stay applications showing typical referral and disposition patterns.
5. `uv run fedcourts query --court ca5 --docket-number 16-70010 --decided-before 2017-07-31`
   - `ranged corpus reads: 117 GET(s), 30670848 byte(s)`
   - Returned 3 Fifth Circuit corpus rows for docket `16-70010`: `ca5/4480565`, `ca5/6240540`, and `ca5/65966066`.

## 2. CourtListener MCP Lookups
1. `mcp_courtlistener_search(type="o", court="ca5", docket_number="16-70010", filed_before="2017-07-31", fields=["caseName", "dateFiled", "docketNumber", "citation", "cluster_id", "opinions"])`
   - Returned 0 results (`query_id: "acd25b22"`).
2. `mcp_courtlistener_search(type="o", court="ca5", case_name="Long v. Davis", filed_before="2017-07-31", fields=["caseName", "dateFiled", "docketNumber", "citation", "cluster_id", "opinions"])`
   - Returned 0 results (`query_id: "a0df50d7"`).
3. `mcp_courtlistener_search(type="o", court="ca5", q=""16-70010" OR "Steven Lynn Long"", filed_before="2017-07-31", fields=["caseName", "dateFiled", "docketNumber", "citation", "cluster_id", "opinions"])`
   - Returned 0 results (`query_id: "b11e754f"`).
4. `mcp_courtlistener_search(type="o", court="ca5", q=""Steven Long" "Lorie Davis"", filed_before="2017-07-31", fields=["caseName", "dateFiled", "docketNumber", "citation", "cluster_id", "opinions"])`
   - Returned 0 results (`query_id: "11feeabe"`).
5. `mcp_courtlistener_search(type="r", court="ca5", docket_number="16-70010", filed_before="2017-07-31", fields=["caseName", "dateFiled", "docketNumber", "docket_id"])`
   - Returned 0 results (`query_id: "72667e6f"`).
6. `mcp_courtlistener_call_endpoint(endpoint_id="clusters", query={"docket": 4480565, "fields": ["id", "case_name", "date_filed", "sub_opinions"]})`
   - Returned 1 result (`query_id: "3c8d5b47"`): cluster `4313659`, `Steven Long v. Lorie Davis, Director`, `date_filed: "2016-10-19"`, `sub_opinions: ["https://www.courtlistener.com/api/rest/v4/opinions/4090920/"]`.
7. `mcp_courtlistener_call_endpoint(endpoint_id="clusters", query={"docket": 6240540, "fields": ["id", "case_name", "date_filed", "sub_opinions"]})`
   - Returned 1 result (`query_id: "2850eac9"`): cluster `4450924`, `Steven Long v. Lorie Davis, Director`, `date_filed: "2017-12-12"`, `sub_opinions: ["https://www.courtlistener.com/api/rest/v4/opinions/4228177/"]`. Because `2017-12-12` postdates the `2017-08-11` snapshot cutoff, we did **not** read `opinion_id: 4228177` and disclosed the metadata return in `flags.json`.
8. `mcp_courtlistener_read_document(opinion_id=4090920, chunk_index=0)`
   - Read chunk 0 of the pre-cutoff Fifth Circuit opinion (`663 F. App'x 362`, decided Oct. 19, 2016).
9. `mcp_courtlistener_read_document(opinion_id=4090920, chunk_index=[1, 2, 3])`
   - Read chunks 1–3 of `opinion_id: 4090920` (`663 F. App'x 362`, Oct. 19, 2016).

## 3. Web Searches
- None attempted.
