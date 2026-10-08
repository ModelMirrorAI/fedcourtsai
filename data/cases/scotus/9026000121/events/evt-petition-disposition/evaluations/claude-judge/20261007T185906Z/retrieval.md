# Retrieval log — claude-judge, run 20261007T185906Z

No retrieval beyond the provisioned inputs and the committed repository.

- Corpus (`fedcourts query` / `open-events`): none run, so no `ranged corpus reads` line.
- CourtListener MCP: no calls.
- Web search: none.
- Read, in the working tree only: `AGENTS.md`, `.github/prompts/evaluate.md`,
  `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`,
  `schemas/agent_tooling.schema.json`; the cell's `event.yaml`, `outcome.json`,
  `record/context.json`, `record/snapshots/2026-10-05.json`,
  `record/documents/documents.json`, `questions-presented.txt`, and grep slices of
  `petition.txt` (to verify the candidates' procedural-history claims); every
  file under `record/blinded/candidate-{a,b,c}/`; `metrics/statpack.md`
  (the sal-v4 "Segment base rate by salience band" table and the
  originating-court section heading); and the in-code scoring helpers in
  `src/fedcourtsai/pipeline/evaluate.py` and `base_rates.py` to confirm the
  pooling rule. `record/opinion/` is absent (ordinary on a cert cell).
- Nothing under `data/qp-topics/`, the committed `predictions/` tree, or any
  alias map was read.
