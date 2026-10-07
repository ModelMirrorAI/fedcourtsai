# Retrieval log — claude-judge, run 20261006T192524Z

No corpus lookups (`fedcourts query` / `open-events`), no CourtListener MCP
calls, and no web searches.

Consulted beyond the per-case provisioned inputs, all from the checkout:

- `metrics/statpack.md` — "Segment base rate by salience band (sal-v4)"
  (bracketed `reached` figures, Terms 2017–2024 pooled for the elevated band),
  plus the relist-count and CVSG cuts the candidates cited.
- `config/tracking.yaml` (`salience.base_rate_lookback_terms`) and
  `src/fedcourtsai/pipeline/{evaluate,base_rates}.py`, to match the in-code
  pooling and skill definitions.
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`,
  `schemas/agent_tooling.schema.json`.

Per-case inputs read: `event.yaml`, `outcome.json`, `record/context.json`,
`record/snapshots/2026-10-05.json`, `record/documents/questions-presented.txt`
and `documents.json`, and every file under `record/blinded/candidate-{a,b,c}/`.
`record/opinion/` is absent, as expected on a cert cell.
