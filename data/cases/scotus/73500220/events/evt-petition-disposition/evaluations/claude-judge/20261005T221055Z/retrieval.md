# Retrieval log — claude-judge — scotus/73500220, evt-petition-disposition, run 20261005T221055Z

## Corpus (`fedcourts query` / `open-events`)

None. No corpus lookup was made; no `ranged corpus reads` line to record.

## CourtListener MCP

None.

## Web searches

None.

## Local sources beyond the provisioned cell inputs

- `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)": the
  per-Term baseline column, bracketed `reached` figures and their `n`, Terms
  2017–2024, for the pooled risk-set base rate.
- `metrics/statpack.json`: the unrounded `prefix_est_grant_rate` and
  `prefix_weighted_resolved` fields for the same band and Terms (593 / 11580 =
  0.05120898).
- `src/fedcourtsai/pipeline/evaluate.py`: the `is_correct`, `brier_score`, and
  `brier_skill` definitions, to match the in-code formulas.
- `schemas/evaluation.schema.json`, `schemas/agent_tooling.schema.json`,
  `schemas/agent_flags.schema.json`: the output contracts.
- `data/cases/scotus/73500220/record/documents/petition.txt`: the appendix
  passages (App. 3 alternative retroactivity holding; the district court's
  denial of an evidentiary hearing) used to check codex-baseline's vehicle
  analysis against the record. Read as evidence of what the appellate opinion
  says, not for new case facts.
- `data/cases/scotus/73500220/summaries/2026-09-28.md`: the plain-language
  case summary, for orientation only.

Nothing under `data/qp-topics/` was read.
