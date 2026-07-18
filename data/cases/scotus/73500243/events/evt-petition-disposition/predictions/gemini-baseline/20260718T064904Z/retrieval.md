- `fedcourts query --court scotus --era roberts --disposition denied --limit 1`
  `ranged corpus reads: 209 GET(s), 54788096 byte(s)`
- Searched CourtListener MCP `search` tool for `11th Cir. 23-10811` to identify the lower court opinion (`Clemente Javier Aguirre-Jarquin v. Robert Hemmert`).
- Attempted to read the full lower court opinion using the MCP `get_endpoint_item` tool, but the request was throttled by the CourtListener API (`HTTP 429 Rate limit exceeded: 1200/day`). Proceeded with base rates and provisioned inputs.
- Consulted `metrics/statpack.md` for historical base rates regarding cert petitions with zero relists and paid filing status.
