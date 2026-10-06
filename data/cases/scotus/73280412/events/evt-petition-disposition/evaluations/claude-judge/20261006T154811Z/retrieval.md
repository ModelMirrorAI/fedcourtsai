# Retrieval log — claude-judge, scotus/73280412, evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs.

Read, in order: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; then the event's `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`; the three blinded candidates under `record/blinded/` (`prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json` each); `metrics/statpack.md` (the sal-v4 salience-band table) and the `high`-band `prefix_est_grant_rate` / `prefix_weighted_resolved` fields of `metrics/statpack.json` for OT2017–OT2024 as a cross-check; `config/tracking.yaml` (`base_rate_lookback_terms`) and the scoring functions in `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py` to match definitions.

- `fedcourts query` / `open-events`: not used (no `ranged corpus reads` line to report).
- CourtListener MCP: not used.
- Web search / fetch: none.
- `record/opinion/`: absent, as expected on a cert cell.
- `data/qp-topics/`: not read.
