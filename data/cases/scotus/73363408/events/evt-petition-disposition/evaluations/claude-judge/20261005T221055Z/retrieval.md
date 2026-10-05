# Retrieval record — claude-judge, scotus/73363408 evt-petition-disposition, run 20261005T221055Z

No retrieval beyond the provisioned inputs.

What I read, all from the working tree: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; the event's `event.yaml` and `outcome.json`; `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, and selected passages of `record/documents/petition.txt` (the jurisdiction statement, the reasons-for-granting section, and the string cites, to check the candidates' characterizations); the three blinded candidate directories under `record/blinded/` (`prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`); the committed `metrics/statpack.md` sal-v4 band table; `config/tracking.yaml`'s lookback setting; and the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py`. No `record/opinion/` slot was staged.

- `fedcourts query` / `open-events`: none. No `ranged corpus reads` line to report.
- CourtListener MCP: none.
- Web search: none.
