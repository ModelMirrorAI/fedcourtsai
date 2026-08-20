# Retrieval

- Consulted the committed `metrics/statpack.md` and `metrics/statpack.json` for the sal-v3 prior-Term arrival anchor, originating-circuit context, and relist/CVSG population shapes. This was a local committed base-rate artifact, not a live corpus query.
- CourtListener MCP `search`: `Hilsenrath School District Chathams Stone Kennedy`, opinions, Third Circuit, five-result limit. Returned *Libby Hilsenrath v. School District of the Chathams*, 136 F.4th 484 (May 5, 2025).
- CourtListener MCP `search`: `Childs Webster Cutter Lemon Kennedy`, opinions, Seventh Circuit, five-result limit. Returned *Shareef Childs v. Cheryl Webster* (Mar. 4, 2026).
- CourtListener MCP `search`: `Stinson Fayetteville Ten Commandments public school`, opinions, Western District of Arkansas, five-result limit. Returned no result.
- CourtListener MCP `search`: repeated the Hilsenrath query with the `opinions` field to obtain opinion document id 10983421.
- CourtListener MCP `search`: repeated the Childs query with the `opinions` field to obtain opinion document id 11270364.
- CourtListener MCP `search_document`: searched opinion ids 10983421 and 11270364 for `Stone`.
- CourtListener MCP `search_document`: searched opinion ids 10983421 and 11270364 for `unless and until`.
- CourtListener MCP `search_document`: searched opinion ids 10983421 and 11270364 for `Kennedy`.

No web search and no live corpus query were used. I did not query the Supreme Court case or its outcome.
