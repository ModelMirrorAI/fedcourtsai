# Retrieval log — claude-judge, run 20261005T221055Z

No retrieval beyond the provisioned inputs and committed artifacts:

- Read the committed `metrics/statpack.md` (segment base rate by salience
  band, sal-v4; relist-count table) and `metrics/statpack.json` (baseline-band
  `prefix_weighted_resolved` / `prefix_est_grant_rate` rows for OT2017–OT2024)
  to pool the cert baseline.
- Read `src/fedcourtsai/pipeline/evaluate.py` to match the in-code
  `is_correct`, `brier_score` and `brier_skill` definitions.
- Read the provisioned record (`record/context.json`, the 2026-10-05 snapshot,
  `record/documents/petition.txt` and `questions-presented.txt`) and the three
  blinded candidates under `record/blinded/`.

No `fedcourts query` or `open-events` call (no `ranged corpus reads` line to
record), no CourtListener MCP lookup, no web search.
