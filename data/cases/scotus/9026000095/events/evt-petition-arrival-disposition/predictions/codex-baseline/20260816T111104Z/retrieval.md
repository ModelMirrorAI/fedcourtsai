# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json` for the sal-v3 prior-Term paid arrival anchor, originating-court cut, and terminal relist/CVSG context.
- CourtListener MCP opinion search: `court=scotus`, query `"judicial disqualification" "due process" "summary denial"`, five-result limit. The server returned HTTP 429 (`Rate limit exceeded`) and supplied no results.
- Corpus lookup: `uv run fedcourts query --court scotus --citation '556 U.S. 868' --limit 1 --full`. It returned no rows and emitted no `ranged corpus reads` line.
- No web searches were used.
