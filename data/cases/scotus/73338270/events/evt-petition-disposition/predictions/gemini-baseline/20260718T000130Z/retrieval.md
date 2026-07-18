# Retrieval Log

**Corpus Lookups:**
- `uv run fedcourts query --court scotus --topic "Due Process" --era 2020s`
  - `ranged corpus reads: 466 GET(s), 122028032 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s | grep "vaccine"`
  - `ranged corpus reads: 430 GET(s), 112590848 byte(s)`

**CourtListener MCP Lookups:**
- `mcp_courtlistener_search(court=["ca9"], q="\"Boysen\" \"PeaceHealth\"", type="o")` (Throttled/Error initially)
- `mcp_courtlistener_search(q="\"Boysen\" \"PeaceHealth\"", type="o")` (No results)
- `mcp_courtlistener_search(court=["ca9"], q="\"Boysen\" \"PeaceHealth\"", type="d")` (Found docket 24-5204)
- `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket":69773998,...})` (Validation error)
- `mcp_courtlistener_search(docket_number="24-5204", q="\"Boysen\"", type="rd")` (Retrieved 9th Cir. docket entries confirming timeline)
- `mcp_courtlistener_search(docket_number="24-5204", q="\"Boysen\"", type="rd", order_by="entry_date_filed desc")` (Further docket inspection)

**Base Rates:**
- Consulted `metrics/statpack.md` for discretionary-cert petition base rates (paid vs IFP), grant rate (~2.5-3%), and impact of no relists.
