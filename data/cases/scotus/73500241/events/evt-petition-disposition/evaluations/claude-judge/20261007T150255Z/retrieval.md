# Retrieval log — scotus/73500241, evt-petition-disposition, claude-judge, run 20261007T150255Z

No retrieval beyond the provisioned inputs.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`,
`schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's
`event.yaml` and `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`,
`record/documents/` (manifest and questions presented), every file under
`record/blinded/<alias>/` for claude-baseline, gemini-baseline and codex-baseline, and the
committed `metrics/statpack.md` (the sal-v4 segment base rate table). No
`record/opinion/` slot is staged, which is the ordinary cert shape.

Local offline computation only: `fedcourtsai.pipeline.base_rates.prediction_base_rate`
run against the candidates' frozen context and the committed `metrics/statpack.json`
to confirm the hand-pooled baseline (0.051209 in code against 0.051203 from the rendered
table's rounded percentages). No `fedcourts query` or `open-events` call, so no
`ranged corpus reads` line to report. No CourtListener MCP call. No web search.
