# Retrieval log — claude-judge, scotus/73500217, evt-petition-disposition, run 20261005T221055Z

No retrieval beyond the provisioned inputs.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's `event.yaml` and `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt`, every file under `record/blinded/candidate-{a,b,c}/`, `metrics/statpack.md` (relist, CVSG and "Segment base rate by salience band (sal-v4)" sections), `metrics/statpack.json` (the same band rows, to confirm the pooled figure), `config/tracking.yaml` (`base_rate_lookback_terms`), and `src/fedcourtsai/pipeline/evaluate.py` (to match the in-code score definitions).

No `fedcourts query` or `open-events` call was made, so no `ranged corpus reads` line was produced. No CourtListener MCP lookup. No web search. `record/opinion/` is absent, as expected on a cert cell.
