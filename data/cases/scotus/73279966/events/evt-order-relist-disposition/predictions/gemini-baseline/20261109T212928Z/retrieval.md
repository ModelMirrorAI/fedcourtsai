# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-71`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: Returned 1 row (`scotus/9026000071`, *The GEO Group, Inc., a Florida Corporation v. Bob Ferguson, Governor of Washington, et al.*, docket `26-71`, filed `2026-07-16`, `distributed_for_conference: "2026-11-13"`, `distribution_count: 3`, `salience_score: 0.4108`, `disposition: null`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: Returned 10 recent granted SCOTUS rows from the 2020s era (including `25-1408`, `26-12`, `26-204`, `25-1103`, `25-7026`, `25-1343`, `25-1131`, and interim applications `26A560`, `26A512`, `26A476`), showing conference distribution counts (2 to 5) on recent cert grants.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Hencely v. Fluor", fields=["caseName", "dateFiled", "citation", "court", "cluster_id"], num_results=5)`
   - Result: Returned 2 clusters: SCOTUS `Hencely v. Fluor Corp.` (`cluster_id: 10846666`, `dateFiled: 2026-04-22`) and Fourth Circuit `Winston Hencely v. Fluor Corporation` (`cluster_id: 10175552`, `dateFiled: 2024-10-30`).

2. `mcp_courtlistener_search(type="o", case_name="CoreCivic, Inc. v. Governor of New Jersey", fields=["caseName", "dateFiled", "citation", "court", "cluster_id"], num_results=5)`
   - Result: Returned 1 cluster: Third Circuit `CoreCivic Inc v. Governor of New Jersey` (`cluster_id: 10638669`, `dateFiled: 2025-07-22`).

3. `mcp_courtlistener_search(type="o", case_name="GEO Group v. Inslee", fields=["caseName", "dateFiled", "citation", "court", "cluster_id"], num_results=5)`
   - Result: Returned 2 clusters from the Ninth Circuit: `The Geo Group, Inc. v. Inslee` panel decision (`cluster_id: 10656684`, `dateFiled: 2025-08-19`) and order denying rehearing en banc (`cluster_id: 10787254`, `dateFiled: 2026-02-11`).

4. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10656684, fields=["id", "case_name", "date_filed", "citations", "sub_opinions"])`
   - Result: Returned cluster metadata for `10656684` with `sub_opinions: ["https://www.courtlistener.com/api/rest/v4/opinions/11123271/"]`.

5. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10787254, fields=["id", "case_name", "date_filed", "citations", "sub_opinions"])`
   - Result: Returned cluster metadata for `10787254` with `sub_opinions: ["https://www.courtlistener.com/api/rest/v4/opinions/11253895/"]`.

6. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10846666, fields=["id", "case_name", "date_filed", "citations", "sub_opinions"])`
   - Result: Returned cluster metadata for `10846666` with `sub_opinions: ["https://www.courtlistener.com/api/rest/v4/opinions/11314033/"]`.

7. `mcp_courtlistener_read_document(opinion_id=11253895, chunk_index=0)`
   - Result: Returned chunk 0 of 3 (`21853` total chars) of the Ninth Circuit's February 11, 2026 order denying rehearing en banc in *The GEO Group, Inc. v. Inslee*, No. 24-2815, including the statement of Judges W. Fletcher, Gould, and Nguyen comparing *Nwauzor* and *Inslee* and noting Judge Bumatay's 8-judge dissent.

8. `mcp_courtlistener_search_document(opinion_id=11314033, query="intergovernmental")`
   - Result: Returned `match_count: 0` in the Supreme Court's opinion in *Hencely v. Fluor Corp.* (`opinion_id: 11314033`, `total_chars: 108282`), confirming *Hencely* addressed combatant-activities preemption under the FTCA rather than Supremacy Clause intergovernmental immunity.

## 3. Web Searches

None attempted.
