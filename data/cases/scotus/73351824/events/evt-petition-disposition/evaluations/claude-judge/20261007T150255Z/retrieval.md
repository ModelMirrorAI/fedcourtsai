# Retrieval log — claude-judge, run 20261007T150255Z, scotus/73351824 evt-petition-disposition

No retrieval beyond the provisioned inputs and the committed repository.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; the event's `event.yaml` and `outcome.json`; `record/context.json`, `record/snapshots/2026-10-06.json`, `record/documents/documents.json` and `questions-presented.txt`; the three blinded candidates' `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md` and `retrieval_log.json`; `metrics/statpack.md` (the sal-v4 salience-band table) and `metrics/statpack.json` (to pool the baseline band's bracketed `reached` figures over OT2017–OT2024); and the pooling and skill definitions in `src/fedcourtsai/pipeline/base_rates.py` and `src/fedcourtsai/pipeline/evaluate.py`.

No `fedcourts query` or `open-events` run (no `ranged corpus reads` line to record). No CourtListener MCP lookup. No web search. `record/opinion/` is absent, as expected on a cert cell.
