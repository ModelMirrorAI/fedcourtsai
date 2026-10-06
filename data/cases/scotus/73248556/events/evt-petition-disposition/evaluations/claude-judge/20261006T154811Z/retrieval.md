# Retrieval log — claude-judge, scotus/73248556 evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs and the committed repository files:

- `data/cases/scotus/73248556/record/blinded/<alias>/` for gemini-baseline, claude-baseline, codex-baseline (prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md, retrieval_log.json).
- `data/cases/scotus/73248556/record/` context.json, the 2026-10-05 snapshot, questions-presented.txt and brief-in-opposition.txt (case facts and posture only). No `record/opinion/` slot exists, as expected on a cert cell.
- `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)", federal column, OT2017–OT2024 bracketed `reached` figures, for the risk-set baseline.
- `src/fedcourtsai/pipeline/evaluate.py` for the in-code `is_correct`, `brier_score` and `brier_skill` definitions, and `config/tracking.yaml` for `base_rate_lookback_terms`.

No `fedcourts query` or `open-events` call, no CourtListener MCP call, no web search, and nothing under `data/qp-topics/`.
