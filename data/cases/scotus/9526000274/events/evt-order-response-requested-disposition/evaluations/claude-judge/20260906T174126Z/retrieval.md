# Retrieval — claude-judge, 20260906T174126Z

No corpus lookups (`fedcourts query` / `open-events`) and no CourtListener
MCP lookups; no web searches. Everything consulted was in the checkout:

- The cell's `event.yaml`, `outcome.json`, `record/context.json`, the decided
  snapshot `record/snapshots/2026-09-05.json`, and
  `record/documents/documents.json` plus the head of
  `record/documents/application.txt` (the applicants' emergency stay
  application, fetched 2026-09-03 — after every candidate ran), read to check
  the candidates' characterisations of the application's argument structure.
- `record/blinded/candidate-{a,b,c}/` — `prediction.json`, `reasoning.md`,
  `predicted_reasoning.md`, `retrieval.md`, `retrieval_log.json`.
- `metrics/statpack.md`, the interim-docket section (Term rows 2025 and 2024),
  to check each candidate's 31/296 ≈ 10.5% pooled baseline against the
  committed pack.
- `docs/outcome-decomposition.md` (the `interim-v1` declaration) and
  `src/fedcourtsai/pipeline/interim_signals.py` (the amicus counter's
  filed-vs-submitted rule), to confirm the outcome's `amicus_briefs: 1`
  against a docket showing one "filed" and one "submitted" amicus entry is
  the parser's deliberate behaviour rather than a data defect.
- `schemas/evaluation.schema.json`, `schemas/agent_flags.schema.json`,
  `schemas/agent_tooling.schema.json`.
