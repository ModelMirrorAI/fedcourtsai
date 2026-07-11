# Retrieval

- Consulted `metrics/statpack.md`, specifically the overall resolved-disposition summary and the Eleventh Circuit row. Its case-level labels are not specific enough to serve as a consolidation-motion base rate.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court ca11 --limit 10 --corpus-backend ranged`. The lookup failed because the runner could not resolve the corpus remote endpoint. It returned no priors and printed no `ranged corpus reads: ...` line.
- Attempted a CourtListener RECAP search in the Eleventh Circuit for the exact phrase `"motion to consolidate appeals"`, requesting ten compact results. The MCP server reported that its session-store configuration was unavailable and supplied no search results.

No web searches were used.
