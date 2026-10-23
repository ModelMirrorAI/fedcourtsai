# Retrieval Log

## 1. Corpus Tooling (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73500240" --event "evt-order-relist-disposition" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 15`
   - Transfer: `ranged corpus reads: 775 GET(s), 203161600 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
   - Transfer: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
4. `uv run fedcourts query --court scotus --docket-number "25-297"`
   - Transfer: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Retrieved prior `scotus/72528904` (*Jacob P. Zorn v. Shela M. Linton*, No. 25-297, decided March 23, 2026).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type: "o"`, `citation: "146 S. Ct. 926"`) — checked citation from BIO p. 13.
2. `mcp_courtlistener_search` (`type: "o"`, `citation: "605 U.S. 73"`) — verified *Barnes v. Felix*, 605 U.S. 73 (2025) (`cluster_id: 10776852`, `opinion_id: 11243439`).
3. `mcp_courtlistener_search` (`type: "o"`, `court: "scotus"`, `case_name: "Zorn v. Linton"`) — located *Zorn v. Linton*, No. 25-297, 607 U.S. ___ (Mar. 23, 2026) (`cluster_id: 10813527`, `opinion_id: 11280281`).
4. `mcp_courtlistener_read_document` (`opinion_id: 11280281`) — read the per curiam summary reversal and dissent in *Zorn v. Linton* (2026).
5. `mcp_courtlistener_read_document` (`opinion_id: 11280281`, `chunk_index: [0, 1]`, `chunk_size: 8000`) — read chunks 0 and 1 of *Zorn v. Linton* (2026).

## 3. Web Searches

None.
