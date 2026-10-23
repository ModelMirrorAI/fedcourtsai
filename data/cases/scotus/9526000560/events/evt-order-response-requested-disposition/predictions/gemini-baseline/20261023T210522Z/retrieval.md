# Retrieval Log (`retrieval.md`)

## 1. Corpus Lookups (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 9526000560 --event evt-order-response-requested-disposition --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query "application for stay injunction border wall IIRIRA waiver" --court scotus --include-applications --limit 10`
   - Exit code 2 (CLI usage note: `fedcourts query` takes structured flags rather than free-text positional arguments; no corpus read performed).
3. `uv run fedcourts query "application for a stay preliminary injunction Solicitor General" --court scotus --include-applications --limit 15`
   - Exit code 2 (same parallel call before switching to structured flags; no corpus read performed).
4. `uv run fedcourts query --court scotus --disposition granted --include-applications --limit 10`
   - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
5. `uv run fedcourts query --court scotus --docket-number 26A124 --include-applications`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
6. `uv run fedcourts query --court scotus --docket-number 26A203 --include-applications`
   - `ranged corpus reads: 6 GET(s), 1441792 byte(s)`
7. `uv run fedcourts query --court scotus --docket-number 26A308 --include-applications`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
8. `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 10`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="r"`, `case_name="Friends of the Ruidosa Church"`)
   - Located originating district court RECAP docket: *Friends of the Ruidosa Church v. Mullin et al.*, No. 3:26-cv-01099 (W.D. Tex., `docket_id=73199706`, Judge Kathleen Cardone).
2. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=73199706`)
   - Confirmed docket metadata for W.D. Tex. No. 3:26-cv-01099.
3. `mcp_courtlistener_get_endpoint_schema` (`endpoint_id="docket-entries"`)
   - Checked filter and `order_by` schema for `docket-entries`.
4. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=73199706`, `order_by="-entry_number"`)
   - Listed recent docket entries in W.D. Tex. No. 3:26-cv-01099 (including entries 74–78).
5. `mcp_courtlistener_call_endpoint` (`endpoint_id="recap-documents"`, `docket_entry__docket=73199706`, `docket_entry__entry_number={"gte": 75}`)
   - Retrieved RECAP document IDs for the district court's October 14, 2026 Memorandum Opinion (`doc_id=497310911`, Doc. 75), Plaintiffs' Opposition to Motion to Stay (`doc_id=498016951`, Doc. 76), and the October 20, 2026 Order Denying Stay (`doc_id=498070832`, Doc. 78).
6. `mcp_courtlistener_read_document` (`recap_document_id=497310911`)
   - Read full text of Judge Cardone's October 14, 2026 Memorandum Opinion and Order (Doc. 75, 14 pages).
7. `mcp_courtlistener_read_document` (`recap_document_id=498070832`)
   - Read full text of Judge Cardone's October 20, 2026 Order Denying Motion to Stay Preliminary Injunction (Doc. 78, 6 pages).
8. `mcp_courtlistener_read_document` (`recap_document_id=498016951`, chunks `0, 1, 4, 5, 6, 7`)
   - Read Plaintiffs' Response in Opposition to Defendants' Motion to Stay Preliminary Injunction Pending Appeal (Doc. 76, 22 pages).
9. `mcp_courtlistener_search` (`type="o"`, `case_name` searches for *Center for Biological Diversity v. Trump*, *County of El Paso v. Chertoff*, *Border Infrastructure Environmental Litigation*, *Trump v. Sierra Club*, *Learning Resources v. Trump*, *Trump v. CASA*, *National Park Service v. National Trust*, *Department of Homeland Security v. League of Women Voters*, *FCC v. Brown*, *Trump v. California*, *Trump v. Cook*, *Mullin v. Doe*)
   - Located Supreme Court opinions for key cited authorities and recent OT2025–OT2026 emergency stay orders.
10. `mcp_courtlistener_read_document` & `mcp_courtlistener_search_document` (`opinion_id=11266028`)
    - Read excerpts of *Learning Resources, Inc. v. Trump*, No. 24-1287 (U.S. Feb. 20, 2026), regarding the major questions doctrine and Chief Justice Roberts's / Justice Barrett's / Justice Kavanaugh's opinions.
11. `mcp_courtlistener_read_document` (`opinion_id=11430669`)
    - Read *National Park Service v. National Trust for Historic Preservation in the United States*, No. 26A203 (U.S. Aug. 31, 2026).
12. `mcp_courtlistener_read_document` (`opinion_id=11451385`)
    - Read *Department of Homeland Security v. League of Women Voters*, No. 26A308 (U.S. Sept. 25, 2026).
13. `mcp_courtlistener_read_document` (`opinion_id=11501811`)
    - Read *Federal Communications Commission v. Brown*, No. 26A476 (U.S. Oct. 14, 2026).
14. `mcp_courtlistener_read_document` (`opinion_id=11424433`)
    - Read *Trump v. California*, No. 26A124 (U.S. Aug. 24, 2026).
15. `mcp_courtlistener_read_document` (`opinion_id=11347761`)
    - Read *Mullin v. Doe*, No. 25-1083 (U.S. June 25, 2026), regarding immigration jurisdiction-stripping bars on non-constitutional claims.
16. `mcp_courtlistener_search` & `mcp_courtlistener_call_endpoint` & `mcp_courtlistener_read_document` (`recap_document_id=494217277`)
    - Read D.C. Circuit stay denial order in *Kingdom v. Trump*, No. 26-5236 (D.C. Cir. Sept. 18, 2026), for comparison with `26A416`.
17. `mcp_courtlistener_analyze_citations`
    - Verified citations used in `reasoning.md` and `predicted_reasoning.md` against CourtListener.

## 3. Web Searches

- None.
