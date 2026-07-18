# Retrieval Log

- `uv run fedcourts query --court "scotus" --disposition "denied" --limit 5`
  stderr output: `ranged corpus reads: 209 GET(s), 54788096 byte(s)`
- Read committed statpack metrics (`metrics/statpack.md`) to evaluate base rates for discretionary cert petitions (overall and by state court origin).
- `mcp_courtlistener_search` via CourtListener MCP to look for opinions discussing `"retention of property" "without due process" "fifth amendment" "fourth amendment"` to evaluate the legitimacy of the alleged circuit split.
