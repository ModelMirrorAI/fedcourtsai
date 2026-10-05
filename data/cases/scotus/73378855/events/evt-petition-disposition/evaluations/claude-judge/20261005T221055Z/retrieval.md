# Retrieval log (evaluator)

No retrieval beyond the provisioned inputs.

Read, all local to the checkout: `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, the three provisioned documents under `record/documents/`, every file under `record/blinded/candidate-{a,b,c}/`, the committed `metrics/statpack.md` (sal-v4 band table) and `metrics/statpack.json` (exact per-Term `prefix_weighted_resolved` / `prefix_est_grant_rate` for the `baseline` band, Terms 2017-2024), and `src/fedcourtsai/pipeline/evaluate.py` / `base_rates.py` to match the in-code pooling. No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to report), no CourtListener MCP call, no web search.
