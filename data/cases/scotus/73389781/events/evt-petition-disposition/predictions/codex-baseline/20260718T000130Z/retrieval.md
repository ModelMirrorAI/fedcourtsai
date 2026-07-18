# Retrieval beyond provisioned inputs

- Read `metrics/statpack.md` and `metrics/statpack.json` for modern discretionary-cert, Term 2025 paid/IFP, relist, CVSG, and originating-court base rates. No `fedcourts query` or `open-events` lookup was used.
- CourtListener MCP opinion search: `q=\"\\\"civil contempt\\\" \\\"ability to pay\\\" \\\"Turner v. Rogers\\\"\"`, opinions filed before 2026-07-18, 8 results. It returned *Turner v. Rogers* and several state appellate applications, including *Stehle v. Zimmerebner*.
- CourtListener MCP opinion-item lookup for result id 10815464. The returned document did not match the search-result caption, so it was treated as unusable and did not affect the forecast.
- CourtListener MCP opinion search: `q=\"\\\"private money judgment\\\" contempt \\\"imprisonment for debt\\\" divorce\"`, opinions filed before 2026-07-18, 10 requested results. It returned no results.
- CourtListener MCP opinion search: `q=\"contempt enforce money judgment \\\"imprisonment for debt\\\" divorce\"`, opinions filed before 2026-07-18, 10 results. It returned state cases including *In re Contempt of Pappas*, *Collins v. Collins*, *English v. Davenport*, *Stehle v. Zimmerebner*, and *Hamilton v. Regan*.
- CourtListener MCP opinion-item lookup for *Stehle v. Zimmerebner* (opinion id 3218829). The service returned HTTP 429, so no opinion text from that lookup was used.
- No web search was used.
