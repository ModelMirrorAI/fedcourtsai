# Evaluation — claude-baseline — scotus/73372297 / evt-petition-disposition

## The cell

Cert stage (`event.yaml` `stage: cert`, moment `distribution`, opened 2026-05-20).
Outcome: `actual_disposition: denied`, `actual_granted: 0`, resolved 2026-10-05
on the order list after the September 28, 2026 Long Conference, with one
distribution, no CVSG, and no noted dissent. No `record/opinion/` slot is staged,
which is the ordinary state for a denied petition and takes no grade here: a
cert cell declares no semantic set, so no `semantic_grades` block is written.

## What the prediction got right

- `predicted_disposition: denied` against `actual_disposition: denied` →
  `correct = 1`.
- `probability = 0.004` → `brier_score = 0.004² = 0.000016`.
- The forecast's whole shape held: denial at the first conference, no relist,
  no response request, no CVSG, no separate writing. (The claims block and the
  forecast document are the harness's and stay unscored here; I note the match
  only as context on how the number was formed.)

## Segment base rate and skill

The prediction froze `band: baseline` under `salience_version: sal-v4`, and the
committed `metrics/statpack.md` table heading is *Segment base rate by salience
band (sal-v4)*, so the basis is `risk_set` and the figure is the bracketed
`reached` rate. The table renders 10 of 10 Terms (2017–2026); the case's Term is
2025, so the pool is every rendered Term strictly before it, 2017–2024, which is
also everything the pack holds inside the configured ten-Term lookback. Pooled
resolved-weighted from the exact per-Term fields in `metrics/statpack.json`
(`prefix_est_grant_rate × prefix_weighted_resolved`, summed, over summed
`prefix_weighted_resolved`):

| quantity | value |
| --- | --- |
| pooled weighted grants | 593.0 |
| pooled weighted resolved (n) | 11,580 |
| `segment_base_rate` | 0.051209 |
| `brier_skill_score` | 1 − 0.000016 / 0.051209² = 0.99390 |

The rendered percentages (4.5%–5.9%) pool to the same figure at display
precision. No version mismatch and no rendered-window divergence, so no flag on
the baseline.

## Reasoning quality: 0.88

What drove the score up:

- The anchor is the right one and is derived correctly: the sal-v4 `baseline`
  bracketed `reached` figures, pooled over 2017–2024 by `n`, to about 5.1%.
  The candidate names the alternative cuts (relist-0, no-CVSG, Federal Circuit
  origin) and uses them only as a direction check, not as stacked multipliers.
- The adjustment from ~5% to 0.4% is argued from facts the record actually
  carries, and I verified each against the decided snapshot: a paid, pro se
  petition; the SG's waiver (June 17); one distribution (June 24) for the
  September 28 conference; a nonprecedential Federal Circuit affirmance of
  December 9, 2025 (No. 2025-1769) resting on an untimely motion for review;
  questions presented that state no rule of law. "No legal question" is
  correctly identified as the dominant factor, and it is the right diagnosis
  of why this petition sits outside the grantable population whatever its band.
- It explains why the number is not lower still (summary action for reasons
  invisible in the petition), which is good calibration discipline rather than
  false certainty, and the realized denial is consistent with either reading.
- It separates what it did not do (CourtListener, web) from why, and records the
  one corpus query it ran and that the query did not inform the number.
- It read the full petition and summarized rather than reproduced the
  petitioner's personal details, noting the privacy point.

What held it back:

- The claim that pro se petitions "grant at a rate that rounds to zero" is
  asserted rather than tied to any committed cut; it is a well-known
  regularity, but the statpack publishes no pro se slice, and the reasoning
  does not say so.
- The CVSG analysis is slightly over-engineered for a cell where the federal
  government is already the respondent, though it reaches the right answer.
- The relist discussion leans on a Long Conference "administrative reschedule"
  hazard it admits it has no cut for; honest, but it is the one place the
  reasoning is impressionistic.

## Leakage

`mode: forward`. The log carries 23 calls, every one `captured` (coverage 1.0).
The only outward call is a corpus query for recent 2020s-era grants, limited to
five rows and filtered on structured fields; it does not name this case. No web
search and no CourtListener call. No `retrieved_doc_date` on any call. The
prediction was created 2026-09-16 on the 2026-09-16 snapshot, twelve days
before the conference and nineteen before the denial, and the reasoning treats
the disposition as future throughout. I checked for the mis-provisioned-forward
case and found none: nothing in the log or prose reads the outcome off the
input. `retrieved_outcome_material = false`, `influenced_prediction =
not_applicable`, `leakage_suspected = false`.

The decided snapshot I hold shows a supplemental brief from the petitioner
filed September 19, 2026, after the candidate's snapshot. That is the ordinary
forward shape (material later than the cell's own baseline), not something the
candidate was given or should have had.

## Stakes

My own read, formed from the record before weighing the candidate's score:
`evaluator_score = 0.02`. One claimant's Vaccine Act damages dispute, affirmed
below on timeliness in a nonprecedential order, with no legal question through
which the Court could reach the program-level debate the petition invokes.
