# Retrieval log — claude-judge, scotus/73500287, evt-petition-disposition, run 20261007T150255Z

No retrieval beyond the provisioned inputs.

Consulted only: `AGENTS.md`, `.github/prompts/evaluate.md`, the evaluation,
agent-flags and agent-tooling schemas, the event's `event.yaml` and
`outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`,
`record/documents/*`, the three `record/blinded/<alias>/` directories
(prediction, reasoning, forecast document, retrieval note, retrieval log),
`summaries/2026-10-05.md`, the committed `metrics/statpack.md` sal-v4 band
table and `metrics/statpack.json` (to cross-check the pooled baseline rate),
`config/tracking.yaml` (lookback), and `src/fedcourtsai/pipeline/evaluate.py`
(scoring definitions). No `fedcourts query` or `open-events` call, no
CourtListener MCP call, no web search. `record/opinion/` is absent, as
expected on a cert cell.
