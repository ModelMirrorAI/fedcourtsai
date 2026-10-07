# Retrieval record — claude-judge, scotus/73335108, evt-petition-disposition, run 20261006T192524Z

No retrieval beyond the provisioned inputs.

Read, in order: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; then the event's `event.yaml` and `outcome.json`, the case-level `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt`, and for each of `codex-baseline`, `claude-baseline`, `gemini-baseline` under `record/blinded/`: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. No `record/opinion/` slot was staged (cert cell; expected). Base rate taken from the committed `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)" table, bracketed `reached` figures for `baseline`, Terms 2017–2024. Scoring definitions checked against `src/fedcourtsai/pipeline/evaluate.py` and the lookback against `config/tracking.yaml`.

- `fedcourts query` / `open-events`: not used; no `ranged corpus reads` line to record.
- CourtListener MCP: not used.
- Web search: none.
