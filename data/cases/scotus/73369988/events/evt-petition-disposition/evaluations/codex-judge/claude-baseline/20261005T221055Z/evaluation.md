# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition cell. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline's September 17 prediction names `denied` and assigns 0.006 to any grant. Therefore exact-label correctness is **1** and the Brier score is **0.000036**, calculated as `(0.006 - 0)^2`. The denial establishes the disposition, not the Court's reasons for declining review.

The prediction's own frozen context, not the evaluator's current context, supplies Term 2025, band `baseline`, and salience version `sal-v4`. These match the committed statpack's sal-v4 heading. I use the bracketed **reached** population and record `base_rate_basis = risk_set`.

| Prior Term | Reached rate | Weighted resolved denominator |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooling these displayed rates by their displayed denominators gives `592.925 / 11580 = 0.05120250431778929`. The numerator is a weighted reconstruction from rounded percentages, not an observed integer grant count. Terms 2025 and 2026 are excluded. The table renders 10 of 10 pack Terms; all eight displayed strictly-prior rows enter the calculation, with no rendered-window omission. The resulting single-event Brier skill is `1 - 0.000036 / 0.05120250431778929^2 = 0.9862684331659415`. This is a score against the specified baseline, not evidence of general forecasting calibration.

These rates describe the committed denial-reweighted live/historical rollup. I did not refresh or query the remote corpus and do not assert its current freshness. The evaluator's provisioned snapshot is dated October 5; the candidate's frozen snapshot date is September 16, 2026. Those are input vintages, not a corpus-wide newest-pull claim.

## Reasoning quality: 0.78

The rationale identifies several concrete obstacles to review: the unpublished and record-dependent decision, the undeveloped conflict presentation, a waived response without a response request in the supplied record, and the petition's acknowledgment that the lower court tested manifest disregard under an assumed federal standard. The latter is supported by the petition's account at printed pages 6–7 and 13. It appropriately identifies the correct risk-set anchor and openly states that the lower-court opinion was not independently read. These are substantive strengths independent of the correct denial forecast.

The analysis is less careful in several places. Its categorical statement that no conflict is alleged overlooks the petition's printed pages 12–13, which mention differing federal treatments of manifest disregard, although they do not develop a clean, outcome-determinative split. Describing the vehicle concern as disqualifying overstates what the petitioner's account alone establishes. The argument partly relies on terminal relist statistics and unsupported population generalizations, including attributing the originating-court GVR share to criminal lead-case sweeps and drawing a counsel-profile inference from a grants-only query without a comparison group. The precise reduction from approximately 5.12% to 0.6% remains subjective rather than quantitatively established. The denial does not validate those stronger assertions.

Only the analytical rationale in `reasoning.md` is graded here. Its embedded forecasts about auxiliary claims and significance receive no separate credit or deduction. I read `predicted_reasoning.md` for context but do not grade it or the structured claims.

## Leakage assessment

The harness log records `forward`, 20 calls, and capture coverage 1.0. The September 17 prediction precedes the October 5 resolution. The log includes a general grants-prior corpus query, a lookup of this docket, and two caption searches. The dated case-specific returns precede resolution: May 20, 2026 for the docket and August 2, 2018 for the earlier litigation search. The rationale expressly distinguishes the earlier opinion from the unlocated 2025 decision and says no cert disposition was recorded. There is no affirmative evidence that this petition's eventual disposition surfaced.

Accordingly, `retrieved_outcome_material = false`, influence is `not_applicable`, and `leakage_suspected = false`. The current evaluator snapshot's denial entry was not the predictor's snapshot and is not evidence of predictor contamination. Captured result digests are not the returned bodies, so this finding is limited to the logged queries, dates, capture markers, and staged prose.

## Scope

Cert votes are not scored, irrespective of the outcome's empty vote list. There is no merits judgment or declared semantic set, so no judgment, vote, or semantic grade is supplied. Mechanical claim scores, process and context stamps, prediction-run linkage, and baseline-version provenance remain the harness's responsibility.
