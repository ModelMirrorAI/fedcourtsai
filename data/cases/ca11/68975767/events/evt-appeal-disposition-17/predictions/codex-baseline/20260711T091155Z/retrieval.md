# Retrieval

- Consulted `metrics/statpack.md`, particularly the overall and Eleventh Circuit resolved-disposition tables. The Eleventh Circuit row contains only 45 resolved cases and reports: other 95.6%, denied 2.2%, granted 2.2%.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court ca11 --topic '3840 Trademark' --decided-before 2023 --limit 5 --corpus-backend ranged`. The pre-2023 cutoff ensured that the lookup could not surface this case. It failed on DNS resolution while connecting to the corpus remote, before returning priors. No `ranged corpus reads: ...` line was emitted.
- Attempted a CourtListener opinions search limited to Eleventh Circuit decisions filed before July 11, 2023 for `motion for reconsideration abuse of discretion clear error manifest injustice`. The MCP service reported that its session store was not configured and supplied no results.
- No web searches were used.
