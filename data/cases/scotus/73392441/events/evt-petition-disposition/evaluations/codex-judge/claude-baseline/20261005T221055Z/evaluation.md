# Evaluation: claude-baseline

Case: scotus/73392441 (Supreme Court docket 25-1310). Event: evt-petition-disposition. Evaluator run: 20261005T221055Z.

## Outcome and numerical score

The supplied cert-stage outcome records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The staged candidate prediction from run `20260917T181231Z` names **denied**, with grant probability **0.007**. Thus `correct = 1`, Brier = (0.007 - 0)^2 = **0.000049**, and Brier skill against the prior-Term baseline below = **0.981309811809198**. This is a single-outcome score, not evidence of calibration or aggregate forecasting performance.

## Reasoning quality: 0.78

The rationale makes a coherent downward adjustment from the correctly matched roughly 5.1% prior-Term risk-set anchor. It identifies the private deed-of-trust dispute, unpublished state appellate disposition, lack of a developed decisional split, and the distinction between the petition's federal jury-trial theory and its due-process argument. The provisioned petition supports the described reformation posture, cross-motions, and alleged inspection of the note. The candidate explicitly acknowledges that the missing appendix prevents independent verification of the lower-court record.

The main deductions are for assumptions beyond that evidence. The counsel-history adjustment relies on expressly unverified training recollection. No response in a sparse docket is not sufficient to establish that nobody has requested one, and the claim that the vehicle is procedurally clean is stronger than the acknowledged record permits. The reasoning treats the due-process issue rather dismissively without closely testing the alleged genuine factual dispute. The 0.7% estimate is a defensible judgmental forecast, not an empirically estimated conditional rate. Correctly predicting the denial does not cure those evidentiary limitations.

## Baseline and scoring scope

Each candidate's own frozen context supplies `baseline`, `sal-v4`, and docket Term 2025. The sal-v4 heading in the committed `metrics/statpack.md` matches that version. I use the bracketed **reached** rate, not the leading terminal-band rate, and pool all displayed Terms strictly before 2025:

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

The published rounded percentages give 592.925 grant-family equivalents / 11,580 weighted resolved petitions = **0.05120250431778929**. Thus `base_rate_basis = risk_set`; these are denial-reweighted live/historical-slice estimates, not raw counts. The table displays 10 of 10 Terms; 2025 and 2026 are excluded, leaving all eight displayed prior-Term rows. No rendered-window truncation is indicated. The scoring rate is intentionally reconstructed from the rendered table rather than an unrounded JSON rate quoted by a candidate.

This is a calculation from the committed statpack supplied to this cell, not a claim about refreshed corpus state. No corpus query or corpus-wide freshness check was performed. The outcome and evaluator snapshot are dated October 5, 2026; the scored predictions froze September 16, 2026 snapshots and were produced September 17, 2026. The evaluator's terminal context was not substituted for any prediction's context.

Only `reasoning.md` receives the qualitative grade. The pointed-to `predicted_reasoning.md` was read for context, not scored. Mechanical claims remain for the harness; this cert event declares no semantic grading set. Individual cert votes are not scored, and `vote_accuracy` is omitted. The recorded denial does not supply a judicial explanation or establish the truth of any predicted merits rationale. No independent big-case score is supplied.

## Leakage assessment

`mode = forward`; `retrieved_outcome_material = false`; `influenced_prediction = not_applicable`; `leakage_suspected = false`.

The captured log records 27 calls with result-capture coverage 1.0. Its case-specific CourtListener queries concern docket 25-1310 and docket entries; the docket-header row has `retrieved_doc_date = 2026-05-26`. The candidate describes a pending, unterminated docket last modified July 8, 2026. The broad corpus query requests granted cases rather than this petition's outcome. Those inquiries were permissible while this forward case remained open. The specific October 5 date in the forecast is presented as an expected order-list date, not evidence of an already-known denial. Captured-result markers establish observability, not the full contents of results whose text is not staged. Read together with the query slices and prose, they provide no evidence of outcome retrieval or mis-provisioning.
