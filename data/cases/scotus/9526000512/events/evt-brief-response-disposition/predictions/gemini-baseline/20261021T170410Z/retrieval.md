# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --include-applications --limit 10`
   - Transfer: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`

*(Note: Two initial `fedcourts query` invocations with free-text arguments exited with CLI usage error code 2 before any corpus reads occurred.)*

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="r"`, `case_name="Coalition for Open Democracy v. Scanlan"`) — checked RECAP docket index for the First Circuit appeal (`No. 26-2132`, filed 2026-10-06).
2. `mcp_courtlistener_search` (`type="o"`, `case_name="Coalition for Open Democracy v. Scanlan"`) — returned earlier D.N.H. litigation (`24-cv-312-SE`, May 20, 2025).
3. `mcp_courtlistener_search` (`type="o"`, `case_name="People Not Politicians v. Onder"`) — located Supreme Court stay opinion (`No. 26A388`, Sept. 25, 2026, `opinion_id=11451693`).
4. `mcp_courtlistener_read_document` (`opinion_id=11451693`) — read the Supreme Court's September 25, 2026 per curiam stay opinion in *People Not Politicians v. Onder*, 609 U.S. ___ (2026) (No. 26A388), cited by both parties on *Purcell*.
5. `mcp_courtlistener_search` (`type="o"`, `case_name="National Republican Congressional Committee v. Brown"`) — located Supreme Court stay opinion (`No. 26A274`, Sept. 4, 2026, `opinion_id=11435097`).
6. `mcp_courtlistener_read_document` (`opinion_id=11435097`) — read the Supreme Court's September 4, 2026 per curiam stay opinion in *National Republican Congressional Committee v. Brown*, 609 U.S. ___ (2026) (No. 26A274), cited by Respondent on the *Hollingsworth* stay factors.
7. `mcp_courtlistener_search` (`type="r"`, `docket_number="1:26-cv-00647"`) — verified D.N.H. docket entry date (`Coalition for Open Democracy v. NH Secretary of State`, `1:26-cv-00647`, filed 2026-08-11).

## Web Searches

- None.
