# Retrieval log — claude-judge, scotus/73372500, evt-petition-disposition, run 20261005T221055Z

No retrieval beyond the provisioned inputs and the committed repository files.

Read: `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, the event's `event.yaml` and `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/documents.json` and `questions-presented.txt`, every file under `record/blinded/candidate-{a,b,c}/`, the `sal-v4` salience-band table in `metrics/statpack.md` with the matching per-Term baseline segments in `metrics/statpack.json`, `config/tracking.yaml` (the lookback setting), and the `segment_base_rate` / `_pooled_band_rate` definitions in `src/fedcourtsai/pipeline/` to match the in-code pooling.

- `fedcourts query` / `open-events`: not used; no `ranged corpus reads` line produced.
- CourtListener MCP: not used.
- Web search / fetch: none.
- `data/qp-topics/`: not read.
- `uv run fedcourts paths --court scotus --docket 73372500 --event evt-petition-disposition --role evaluator`: operational, to confirm the cell's event and outcome paths.
