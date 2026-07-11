# Retrieval

- Consulted `metrics/statpack.md`, especially the corpus-wide and First Circuit disposition base rates.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court ca1 --limit 10`. The ranged corpus endpoint could not be resolved, so the command failed before returning priors or printing a `ranged corpus reads: ...` line.
- Attempted a CourtListener opinions search for `PROMESA automatic stay appeal`, limited to the First Circuit and filings before November 1, 2019. The MCP server returned `REDIS_URL is not set; cannot access session store.` No results were returned.
- No web searches were used.

No retrieval sought or exposed this case's disposition or subsequent history.
