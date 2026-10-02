# Retrieval — claude-judge — scotus/73281619 evt-petition-disposition — run 20261002T200745Z

No retrieval beyond the provisioned inputs and the committed repository files.

Consulted, all local to the checkout:

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- The event's `event.yaml` and `outcome.json`; `record/context.json`; `record/snapshots/2026-10-01.json` (docket entries, to confirm the grant entry and the distribution history); `record/documents/documents.json` and `questions-presented.txt`.
- `record/blinded/<alias>/` for gemini-baseline, codex-baseline, claude-baseline: `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`.
- `metrics/statpack.md` (the sal-v4 *Segment base rate by salience band* table) and `metrics/statpack.json` (the `prefix_est_grant_rate` / `prefix_weighted_resolved` entries for the `elevated` segment, Terms 2017–2024, pooling to 484 / 2,810).
- `src/fedcourtsai/pipeline/evaluate.py` and `src/fedcourtsai/pipeline/base_rates.py`, to match the in-code definitions of `correct`, `brier_score`, `brier_skill` and the risk-set pooling.
- `record/opinion/` was checked and is absent, as expected on a cert cell.

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to report), no CourtListener MCP call, no web search. Nothing under `data/qp-topics/` was read.
