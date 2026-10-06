# Retrieval log — claude-judge, scotus/73281412, evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs.

Read only from the checkout: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's `event.yaml` and `outcome.json`, the case-level `record/context.json`, the decided-docket snapshot `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt` and `documents.json`, each `record/blinded/<alias>/` directory (`prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`), the committed `metrics/statpack.md` sal-v4 band table and relist-count cut with the matching rows of `metrics/statpack.json`, and the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py`.

- `fedcourts query` / `open-events`: not run (no `ranged corpus reads` line).
- CourtListener MCP: not used.
- Web search: none.
- `record/opinion/`: absent, as expected on a cert cell.
