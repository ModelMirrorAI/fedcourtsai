# Retrieval log — claude-judge, run 20261005T221055Z

No retrieval beyond the provisioned inputs and the committed repository.

- Read `record/blinded/<alias>/` for gemini-baseline, claude-baseline, codex-baseline (prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md, retrieval_log.json); `outcome.json`, `event.yaml`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/` (petition and questions presented; fetched 2026-10-03, after the predictions ran).
- Read `metrics/statpack.md` "Segment base rate by salience band (sal-v4)" and the matching `metrics/statpack.json` rows to pool the baseline band's bracketed `reached` rate over OT2017–OT2024 (resolved-weighted, n = 11580): 0.051209.
- Read `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py` to match the in-code definitions of `brier_skill` and `prediction_base_rate`.
- No `fedcourts query` / `open-events` call, so no `ranged corpus reads` line. No CourtListener MCP lookup. No web search.
