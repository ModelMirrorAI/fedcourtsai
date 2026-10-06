# Evaluation: gemini-baseline

## Outcome and mechanical scores

The event declares stage `cert`, although the docket describes an original mandamus petition. I retain that declared scoring axis and flag the population mismatch rather than reclassify the event. The committed outcome is `denied`, `actual_granted = 0`, resolved October 5, 2026. gemini-baseline's September 17 prediction names `denied` and P(grant) = 0.001: **correct = 1; Brier = 0.000001**.

The selected baseline is the prediction's frozen `baseline` band under `sal-v4`, not the evaluator's decided-docket context. That version matches the committed statpack heading. Pooling the bracketed reached rates for all displayed Terms strictly before its Term 2025 gives:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The denominator is 11,580 and the rate-times-denominator sum is 592.925, yielding **0.05120250431778929**, basis `risk_set`. The numerator is reconstructed from rounded published percentages, not an exact grant count. Brier skill is `1 - 0.000001 / baseline^2` = **0.9996185675879428**. The table displays 10 of 10 Terms; 2025 and 2026 are excluded. No rendered-window mismatch arises. These are committed-pack estimates, not newly refreshed corpus counts. The baseline is an ordinary paid-cert risk set, not a matched mandamus cohort; this one denial does not establish calibration or general forecasting skill.

## Rationale quality: 0.55

The rationale correctly identifies mandamus, self-representation, the response waivers, and the frozen baseline. It recognizes that an extraordinary-writ petition differs from the ordinary petition population and gives a coherent qualitative reason to move below the approximately 5% reference rate.

The analytical support for the precise 0.1% is thin. It treats a missing lower-court metadata field as no lower-court decision, when that field establishes only missing information. It also treats waivers as evidence that respondents regard the petition as meritless without separating that inference from the observed procedural act. Its near-universal-denial assertion supplies neither a matched sample nor an explicit extraordinary-writ test, and the rationale does not identify the petition's substantive request. Those weaknesses matter independently of the correct outcome. A bare denial does not confirm the proposed reasons for denial.

Only `reasoning.md` determines this grade. The forecast document was read for context but is not scored; neither its procedural predictions nor the structured claims affect this qualitative score. Mechanical claim scores remain the harness's. No semantic grade, vote accuracy, or judgment comparison is appropriate on this cert-stage cell.

## Leakage and limitations

The harness records `forward` and September 17 calls, before the October 5 resolution. The queries and rationale reveal no already-decided disposition of this petition. Influence is `not_applicable`, and leakage is not suspected. All 24 call results are `unobserved`; the 0.0 capture coverage and null document dates cannot prove that searches found nothing. The query evidence supports the ordinary forward assessment without inventing any result contents.

The log also records a corpus-query attempt for Joan Farr that the candidate's retrieval note does not mention. I flag that narrow self-report discrepancy without inferring success, failure, or leakage. The petition text available in this evaluation is not assumed to have been available to the predictor.

My independent significance assessment is 0.05, formed before viewing candidate scores from the staged questions presented, snapshot, and outcome: individual next-friend and party-joinder requests, with no demonstrated broad doctrinal reach. It is not an agreement score.
