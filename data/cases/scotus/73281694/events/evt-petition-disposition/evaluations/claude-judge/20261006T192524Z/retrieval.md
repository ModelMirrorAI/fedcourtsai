# Retrieval log — claude-judge, scotus/73281694, evt-petition-disposition, run 20261006T192524Z

No retrieval beyond the provisioned inputs and the committed repository files.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`,
`schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; the event's
`event.yaml` and `outcome.json`; `record/context.json`, `record/snapshots/2026-10-05.json`;
every file under `record/blinded/candidate-{a,b,c}/` (`prediction.json`, `reasoning.md`,
`predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`); the sal-v4 "Segment base
rate by salience band" table in `metrics/statpack.md`; and the scoring definitions in
`src/fedcourtsai/pipeline/evaluate.py`. `record/opinion/` is absent, as expected on a cert cell.

No `fedcourts query` / `open-events` calls (no `ranged corpus reads` lines to record), no
CourtListener MCP calls, no web searches or fetches. Nothing under `data/qp-topics/` was read.
