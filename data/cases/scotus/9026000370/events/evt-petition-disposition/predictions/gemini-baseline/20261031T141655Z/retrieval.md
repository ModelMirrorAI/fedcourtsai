# Retrieval Log — `scotus/9026000370` (`evt-petition-disposition`)

## 1. Local Corpus Queries (`uv run fedcourts query`)

- **Query 1:** `uv run fedcourts query --court scotus --era 2020s --limit 10`
  - **Stderr / reads:** `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
  - **Purpose & result:** Retrieved recent OT2026 SCOTUS dispositions and salience metadata in the local corpus (10 rows returned).
- **Query 2:** `uv run fedcourts query --court scotus --citation "555 U.S. 438" --citation "540 U.S. 398" --citation "509 U.S. 209" --limit 5`
  - **Stderr / reads:** `ranged corpus reads: 9 GET(s), 2359296 byte(s)` (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`)
  - **Purpose & result:** Checked whether *linkLine*, *Trinko*, or *Brooke Group* parallel cites were indexed on corpus rows; 0 rows returned as expected per the CLI note.
- **Query 3:** `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - **Stderr / reads:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - **Purpose & result:** Retrieved 5 recent OT2026 denied SCOTUS matters to compare baseline salience and distribution attributes.
- **Query 4:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - **Stderr / reads:** `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
  - **Purpose & result:** Retrieved 5 recent OT2026 granted SCOTUS matters (including paid cert grants *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12, `distribution_count: 3`; *Department of Justice v. McNutt*, No. 26-204, `distribution_count: 2`; and *U.S. DOGE Service v. U.S. District Court*, No. 25-1103, `distribution_count: 2`), confirming the multi-distribution trajectory of granted cert petitions.

## 2. CourtListener MCP Queries

- **Query 5:** `mcp_courtlistener_search(type="o", court="ca2", case_name="Cumulus Media New Holdings v. Nielsen")`
  - **Purpose & result:** Returned 1 opinion match (`query_id: "a187bb2a"`): *Cumulus Media New Holdings Inc. v. The Nielsen Co. (US), LLC*, No. 26-88, 182 F.4th 108 (2d Cir. July 13, 2026), Cluster ID 10927183, matching the opinion reproduced in the provisioned `appendix.txt` (Pet. App. 1a–55a).
- **Query 6:** `mcp_courtlistener_search(type="r", court="ca2", case_name="Cumulus Media New Holdings v. Nielsen")`
  - **Purpose & result:** Returned 2 RECAP docket matches in the Second Circuit (`query_id: "0368ec88"`): Docket ID 72151292 (No. 26-88, the preliminary-injunction appeal below) and Docket ID 74800092 (No. 26-2516, the subsequent enforcement appeal referenced at Pet. 10–11).
- **Query 7:** `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", num_results=30, query={"docket": 74800092, "fields": ["id", "entry_number", "date_filed", "description"]})`
  - **Purpose & result:** Returned the 30 most recent docket entries up to October 23, 2026 in Second Circuit No. 26-2516 (`query_id: "755fa83e"`), confirming that merits briefing on the second appeal (concerning the September 9, 2026 district-court enforcement order) completed on October 21, 2026 and argument is calendared for November 17, 2026.

## 3. Web Search

- None attempted (`used_web_search: false`).
