# Retrieval log — claude-judge, scotus/73281629 evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs.

Committed repository files read while scoring (not retrieval): `metrics/statpack.md` (the sal-v4 salience-band table) and `metrics/statpack.json`, `docs/salience.md` (band ladder and the `sal-v4` rule), `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py` (to match the in-code definitions), and the case record (`record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt`, `documents.json`). I ran `fedcourtsai.pipeline.base_rates.prediction_base_rate` locally on the committed statpack to confirm the pooled elevated risk-set rate (0.17224).

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to record), no CourtListener MCP call, no web search.
