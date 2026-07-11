# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Cases by court” and “SCOTUS petitions by Term.” The file reports a 1.4% granted share among 296 resolved SCOTUS records, but the resolved sample is sparse, dominated by non-merits labels, and has no resolved recent Terms. The “Modern discretionary-cert petitions by disposition” section described in the prediction prompt was not present, so the aggregate served only as broad calibration.

## CourtListener MCP

- Attempted an opinions search limited to SCOTUS, filed before July 11, 2026, for `"reserved powers doctrine" contract clause`. The service returned `REDIS_URL is not set; cannot access session store.` No results were available and no further MCP calls were made.

## Corpus query

- Attempted: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '518 U.S. 839' --limit 10 --corpus-backend ranged`
- The command failed because the corpus remote hostname could not be resolved. It printed no `ranged corpus reads: …` line because the connection failed before a ranged read completed, and it returned no priors.

No web searches were used.
