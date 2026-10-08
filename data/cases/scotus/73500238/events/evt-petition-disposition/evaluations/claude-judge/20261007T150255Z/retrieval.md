# Retrieval log — evaluator cell

No `fedcourts query` / `open-events` calls, no CourtListener MCP lookups, and no web searches were made; nothing beyond the provisioned inputs and committed repository files was consulted.

Committed files read for the baseline and the scoring definitions (not retrieval, listed for completeness):

- `metrics/statpack.md`, section "Segment base rate by salience band (sal-v4)" — caption "Most recent 10 of 10 Term(s)"; the `baseline` column's bracketed `reached` figures for Terms 2017–2024.
- `metrics/statpack.json` — the same Terms' unrounded `prefix_est_grant_rate` and `prefix_weighted_resolved` for the `baseline` band, pooled resolved-weighted: 593 / 11,580 = 0.051209.
- `src/fedcourtsai/pipeline/evaluate.py` and `src/fedcourtsai/pipeline/base_rates.py` — the in-code pooling definition, to match it; `config/tracking.yaml` for the 10-Term lookback.
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
