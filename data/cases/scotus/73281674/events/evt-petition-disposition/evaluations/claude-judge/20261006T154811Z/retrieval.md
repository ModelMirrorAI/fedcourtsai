# Retrieval record — claude-judge, run 20261006T154811Z

No retrieval beyond the provisioned inputs and the committed checkout:

- Read the event's `event.yaml` and `outcome.json`, the case-level `record/context.json`, the October 5 snapshot, `documents.json`, `questions-presented.txt`, and slices of the provisioned `petition.txt` and `brief-in-opposition.txt` for my own stakes read; no `record/opinion/` slot exists on this cert cell.
- Read every staged candidate directory under `record/blinded/` (`codex-baseline`, `claude-baseline`, `gemini-baseline`): `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, and `retrieval_log.json`. Nothing under `events/…/predictions/` was read, and nothing under `data/qp-topics/`.
- Read `metrics/statpack.md` ("Segment base rate by salience band (sal-v4)") and pooled the `baseline` band's unrounded `prefix_est_grant_rate` × `prefix_weighted_resolved` over Terms 2017–2024 from `metrics/statpack.json` (593 / 11580).
- Read `src/fedcourtsai/pipeline/evaluate.py` and `pipeline/base_rates.py` to match the in-code `is_correct`, `brier_score`, `brier_skill`, and `_pooled_band_rate` definitions, and `schemas/*.json` for the output contract.
- No `fedcourts query` or `open-events` call (so no `ranged corpus reads` line to report), no CourtListener MCP lookup, and no web search or fetch.
