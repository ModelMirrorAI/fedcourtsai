# Retrieval

- Consulted `metrics/statpack.md`. It reports a 1.4% grant share (4 of 296 resolved SCOTUS records), but it does not contain the “Modern discretionary-cert petitions by disposition” section described in the prediction prompt. I treated the reported rate only as broad confirmation that grants are rare, not as a modern paid-petition denominator.
- Attempted `uv run fedcourts query --court scotus --limit 12 --corpus-backend ranged`. The command failed before returning priors because the corpus remote hostname could not be resolved. It printed no `ranged corpus reads: …` line because no ranged read completed.
- Attempted a CourtListener opinions search for `"settled expectations" AND ("inter partes review" OR PTAB)` in the Federal Circuit and Supreme Court, limited through July 10, 2026. The MCP server returned `REDIS_URL is not set; cannot access session store.` and supplied no results.
- No web searches were used.
