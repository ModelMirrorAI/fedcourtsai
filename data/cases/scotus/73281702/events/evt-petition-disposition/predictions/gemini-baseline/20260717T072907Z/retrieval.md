No retrieval beyond the provisioned inputs and the CourtListener MCP server.

MCP tool calls made:
- `mcp_courtlistener_search` with query `"21.02" unanimous` (0 results)
- `mcp_courtlistener_search` with query `"continuous sexual abuse" unanimous` (0 results in dockets, 4 results in opinions, revealing no obvious split-inducing SCOTUS precedent)

Corpus tool calls made:
- Base rates retrieved via `cat metrics/statpack.md | grep -A 20 "Modern discretionary-cert petitions"`, identifying the base rate for paid state-court cert petitions.
