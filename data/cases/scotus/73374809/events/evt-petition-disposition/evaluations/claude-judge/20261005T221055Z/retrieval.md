# Retrieval record (evaluator)

No retrieval beyond the provisioned inputs.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`,
`schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`; the event's
`event.yaml` and `outcome.json`; `record/context.json`, `record/snapshots/2026-10-05.json`,
`record/documents/*`; every file under `record/blinded/candidate-{a,b,c}/`; and the
committed `metrics/statpack.md` (the sal-v4 salience-band table, lines 187–203, and the
paid-segment relist and CVSG cuts, lines 100–117).

- No `fedcourts query` / `open-events` lookup (no `ranged corpus reads` line to record).
- No CourtListener MCP lookup.
- No web search.
- Nothing under `data/qp-topics/` was read.
