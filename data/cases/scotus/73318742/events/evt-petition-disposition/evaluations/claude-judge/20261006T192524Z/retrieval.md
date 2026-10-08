# Retrieval log — claude-judge, run 20261006T192524Z, scotus/73318742 evt-petition-disposition

No retrieval beyond the provisioned inputs and the committed repository files.

- Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`,
  `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- Read the cell: `event.yaml`, `outcome.json`, `record/context.json`,
  `record/snapshots/2026-10-05.json`, `record/documents/documents.json`,
  `record/documents/questions-presented.txt`, the opening of
  `record/documents/petition.txt`, and a grep plus the opening of
  `record/documents/brief-in-opposition.txt` (to check the candidates' readings
  of the alternative grounds and preservation points). `record/opinion/` is
  absent, as expected on a cert cell.
- Read every staged candidate under `record/blinded/` (`prediction.json`,
  `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`).
- Read `metrics/statpack.md`, the "Segment base rate by salience band (sal-v4)"
  table, and pooled OT2017–OT2024 bracketed `reached` baseline figures locally.
- No `fedcourts query` / `open-events` call (no `ranged corpus reads` line to
  record), no CourtListener MCP call, no web search.
