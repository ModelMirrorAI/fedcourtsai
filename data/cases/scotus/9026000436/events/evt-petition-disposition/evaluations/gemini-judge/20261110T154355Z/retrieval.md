# Retrieval log

## Local tools and statpack history

- `uv run fedcourts statpack-at data/cases/scotus/9026000436/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` (and identical runs for `claude-baseline` and `codex-baseline` at run id `20261009T143059Z`) — reconstructed the `sal-v4` statpack builds in force at prediction time (`0918fb18e74fb89adc9a0882411996400986925e` and alternative `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`) to verify the candidates' base-rate anchors.
- Read the committed `metrics/statpack.md` (`sal-v8`) and the provisioned inputs under `data/cases/scotus/9026000436/`.
- No `fedcourts query` or `open-events` calls, no CourtListener MCP lookups, and no web searches were performed.
