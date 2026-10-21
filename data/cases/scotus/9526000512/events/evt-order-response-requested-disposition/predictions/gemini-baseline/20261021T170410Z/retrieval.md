# Retrieval Log (`retrieval.md`)

## 1. Corpus Tooling (`fedcourts query`)

1. `uv run fedcourts query "Purcell election stay preliminary injunction" --court scotus --limit 10`
   - Result: CLI usage error (exit code 2; `fedcourts query` accepts structured filter flags only, no positional free-text argument).
2. `uv run fedcourts query "stay application Secretary of State election" --court scotus --limit 10`
   - Result: CLI usage error (exit code 2; `fedcourts query` accepts structured filter flags only).
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --include-applications --limit 10`
   - Transfer stderr line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
4. `uv run fedcourts query --court scotus --disposition denied --era 2020s --include-applications --limit 10`
   - Transfer stderr line: `ranged corpus reads: 0 GET(s), 0 byte(s)`

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="r"`, `court="nhd"`, `case_name="Coalition for Open Democracy v. Scanlan"`) — 0 results under exact `case_name` filter.
2. `mcp_courtlistener_search` (`type="o"`, `q=""Purcell v. Gonzalez" "preliminary injunction" stay "Secretary of State""`) — retrieved general appellate opinions citing *Purcell v. Gonzalez*.
3. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_before="2026-10-15"`, `q=""Purcell v. Gonzalez" stay"`) — retrieved 16 SCOTUS opinions citing *Purcell*, including *People Not Politicians v. Onder* (`26A388`, Sept. 25, 2026).
4. `mcp_courtlistener_call_endpoint` (`endpoint_id="clusters"`, `id=10984030`) — resolved opinion ID `11451693` for *People Not Politicians v. Onder* (`26A388`).
5. `mcp_courtlistener_search` (`type="o"`, `court=["nhd", "ca1"]`, `filed_before="2026-10-15"`, `q=""Coalition for Open Democracy""`) — 0 indexed opinions.
6. `mcp_courtlistener_search` (`type="r"`, `court=["nhd", "ca1"]`, `filed_before="2026-10-15"`, `q=""Coalition for Open Democracy" "Scanlan""`) — located 1st Cir. docket `26-2132` (`docket_id: 74929205`).
7. `mcp_courtlistener_read_document` (`opinion_id=11451693`) — read per curiam stay opinion in *People Not Politicians v. Onder*, No. 26A388 (U.S. Sept. 25, 2026).
8. `mcp_courtlistener_search` (`type="rd"`, `docket_number="26-2132"`) — listed RECAP filings in 1st Cir. No. 26-2132.
9. `mcp_courtlistener_search` (`type="rd"`, `docket_number="1:26-cv-00647"`) — listed RECAP filings in D.N.H. No. 1:26-cv-00647-JL.
10. `mcp_courtlistener_search` (`type="rd"`, `court="nhd"`, `docket_number="1:26-cv-00647"`, `entry_date_filed_after="2026-10-01"`, `entry_date_filed_before="2026-10-15"`, `available_only=true`) — identified available D.N.H. orders (`Doc. 63`, `Doc. 64`, `Doc. 72`).
11. `mcp_courtlistener_search` (`type="rd"`, `court="ca1"`, `docket_number="26-2132"`, `entry_date_filed_before="2026-10-15"`, `available_only=true`) — identified available 1st Cir. filings (`Order Denying Stay`, Appellee's Response, RNC Amicus Brief).
12. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="26A274"`) — located *National Republican Congressional Committee v. Brown* (`cluster_id: 10967483`, Sept. 4, 2026).
13. `mcp_courtlistener_read_document` (`recap_document_id=496221696`) — read D.N.H. Doc. 64 (`PRELIMINARY INJUNCTION ORDER`, Oct. 5, 2026).
14. `mcp_courtlistener_read_document` (`recap_document_id=496599428`) — read D.N.H. Doc. 72 (`ORDER DENYING STAY`, Oct. 7, 2026).
15. `mcp_courtlistener_read_document` (`recap_document_id=497497832`) — read 1st Cir. Order Denying Stay (Oct. 14, 2026, Gelpí & Aframe; Dunlap dissenting).
16. `mcp_courtlistener_read_document` (`recap_document_id=496088272`, chunks `0, 1, 7, 8, 9, 10, 11, 12`) — read D.N.H. Doc. 63 (`ORDER GRANTING PARTIAL PRELIMINARY INJUNCTIVE RELIEF`, Oct. 2, 2026).
17. `mcp_courtlistener_read_document` (`recap_document_id=497197160`, chunks `0–6`) — read Appellee Coalition for Open Democracy's Response to Renewed Emergency Motion for a Stay Pending Appeal in 1st Cir. No. 26-2132 (Oct. 13, 2026).
18. `mcp_courtlistener_call_endpoint` (`endpoint_id="clusters"`, `id=10967483`) — resolved opinion ID `11435097` for *NRCC v. Brown* (`26A274`).
19. `mcp_courtlistener_read_document` (`opinion_id=11435097`) — read per curiam stay opinion in *NRCC v. Brown*, No. 26A274 (U.S. Sept. 4, 2026).
20. `mcp_courtlistener_read_document` (`recap_document_id=496834525`) — read D.N.H. Doc. 43 (`ORDER DENYING PRELIMINARY INJUNCTIVE RELIEF` as to Sept. 8 primary election, Sept. 1, 2026).
21. `mcp_courtlistener_read_document` (`recap_document_id=497497833`) — read Amicus Curiae Brief of Republican National Committee Supporting Stay in 1st Cir. No. 26-2132 (Oct. 10, 2026).
22. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2025-10-01"`, `filed_before="2026-10-15"`, `q=""Purcell" OR "Malliotakis" OR "Milligan""`) — checked recent 2026 SCOTUS opinions citing *Purcell*.

## 3. Web Searches
None.
