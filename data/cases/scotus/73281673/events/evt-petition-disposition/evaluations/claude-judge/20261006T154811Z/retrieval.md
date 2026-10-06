# Retrieval record — claude-judge, scotus/73281673, evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs.

Read, in the contract's order: `AGENTS.md`, `.github/prompts/evaluate.md`,
`schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`,
`schemas/agent_tooling.schema.json`; then the event's `event.yaml` and
`outcome.json`, the case-level `record/context.json`,
`record/snapshots/2026-10-05.json`, `record/documents/documents.json` and
`questions-presented.txt`, and each blinded candidate's `prediction.json`,
`reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, and
`retrieval_log.json` under `record/blinded/`. No `record/opinion/` slot was
staged (cert cell; expected). Base rates were read from the committed
`metrics/statpack.md` (the `sal-v4` per-Term band table and the relist-count
table); the scoring definitions were checked against
`src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py`.

No `fedcourts query` or `open-events` call, no CourtListener MCP call, and
no web search was made. Nothing under `data/qp-topics/` was read, and the
committed `predictions/` and `evaluations/` trees were not touched.
