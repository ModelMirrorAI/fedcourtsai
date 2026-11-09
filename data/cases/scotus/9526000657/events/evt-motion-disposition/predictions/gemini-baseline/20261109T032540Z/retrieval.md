# Retrieval Log — `scotus/9526000657` (`evt-motion-disposition`)

## 1. Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000657" --event "evt-motion-disposition" --role predictor`
   - No ranged corpus read transfer line (resolved local case/corpus/event paths).
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Returned 5 recent OT2026 SCOTUS denials (`scotus/9026006013`, `scotus/9526000623`, `scotus/9526000634`, `scotus/9526000637`, `scotus/9526000644`), including pro se non-capital stay applications `26A637` and `26A644` denied without a response request or referral.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   - Returned 5 recent OT2026 SCOTUS grants (`scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`), including substantive stay grants `26A512` and `26A476` (both referred to the full Court with responses filed).
4. `uv run fedcourts query --court scotus --docket-number 26A655`
   - `ranged corpus reads: 15 GET(s), 3801088 byte(s)`
   - Returned `scotus/9526000655` (*M. P. v. Arizona Department of Child Safety*, extension application).
5. `uv run fedcourts query --court scotus --docket-number 26A656`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9526000656` (*Melchor Magdaleno-Garcia v. Texas*, extension application).
6. `uv run fedcourts query --court scotus --docket-number 26A658`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned companion application `scotus/9526000658` (*Paul Schultz v. H. Jason Gold*, No. 26A658, substantive application filed pro se by Paul David Schultz from `26-2404`).
7. `uv run fedcourts query --court scotus --docket-number 26A659`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9526000659` (*Kevin Duden v. Washington, et al.*, extension application).
8. `uv run fedcourts query --court scotus --docket-number 26A660`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9526000660` (*Jonathan D. Carr v. Kansas*, extension application).
9. `uv run fedcourts query --court scotus --docket-number 26A654`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned `scotus/9526000654` (*Andrew Lamont Brown v. Chance Andes, Warden*, extension application).
10. `uv run fedcourts query --court scotus --docket-number 26A661`
    - `ranged corpus reads: 707 GET(s), 185204736 byte(s)`
    - Returned note: no row for `26A661` in scope.
11. `uv run fedcourts query --court scotus --docket-number 26A662`
    - `ranged corpus reads: 720 GET(s), 188481536 byte(s)`
    - Returned note: no row for `26A662` in scope.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="r", court="ca4", docket_number="26-2406")`
   - Returned 1 result: Fourth Circuit Docket No. `26-2406`, *In re: Paul Schultz* (`docket_id: 74925989`), showing an unpublished per curiam opinion and judgment order filed on `2026-10-26` and a court order filed on `2026-11-04`.
2. `mcp_courtlistener_search(type="o", case_name="Schultz v. McCarthy")`
   - Returned 3 unrelated state-court opinions (*McCarthy v. Schultz* / *State v. Schultz*).
3. `mcp_courtlistener_search(type="r", case_name="Schultz v. McCarthy")`
   - Returned 8 RECAP dockets: 2 Fourth Circuit appeals (`26-2104`, `docket_id: 74648333`; `26-2103`, `docket_id: 74647848`), 5 Eastern District of Virginia bankruptcy appeals (`1:26-cv-02340-LMB-IDD`, `docket_id: 73714389`; `1:26-cv-02099-LMB-IDD`; `1:26-cv-01870-LMB-IDD`; `1:26-cv-01869-LMB-IDD`; `1:26-cv-00410-LMB-IDD`), and 1 Eastern District of Virginia Bankruptcy Court adversary proceeding (`25-01061`, `docket_id: 71895215`, Judge Klinette H. Kindred, Chapter 7 Trustee Kevin McCarthy).
4. `mcp_courtlistener_search(type="o", court="ca4", docket_number="26-2406")`
   - Returned 0 results in the opinion search index (the cluster was subsequently retrieved via the docket endpoint).
5. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 74925989, "fields": ["id", "entry_number", "date_filed", "description", "recap_documents"]})`
   - Returned the docket entries for Fourth Circuit No. `26-2406` (`docket_id: 74925989`), entries 9, 11, 12, and 15.
6. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=74925989, fields=["id", "case_name", "docket_number", "cause", "nature_of_suit", "date_filed", "date_terminated", "originating_court_information"])`
   - Failed with invalid field error (`originating_court_information` is `original_court_info` on the `dockets` endpoint).
7. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=74925989, fields=["id", "case_name", "docket_number", "cause", "nature_of_suit", "date_filed", "date_terminated", "appeal_from_str", "panel_str", "appellate_case_type_information", "clusters"])`
   - Returned docket metadata for `74925989` (*In re: Paul Schultz*, No. `26-2406`), linking to cluster `11046332`.
8. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=71895215, fields=["id", "case_name", "docket_number", "cause", "nature_of_suit", "date_filed", "date_terminated"])`
   - Returned metadata for Bankr. E.D. Va. adversary proceeding `25-01061` (*Schultz v. McCarthy*, filed `2025-11-10`).
