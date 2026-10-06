# Retrieval log — claude-judge, scotus/73452191, evt-petition-disposition, run 20261005T221055Z

No retrieval beyond the provisioned inputs.

Read only: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's `event.yaml` and `outcome.json`, the case-level `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/`, the three blinded candidates under `record/blinded/` (`prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`), the committed `metrics/statpack.md` (the sal-v4 salience-band table and the relist and CVSG cuts), `config/tracking.yaml` (the lookback value), and `src/fedcourtsai/pipeline/evaluate.py` (to match the scoring definitions).

- No `fedcourts query` or `open-events` calls, so no `ranged corpus reads` lines.
- No CourtListener MCP calls.
- No web searches.
- Nothing under `data/qp-topics/` was read.
