# Retrieval Log

## 1. Local Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000341" --event "evt-petition-disposition" --role predictor`
   - Resolved case (`scotus/9026000341`), corpus (`corpus/corpus.db`), and event (`data/cases/scotus/9026000341/events/evt-petition-disposition/event.yaml`) paths.
2. `uv run fedcourts query --help`
   - Inspected structured filter flags for `fedcourts query`.
3. `uv run fedcourts query --court scotus --judge Thomas --limit 10`
   - Transfer line: `ranged corpus reads: 715 GET(s), 187432960 byte(s)`
   - Returned 0 rows.
4. `uv run fedcourts query --court scotus --docket-number 25-466`
   - Transfer line: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned 1 row: `scotus/73215957` (*Ongkaruck Sripetch v. Securities and Exchange Commission*, No. 25-466, cert granted 2026-01-09, merits decided 2026-06-04, judgment `affirmed`, including amicus curiae Investor Choice Advocates Network).
5. `uv run fedcourts query --court scotus --party "Securities and Exchange Commission" --limit 25` (attempted)
   - Refused with CLI usage error (`No such option: --party`).

## 2. CourtListener MCP Tool Calls

1. `mcp_courtlistener_search(type="o", case_name="Sripetch v. SEC", fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber", "court_id"])`
   - Returned 1 result: *Sripetch v. SEC*, No. 25-466, `cluster_id: 10870059`, `dateFiled: 2026-06-04`.
2. `mcp_courtlistener_search(type="o", case_name="Spartan Securities", fields=["caseName", "citation", "dateFiled", "cluster_id", "docketNumber", "court_id"])`
   - Returned 2 results, including *U.S. Securities and Exchange Commission v. Spartan Securities Group, LTD*, No. 22-13129 (11th Cir.), `cluster_id: 10775540`, `dateFiled: 2026-01-16`.
3. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10870059, fields=["id", "case_name", "date_filed", "sub_opinions", "judges"])`
   - Returned cluster metadata for *Sripetch v. SEC* (`opinion_id: 11337516`, author Justice Neil Gorsuch).
4. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10775540, fields=["id", "case_name", "date_filed", "sub_opinions", "judges"])`
   - Returned cluster metadata for *SEC v. Spartan Securities Group, LTD* (`opinion_id: 11242127`).
5. `mcp_courtlistener_read_document(opinion_id=11337516, chunk_index=[0, 1, 2, 3], chunk_size=8000)` (attempted)
   - Returned transient upstream HTTP 502 error from CourtListener (`Client error '502 Bad Gateway'`).
6. `mcp_courtlistener_search_document(opinion_id=11242127, query="TJOFLAT")`
   - Returned 20 of 73 matches in the Eleventh Circuit opinion (`total_chars: 487215`), confirming that Judge Tjoflat's dissent focused on civil procedure and "shotgun pleading" under Federal Rules of Civil Procedure 8(a)(2) and 9(b).
7. `mcp_courtlistener_search_document(opinion_id=11337516, query="78u(d)(7)")`
   - Returned 20 of 26 matches in *Sripetch v. SEC* (`total_chars: 72765`), showing both Justice Gorsuch's opinion for the Court reserving the scope of 15 U.S.C. § 78u(d)(7) and Justice Thomas's concurrence discussing the circuit split between *Hallam* (5th Cir.) and *Ahmed* (2d Cir.).
8. `mcp_courtlistener_search_document(opinion_id=11337516, query="Treasury")`
   - Returned all 4 matches in *Sripetch v. SEC* discussing disgorgement deposits to the U.S. Treasury and citing the Brief for Investor Choice Advocates Network as Amicus Curiae.
9. `mcp_courtlistener_read_document(opinion_id=11242127, chunk_index=60, chunk_size=8000)`
   - Read the final chunk (`chunk_index: 60` of 61) of the Eleventh Circuit opinion in *SEC v. Spartan Securities Group, LTD* (the appendix of the SEC's complaint attached to Judge Tjoflat's dissent).
10. `mcp_courtlistener_read_document(opinion_id=11337516, chunk_index=[5, 6, 7, 8], chunk_size=8000)`
    - Read chunks 5–8 of *Sripetch v. SEC*, covering the end of the Court's opinion and Justice Thomas's concurring opinion.
11. `mcp_courtlistener_read_document(opinion_id=11337516, chunk_index=9, chunk_size=8000)`
    - Read the final chunk (`chunk_index: 9`) of *Sripetch v. SEC*, completing Justice Thomas's concurrence.

## 3. Web Searches

- None attempted.
