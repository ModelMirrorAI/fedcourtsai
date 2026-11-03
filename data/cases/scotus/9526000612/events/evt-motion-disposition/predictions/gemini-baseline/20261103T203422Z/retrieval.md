# Retrieval Log: `scotus/9526000612` (`evt-motion-disposition`)

## 1. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 20`
   - Transfer line: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Result: Returned 20 recent OT 2026 SCOTUS dockets (including substantive applications `26A606`, `26A613`, `26A617`, `26A618`, `26A499`, `26A535`, `26A532`, `26A512`, `26A555`, `26A556`, `26A416`, `26A545`, `26A524`, `26A530`, `26A536`).
2. `uv run fedcourts query --court cadc --era 2020s --limit 20`
   - Transfer line: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Result: Returned 20 recent D.C. Circuit dockets from the corpus.
3. `uv run fedcourts query --court scotus --docket-number 24A730`
   - Transfer line: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned `scotus/72416811` (*Martin Akerman v. Merit Systems Protection Board*, No. `24A730`, filed `2025-01-24`, decided `2025-03-24`, `disposition: "denied"`, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`).
4. `uv run fedcourts query --court scotus --docket-number 24A731`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/72416812` (*Martin Akerman v. Merit Systems Protection Board*, No. `24A731`, filed `2025-01-24`, decided `2025-03-24`, `disposition: "denied"`, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`).
5. `uv run fedcourts query --court scotus --docket-number 26A235`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9526000235` (*Martin Akerman v. United States District Court for the District of Nevada, et al.*, No. `26A235`, `application_kind: "extension"`, granted `2026-08-21`).
6. `uv run fedcourts query --court scotus --docket-number 23-6709`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72481974` (*Martin Akerman v. United States*, No. `23-6709`, originating from CADC `23-5229`, cert denied `2024-03-18`).
7. `uv run fedcourts query --court scotus --docket-number 23-6710`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/72481976` (*Martin Akerman v. Sherri Doiron*, No. `23-6710`, originating from CADC `23-5230`, cert denied `2024-04-15`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="r", docket_number="26-5131", fields=["caseName", "docketNumber", "court_id", "dateFiled", "docket_id", "absolute_url"])`
   - Result: Returned 57 results across federal bankruptcy/district dockets matching `26-5131`.
2. `mcp_courtlistener_search(type="o", case_name="Akerman v. Merit Systems Protection Board", fields=["caseName", "docketNumber", "court_id", "dateFiled", "citation", "cluster_id", "opinions"])`
   - Result: Returned `count: 0`.
3. `mcp_courtlistener_search(type="d", party_name="Martin Akerman")`
   - Result: Failed with transient MCP tool error `fetch failed`.
4. `mcp_courtlistener_search(type="o", case_name="Akerman", order_by="dateFiled desc", num_results=20, fields=["caseName", "docketNumber", "court_id", "dateFiled", "cluster_id"])`
   - Result: Returned 52 opinions with "Akerman" in the case name (none for Martin Akerman).
5. `mcp_courtlistener_search(type="d", court="cadc", docket_number="26-5131", fields=["caseName", "docketNumber", "court_id", "dateFiled", "docket_id"])`
   - Result: Returned 1 match: *Martin Akerman v. MSPB*, `court_id: "cadc"`, `docketNumber: "26-5131"`, `docket_id: 73235695`.
6. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=73235695, fields=["id", "case_name", "docket_number", "date_filed", "date_terminated", "nature_of_suit", "cause", "originating_court_information", "clusters", "audio_files"])`
   - Result: Returned field-name validation error (`originating_court_information` not a valid field name on `dockets`).
7. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 73235695, "fields": ["id", "date_filed", "entry_number", "description", "recap_documents"]})`
   - Result: Returned 19 docket entries for CADC `26-5131` (from April 23, 2026 docketing through October 19, 2026 Per Curiam Order of Special Panel).
8. `mcp_courtlistener_search(type="o", q=""Martin Akerman"")`
   - Result: Returned 10 opinions mentioning "Martin Akerman", including Fourth Circuit No. `22-1628` (*Martin Akerman v. Austin*, 2023-02-27) and Federal Circuit No. `2024-1313` (*In re Martin Akerman*, 2024-05-15).
9. `mcp_courtlistener_search(type="r", q=""Martin Akerman"")`
   - Result: Returned 49 RECAP dockets involving Martin Akerman across `cadc`, `ca9`, `cafc`, `dcd`, `nvd`, `vaed`, and `cit`, including `cadc` No. `26-1285` (`docket_id: 74946868`, *In re: Martin Akerman*) and `dcd` No. `1:23-cv-02574` (`docket_id: 67786074`, *AKERMAN v. MERIT SYSTEMS PROTECTION BOARD*).
10. `mcp_courtlistener_read_document(recap_document_id=496946683)`
    - Result: Read full text (7,247 chars) of Akerman's October 9, 2026 Emergency Petition for Writ of Mandamus in CADC No. `26-1285`, which summarized the procedural posture of `dcd` No. `1:23-cv-02574-RDM` (including the April 18, 2026 order at ECF 98) and the interlocutory appeal in CADC No. `26-5131`.
11. `mcp_courtlistener_read_document(recap_document_id=496946684)`
    - Result: Read full text (7,698 chars) of Akerman's October 9, 2026 Emergency Motion to Expedite in CADC No. `26-1285`.
12. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 67786074, "fields": ["id", "date_filed", "entry_number", "description", "recap_documents"]})`
    - Result: Returned first page (20 entries) of `dcd` No. `1:23-cv-02574` (ECF 106–123, April 23, 2026 to October 9, 2026).
13. `mcp_courtlistener_get_more_results(query_id="a7beebaf", num_results=30)`
    - Result: Returned next 24 entries of `dcd` No. `1:23-cv-02574` (ECF 38–105, July 10, 2025 to April 21, 2026, including Judge Randolph D. Moss's detailed Minute Orders and the April 18, 2026 omnibus denial order at ECF 98 and April 20, 2026 Notice of Interlocutory Appeal at ECF 103).
14. `mcp_courtlistener_call_endpoint(endpoint_id="dockets", query={"court": "cadc", "docket_number": "26-5131", "fields": ["id", "case_name", "docket_number", "date_filed", "date_terminated", "appeal_from_str", "panel_str", "assigned_to_str"]})`
    - Result: Returned docket metadata for CADC `26-5131` (`id: 73235695`).
15. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 74946868, "fields": ["id", "date_filed", "entry_number", "description", "recap_documents"]})`
    - Result: Returned 5 docket entries for CADC `26-1285` (October 9–10, 2026).

## 3. Web Searches

None attempted.
