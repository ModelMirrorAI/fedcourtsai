# Retrieval Log (`retrieval.md`)

## 1. Local Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --originating-court ca4 --limit 10`
   - Result: CLI usage error (`No such option: --originating-court`), no corpus read performed.
2. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - Transfer line: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `docket_number="25-2149"`) — 0 indexed opinion-cluster hits.
2. `mcp_courtlistener_search` (`type="o"`, `case_name="Eastern Panhandle Anesthesia"`) — 0 indexed opinion-cluster hits.
3. `mcp_courtlistener_search` (`type="r"`, `case_name="Eastern Panhandle Anesthesia"`) — returned 2 RECAP dockets: Fourth Circuit Docket `71455680` (`Timothy Hall v. Eastern Panhandle Anesthesia Associates`, No. `25-2149`) and N.D. W. Va. Docket `68547595` (`Hall v. Eastern Panhandle Anesthesia Associates`, No. `3:24-cv-00061`).
4. `mcp_courtlistener_search` (`type="r"`, `docket_number="25-2149"`, `party_name="Eastern Panhandle"`) — retrieved RECAP docket metadata and sample documents for CA4 No. `25-2149`.
5. `mcp_courtlistener_search` (`type="r"`, `docket_number="3:24-cv-00061"`, `party_name="Eastern Panhandle"`) — retrieved RECAP docket metadata and sample documents for N.D. W. Va. No. `3:24-cv-00061`.
6. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=71455680`) — retrieved the 40 docket entries for CA4 No. `25-2149` (showing Entry 2 informal briefing order on 2025-09-25, Entries 36–37 unpublished per curiam opinion and judgment on 2026-06-23, and Entry 40 order denying rehearing on 2026-07-21).
7. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=68547595`, `num_results=50`) — retrieved the most recent 50 docket entries for N.D. W. Va. No. `3:24-cv-00061`.
8. `mcp_courtlistener_read_document` (`recap_document_id=399647335`, `chunk_index=0`) — read the opening chunk of the pro se Complaint in N.D. W. Va. No. `3:24-cv-00061` (ECF No. 1).
9. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=436037233`) — retrieved N.D. W. Va. Docket Entry 72 (`recap_document_id=450473624`), including the full plain text of Chief Judge Gina M. Groh's August 27, 2025 Memorandum Opinion and Order dismissing seven sets of defendants and staying the action pending arbitration as to Eastern Panhandle Anesthesia Associates.
10. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=468399591`) — checked N.D. W. Va. Entry 84 (USCA Per Curiam opinion metadata; document PDF not uploaded to RECAP).
11. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=468399584`) — checked N.D. W. Va. Entry 85 (USCA Judgment metadata).
12. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=471563970`) — checked N.D. W. Va. Entry 87 (USCA Order denying rehearing metadata).
13. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=481785989`) — checked N.D. W. Va. Entry 91 (Roseboro Notice filed 2026-10-16).
14. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=472480446`) — checked N.D. W. Va. Entry 88 (USCA Mandate filed 2026-07-29).
15. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=481367784`) — checked N.D. W. Va. Entry 89 (Motion for Judgment under Rule 54(b) filed 2026-10-13).
16. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=481463100`) — checked N.D. W. Va. Entry 90 (Motion to Dismiss for Lack of Prosecution filed 2026-10-14).

## 3. Web Searches
- None performed.
