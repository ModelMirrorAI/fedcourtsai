# Retrieval Log: `scotus/9026000583` (`evt-petition-arrival-disposition`)

- **Mode:** `forward` (`record/context.json` → `"mode": "forward"`, `"cutoff": "2026-11-04"`, `"decided_before": null`)
- **Leakage Guard:** Forward mode — the event is unresolved (`opened_at: 2026-11-03`, `resolved: false`), so external retrieval is unrestricted.

---

## 1. Local Corpus Queries (`fedcourts query`)

1. **Query 1 — Recent 2020s SCOTUS priors:**
   - **Command:** `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - **Transfer stderr:** `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - **Outcome:** Returned 10 recent 2020s SCOTUS rows (dispositions, salience scores, and representation metadata).

2. **Query 2 — Recent 2020s SCOTUS denied priors:**
   - **Command:** `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 5`
   - **Transfer stderr:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Outcome:** Returned 5 recent denied SCOTUS rows from the warm cache.

3. **Query 3 — Citation lookup check (*Bell v. Hood*, `327 U.S. 678`):**
   - **Command:** `uv run fedcourts query --court scotus --citation "327 U.S. 678" --limit 5`
   - **Transfer stderr:** `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - **Outcome:** Empty result with sparse-citation coverage note (`only 200 row(s) in scope (scotus) carry any reporter citation at all`).

4. **Query 4 — Target docket lookup (`26-583`):**
   - **Command:** `uv run fedcourts query --court scotus --docket-number 26-583`
   - **Transfer stderr:** `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - **Outcome:** Returned the corpus row for `scotus/9026000583` (`originating_court = "ca11"`, `originating_docket_number = "25-12004"`, `salience_score = 0.0309`, `counsel_of_record = false`).

---

## 2. CourtListener MCP Retrieval

1. **Opinion Search 1 (`mcp_courtlistener_search`, `type="o"`):**
   - **Parameters:** `court="ca11"`, `docket_number="25-12004"`, `case_name="Shaikh v. Fox News"`, `fields=["caseName", "docketNumber", "dateFiled", "court_id", "cluster_id", "id", "snippet"]`
   - **Outcome:** Returned 1 match (`cluster_id = 10870293`, *Ahmed Shaikh v. Fox News Network, LLC*, No. 25-12004, filed `2026-06-04`).

2. **RECAP Search 1 (`mcp_courtlistener_search`, `type="r"`):**
   - **Parameters:** `docket_number="25-12004"`, `case_name="Shaikh v. Fox News"`, `fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id"]`
   - **Outcome:** Returned 1 match (`docket_id = 73442430`, `court_id = "ca11"`, No. `25-12004`).

3. **RECAP Search 2 (`mcp_courtlistener_search`, `type="r"`):**
   - **Parameters:** `case_name="Shaikh v. Fox News"`, `fields=["caseName", "docketNumber", "dateFiled", "court_id", "docket_id", "description"]`
   - **Outcome:** Returned 2 matches: Eleventh Circuit `docket_id = 73442430` (`25-12004`) and Middle District of Florida `docket_id = 69301906` (*Shaikh v. Fox News Network, LLC*, No. `6:24-cv-01894`, filed `2024-10-22`).

4. **Cluster Metadata Lookup (`mcp_courtlistener_get_endpoint_item`, `endpoint_id="clusters"`):**
   - **Parameters:** `item_id=10870293`, `fields=["id", "case_name", "date_filed", "judges", "precedential_status", "sub_opinions", "docket_id", "nature_of_suit"]`
   - **Outcome:** Returned cluster `10870293` (`precedential_status = "Published"`, `sub_opinions = [".../opinions/11337751/"]`).

5. **District Court Docket Metadata Lookup (`mcp_courtlistener_get_endpoint_item`, `endpoint_id="dockets"`):**
   - **Parameters:** `item_id=69301906`, `fields=["id", "case_name", "cause", "nature_of_suit", "date_filed", "date_terminated"]`
   - **Outcome:** Returned docket `69301906` (`cause = "18:2511 Wiretapping"`, `nature_of_suit = "890 Other Statutory Actions"`, `date_terminated = "2025-05-20"`).

6. **District Court Docket Entries Lookup (`mcp_courtlistener_call_endpoint`, `endpoint_id="docket-entries"`):**
   - **Parameters:** `num_results=30`, `query={"docket": 69301906, "fields": ["id", "entry_number", "date_filed", "description", "recap_documents"]}`
   - **Outcome:** Returned recent docket entries for `6:24-cv-01894`, including Entry 91 (`recap_document_id = 440098663`, May 20, 2025 Order dismissing the complaint under Rule 12(b)(1) as patently insubstantial, with full `plain_text`), Entry 93 (Notice of Appeal), Entry 104 (USCA Opinion, June 5, 2026), and Entry 105 (USCA Mandate, July 29, 2026).

7. **Eleventh Circuit Opinion Full Text (`mcp_courtlistener_read_document`):**
   - **Parameters:** `opinion_id=11337751`
   - **Outcome:** Returned full text (18,486 chars) of the published *per curiam* opinion in *Ahmed Shaikh v. Fox News Network, LLC, et al.*, No. 25-12004 (11th Cir. June 4, 2026) (Before Newsom, Brasher, and Tjoflat, JJ.), affirming the Rule 12(b)(1) dismissal under *Bell v. Hood*.

8. **Opinion Search 2 (`mcp_courtlistener_search`, `type="o"`):**
   - **Parameters:** `court="ca11"`, `case_name="Ahmed Shaikh"`, `fields=["caseName", "docketNumber", "dateFiled", "cluster_id"]`
   - **Outcome:** Confirmed `cluster_id = 10870293` is the sole Eleventh Circuit opinion involving petitioner Ahmed Shaikh.
