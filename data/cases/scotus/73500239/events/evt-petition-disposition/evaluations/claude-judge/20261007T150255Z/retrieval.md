# Retrieval log — claude-judge, run 20261007T150255Z, scotus/73500239 evt-petition-disposition

No retrieval beyond the provisioned inputs and the committed repository.

Consulted, all local and read-only:

- `AGENTS.md`, `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.
- `data/cases/scotus/73500239/events/evt-petition-disposition/event.yaml` and `outcome.json`.
- `data/cases/scotus/73500239/record/context.json`, `record/snapshots/2026-10-05.json` (the decided docket: waiver June 25, distribution July 1 for the September 28 conference, denied October 5, 2026), `record/documents/questions-presented.txt`, and `record/documents/petition.txt` (grepped to verify the candidates' quotations: MacRae, Johnson v. Multnomah, "not quite", "unpublished opinions", "affirms or reverses", the causation holding, and the court of appeals not explicitly addressing the Garcetti ground).
- `record/blinded/candidate-{a,b,c}/` — `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`. `record/opinion/` is absent, as expected on a cert cell.
- `metrics/statpack.md`, the "Segment base rate by salience band (sal-v4)" table, rows OT2017–OT2024, bracketed `reached` baseline column, pooled resolved-weighted to ≈ 5.12% over n = 11,580.
- `src/fedcourtsai/pipeline/evaluate.py` — `is_correct`, `brier_score`, `brier_skill_score` definitions, to match the in-code formulas.

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to record). No CourtListener MCP call. No web search. Nothing read under `data/qp-topics/`.
