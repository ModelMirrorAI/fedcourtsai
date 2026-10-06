# Retrieval log — claude-judge, scotus/73281630, evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs and committed repository files. No
`fedcourts query` / `open-events` calls (so no `ranged corpus reads` lines), no
CourtListener MCP calls, no web searches.

Committed files consulted for context, beyond the cell's own event, outcome, record
and blinded staging area:

- `metrics/statpack.md` — "Segment base rate by salience band (sal-v4)" table, for
  the pooled elevated-band risk-set rate over OT2017–OT2024.
- `metrics/statpack.json` — the unrounded `prefix_est_grant_rate` /
  `prefix_weighted_resolved` fields behind the same rows (484 / 2,810 = 0.1722),
  cross-checked against the rendered table (0.1724 from the rounded percentages).
- `config/tracking.yaml` and `src/fedcourtsai/pipeline/{evaluate,base_rates}.py` —
  to confirm the lookback and the skill-score definition I was matching.
- `data/cases/scotus/73281630/summaries/2026-10-05.md` — the committed plain-language
  case summary, read only to confirm the disposition narrative; it is a
  pipeline-produced summary and nothing in the grades rests on it.
- `data/cases/scotus/73281630/record/snapshots/2026-10-05.json` — the decided
  docket's proceedings list, to confirm the 2026-10-05 denial and the absence of a
  noted dissent.

Nothing under `data/qp-topics/` was read.
