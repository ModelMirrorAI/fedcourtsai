# Retrieval Log

1. CourtListener MCP Lookup: `mcp_courtlistener_search` with query `"Christopher Zook" "Scott Fuqua"` to find the 10th Circuit opinion.
2. CourtListener MCP Lookup: `mcp_courtlistener_get_endpoint_item` to fetch the `html_with_citations` for opinion ID `11196917` (*Fuqua v. Santa Fe County Sheriff's Office*).
3. Read `metrics/statpack.md` to check base rates for modern discretionary-cert petitions and CVSG status. (No `fedcourts query` calls made).