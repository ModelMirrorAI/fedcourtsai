# Retrieval log — claude-judge, scotus/73281388, evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`,
`schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's
`event.yaml` and `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`,
`record/documents/documents.json` and `questions-presented.txt`, every file under
`record/blinded/<alias>/` for claude-baseline, gemini-baseline and codex-baseline, the
"Segment base rate by salience band (sal-v4)" table in `metrics/statpack.md` (with the
unrounded per-Term `elevated` rows in `metrics/statpack.json` to confirm the pooled
figure), and the scoring definitions in `src/fedcourtsai/pipeline/evaluate.py` and the
lookback in `config/tracking.yaml`.

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to record),
no CourtListener MCP call, no web search. `record/opinion/` is absent on this cert
cell, as expected.
