# Retrieval Log

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000583" --event "evt-petition-arrival-disposition" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --help`
   - Inspected structured filter flags for `fedcourts query`.
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 5 recent resolved 2020s SCOTUS denied priors (`scotus/9526000606`, `scotus/9526000613`, `scotus/9526000617`, `scotus/9526000618`, `scotus/9526000499`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer line: `ranged corpus reads: 22 GET(s), 5767168 byte(s)`
   - Returned 5 recent resolved/granted 2020s SCOTUS priors (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca11", docket_number="25-12004", fields=["caseName", "docketNumber", "dateFiled", "court", "cluster_id", "docket_id", "status"])`
   - Returned 1 result: *Ahmed Shaikh v. Fox News Network, LLC*, No. 25-12004, filed `2026-06-04`, `cluster_id: 10870293`, `docket_id: 73442430`, `status: "Published"`.
2. `mcp_courtlistener_search(type="r", court="ca11", docket_number="25-12004", fields=["caseName", "docketNumber", "dateFiled", "court", "docket_id"])`
   - Returned 1 result: *Ahmed Shaikh v. Fox News Network, LLC*, No. 25-12004, `docket_id: 73442430`.
3. `mcp_courtlistener_search(type="o", case_name="Shaikh v. Fox News", fields=["caseName", "docketNumber", "dateFiled", "court", "cluster_id", "docket_id"])`
   - Returned 1 result: `cluster_id: 10870293`, `docket_id: 73442430`.
4. `mcp_courtlistener_search(type="r", case_name="Shaikh v. Fox News", fields=["caseName", "docketNumber", "dateFiled", "court", "docket_id"])`
   - Returned 2 results: Eleventh Circuit No. `25-12004` (`docket_id: 73442430`) and M.D. Fla. No. `6:24-cv-01894` (`docket_id: 69301906`, filed `2024-10-22`).
5. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10870293, fields=["id", "case_name", "date_filed", "judges", "precedential_status", "sub_opinions", "citations"])`
   - Returned cluster metadata and sub-opinion URL `opinions/11337751/`.
6. `mcp_courtlistener_call_endpoint(endpoint_id="opinions", query={"cluster": 10870293, "fields": ["id", "type", "author_str", "per_curiam"]})`
   - Confirmed `opinion_id: 11337751` (`type: "010combined"`).
7. `mcp_courtlistener_read_document(opinion_id=11337751)`
   - Read the full 8-page published per curiam opinion of the Eleventh Circuit (`18,486` chars) affirming the Rule 12(b)(1) dismissal of Shaikh's complaint under *Bell v. Hood*.
8. `mcp_courtlistener_search(type="o", case_name="Ahmed Shaikh", fields=["caseName", "docketNumber", "dateFiled", "court", "cluster_id"])`
   - Returned 2 results: Eleventh Circuit No. `25-12004` (`cluster_id: 10870293`) and an unrelated 2006 Seventh Circuit immigration case (`cluster_id: 2999707`).

## 3. Web Searches

None.