9. `mcp_courtlistener_search(type="o", court="ca4", case_name="Paul Schultz")`
   - Returned 1 unrelated 1997 Fourth Circuit opinion (*United States v. Dorlouis*).
10. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 71895215, "fields": ["id", "entry_number", "date_filed", "description"]})`
    - Returned docket entry dates/numbers for Bankr. E.D. Va. `25-01061`.
11. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=11046332, fields=["id", "case_name", "date_filed", "citations", "judges", "sub_opinions", "Precedential_status", "syllabus", "summary"])`
    - Failed with invalid field error (`Precedential_status` should be lowercase `precedential_status`).
12. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=74648333, fields=["id", "case_name", "docket_number", "clusters", "date_filed", "date_terminated"])`
    - Returned Fourth Circuit docket `26-2104` (*Paul Schultz v. Kevin McCarthy*, `clusters: []`).
13. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=74647848, fields=["id", "case_name", "docket_number", "clusters", "date_filed", "date_terminated"])`
    - Returned Fourth Circuit docket `26-2103` (*Paul Schultz v. Kevin McCarthy*, `clusters: []`).
14. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=11046332, fields=["id", "case_name", "date_filed", "citations", "judges", "sub_opinions", "precedential_status", "syllabus", "summary", "disposition"])`
    - Returned cluster `11046332` (*In re: Paul Schultz*, `date_filed: "2026-10-26"`, `precedential_status: "Unpublished"`, `sub_opinions: [".../opinions/11514107/"]`).
15. `mcp_courtlistener_search(type="r", court="ca4", case_name="Paul Schultz")`
    - Returned 28 Fourth Circuit RECAP dockets involving Paul Schultz, including mandamus dockets `26-2404` (`74925991`), `26-2405` (`74925990`), `26-2406` (`74925989`), and consolidated bankruptcy appeals `25-2493` (`72056709`).
16. `mcp_courtlistener_read_document(opinion_id=11514107)`
    - Read the full text (3,713 chars) of the Fourth Circuit's October 26, 2026 unpublished per curiam opinion in *In re: Paul Schultz*, No. 26-2406 (on petition for writ of mandamus to E.D. Va. `1:26-cv-02340-LMB-IDD`), denying mandamus to disqualify Judge Brinkema and denying stay/expedite motions as moot.
17. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=72056709, fields=["id", "case_name", "docket_number", "clusters"])`
    - Returned Fourth Circuit No. `25-2493` (*Clear Sky Financial, LLC v. Paul Schultz*), linking to cluster `10927073`.
18. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=74925991, fields=["id", "case_name", "docket_number", "clusters"])`
    - Returned Fourth Circuit No. `26-2404` (*In re: Paul Schultz*), linking to cluster `11044676`.
19. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=74925990, fields=["id", "case_name", "docket_number", "clusters"])`
    - Returned Fourth Circuit No. `26-2405` (*In re: Paul Schultz*), linking to cluster `11044675`.
20. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=11044676, fields=["id", "case_name", "date_filed", "sub_opinions", "precedential_status"])`
    - Returned cluster `11044676` (`date_filed: "2026-10-22"`, `opinion_id: 11512446`).
21. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=11044675, fields=["id", "case_name", "date_filed", "sub_opinions", "precedential_status"])`
    - Returned cluster `11044675` (`date_filed: "2026-10-22"`, `opinion_id: 11512445`).
22. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10927073, fields=["id", "case_name", "date_filed", "sub_opinions", "precedential_status"])`
    - Returned cluster `10927073` (`date_filed: "2026-07-10"`, `opinion_id: 11394611`).
23. `mcp_courtlistener_read_document(opinion_id=11512446)`
    - Read the full text of the Fourth Circuit's October 22, 2026 unpublished per curiam opinion in *In re: Paul Schultz*, No. 26-2404 (`1:26-cv-02804-LMB-IDD`).
24. `mcp_courtlistener_read_document(opinion_id=11512445)`
    - Read the full text of the Fourth Circuit's October 22, 2026 unpublished per curiam opinion in *In re: Paul Schultz*, No. 26-2405 (`1:26-cv-01125-LMB-IDD`).
25. `mcp_courtlistener_read_document(opinion_id=11394611)`
    - Read the full text of the Fourth Circuit's July 10, 2026 unpublished per curiam opinion in *Clear Sky Financial, LLC v. Paul Schultz* et al. (Nos. 25-2195, 25-2293, 25-2295, 25-2405, 25-2406, 25-2485, 25-2493, and 26-1086), detailing the Chapter 11-to-Chapter 7 conversion and underlying bankruptcy appeals before Judge Brinkema.
26. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 73714389, "fields": ["id", "entry_number", "date_filed", "description"]})`
    - Returned empty list (no PACER docket entries ingested into RECAP for E.D. Va. `1:26-cv-02340-LMB-IDD`).
