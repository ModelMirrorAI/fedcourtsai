# Retrieval log — claude-judge, scotus/73129750, evt-petition-disposition, 20260814T033644Z

No retrieval beyond the provisioned inputs and committed repo files. No
`fedcourts query` / `open-events` corpus lookups (so no `ranged corpus reads`
lines), no CourtListener MCP calls, and no web searches.

Consulted, all local and committed:

- `data/cases/scotus/73129750/events/evt-petition-disposition/event.yaml` and
  `outcome.json` — the resolved ground truth.
- `data/cases/scotus/73129750/record/blinded/candidate-{a,b,c}/` —
  `prediction.json`, `reasoning.md`, `retrieval.md`, `retrieval_log.json` for
  each candidate (no `predicted_reasoning_doc` pointer set on any prediction,
  and none staged).
- `data/cases/scotus/73129750/record/context.json` — the cell's own context,
  for the terminal band and salience version only.
- `metrics/statpack.md` — the sal-v2 "Segment base rate by salience band"
  table, for the terminal federal-band base rate pooled over Terms 2017–2024.
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`,
  `schemas/agent_tooling.schema.json` — output contracts.
- `src/fedcourtsai/pipeline/evaluate.py` and `config/tracking.yaml` — to match
  the in-code pooling, skill, and lookback definitions.
