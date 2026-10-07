# Retrieval log (evaluator)

No retrieval beyond the provisioned inputs.

I read the provisioned inputs only: `event.yaml`, `outcome.json`, the case-level `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/` (the questions-presented text and the opening pages of the petition, for context on the posture), and each blinded candidate's `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, and `retrieval_log.json` under `record/blinded/`. No `record/opinion/` slot was staged, as expected on a cert cell. The base rate was read from the committed `metrics/statpack.md` ("Segment base rate by salience band (sal-v4)", Terms 2017 through 2024, bracketed `reached` figures). No `fedcourts query` / `open-events` calls, no CourtListener MCP calls, and no web searches.
