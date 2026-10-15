# Retrieval

- Read the committed `metrics/statpack.md`, section "The interim docket (applications)", for the base rate.
- CourtListener MCP `search` (type=d, q="City of Brunswick" Honeywell): this returned the S.D. Ga.
  and CA11 dockets only. There was no SCOTUS docket for No. 26-289 and no disposition information.
- `uv run fedcourts query --court scotus "<free text>"`: this was rejected at argument parsing
  (positional text is not accepted), so it made no corpus read and printed no `ranged corpus reads`
  line.
