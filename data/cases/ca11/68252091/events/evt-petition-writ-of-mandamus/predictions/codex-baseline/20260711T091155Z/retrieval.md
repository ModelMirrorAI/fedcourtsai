# Retrieval

- Consulted `metrics/statpack.md`, especially the Eleventh Circuit row under “Cases by court.” It reports 95,619 cases, 45 resolved cases, and a resolved-case distribution of 95.6% other, 2.2% denied, and 2.2% granted. The sample is not mandamus-specific and was treated as a weak calibration check.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court ca11 --limit 20 --corpus-backend ranged`. The lookup failed because the runner could not resolve the configured corpus remote host. It returned no priors and printed no `ranged corpus reads: …` statistics line.
- Attempted a CourtListener MCP RECAP search for filings in N.D. Florida docket `4:22-cv-00439`, limited to filings before February 1, 2024. The service returned `REDIS_URL is not set; cannot access session store.` It returned no results.
- No web search was used.

No query targeted this mandamus proceeding's outcome or post-petition history.
