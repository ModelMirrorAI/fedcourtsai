# Retrieval Log (`scotus/73500250`)

## 1. Local CLI & Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 73500250 --event evt-order-call-for-response-disposition --role predictor`
   - Returned case, corpus, and event paths.
2. `uv run fedcourts query --help`
   - Checked structured filter flags.
3. `uv run fedcourts query --court scotus --era 2020s --decided-before 2026-07-28 --limit 10`
   - Transfer line: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   - Returned 10 resolved SCOTUS priors decided before 2026-07-28.
4. `uv run fedcourts query --court scotus --citation "605 U.S. 73" --decided-before 2026-07-28 --limit 5`
   - Transfer line: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).
5. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026-07-28 --limit 10`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned 10 resolved SCOTUS GVR priors from the 2020s decided before 2026-07-28.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="605 U.S. 73", fields=["caseName", "dateFiled", "citation", "cluster_id"], num_results=5)`
   - Failed with HTTP 429: `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 1290 seconds.'}`
2. `mcp_courtlistener_search(type="o", court="ca5", case_name="Delgado", filed_before="2026-07-28", fields=["caseName", "dateFiled", "citation", "docketNumber"], num_results=5)`
   - Failed with HTTP 429: `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 1290 seconds.'}`

*(Per prompt instructions, degraded gracefully upon MCP HTTP 429 rate-limit error and relied on the provisioned case record, Appendix A containing the full Fifth Circuit opinion, and local corpus/statpack base rates. No web searches were performed.)*
