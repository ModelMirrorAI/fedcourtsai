# Retrieval Log (`retrieval.md`)

## 1. Corpus Tooling (`fedcourts query` / `fedcourts open-events`)
None.

## 2. CourtListener MCP Lookups
1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Scanlan v. Coalition for Open Democracy"`) — returned 0 results (October 22, 2026 detached order/dissent not yet indexed in CourtListener opinions).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="26A512"`) — returned 0 results.
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2026-10-20"`, `q="Scanlan OR "Coalition for Open Democracy" OR "26A512""`) — returned 0 results.

## 3. Web Searches and Fetches
1. `google_web_search` (`query=""26A512" "Scanlan" "Jackson" dissenting October 22 2026"`) — located the Supreme Court's October 22, 2026 order and Justice Jackson's dissenting opinion in *Scanlan v. Coalition for Open Democracy*, No. 26A512.
2. `web_fetch` (LII / SupremeCourt.gov order PDF for `26A512`, *Scanlan v. Coalition for Open Democracy*) — read the verbatim text of the Supreme Court's one-paragraph majority order (citing *Republican National Committee v. Democratic National Committee*, 589 U.S. 423, 424 (2020), and *People Not Politicians v. Onder*, 609 U.S. ___ (Sept. 25, 2026)) and Justice Jackson's solo dissenting opinion.
