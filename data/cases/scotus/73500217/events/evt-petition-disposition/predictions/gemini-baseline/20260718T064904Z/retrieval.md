- `cat metrics/statpack.md | grep -A 20 "Modern discretionary-cert petitions"`: consulted general baseline grant rates.
- `uv run fedcourts query --court scotus --topic "private right of action"`: attempted, but the local corpus sidecar service was unreachable.
- `mcp_courtlistener_search(q="Providence Health & Services" AND "Crites-Bachert", type="d")`: attempted, but the CourtListener MCP tool reported an HTTP 429 rate limit error.

Proceeded with prediction based on provisioned inputs (snapshot, event, and questions presented).