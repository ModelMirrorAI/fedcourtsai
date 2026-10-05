# Evaluation: gemini-baseline

Case: scotus/73392441 (Supreme Court docket 25-1310). Event: evt-petition-disposition. Evaluator run: 20261005T221055Z.

## Outcome and numerical score

The supplied cert-stage outcome records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The staged candidate prediction from run `20260917T181231Z` names **denied**, with grant probability **0.005**. Thus `correct = 1`, Brier = (0.005 - 0)^2 = **0.000025**, and Brier skill against the prior-Term baseline below = **0.990464189698571**. This is a single-outcome score, not evidence of calibration or aggregate forecasting performance.

## Reasoning quality: 0.65

The short rationale correctly identifies the central forecast considerations: an individualized property dispute, a state-court summary-judgment challenge, no developed split, and difficulties with treating a federal civil-jury guarantee as directly controlling state proceedings. Its denial prediction is consistent with the realized outcome, and a small nonzero grant probability is reasonable for the posture described.

The analysis is less well supported than the other candidates' rationales. It gives about 5.7% as the prior-Term anchor, which matches the displayed 2024 row but not the required pooled 2017–2024 rate of about 5.12%; it never shows the pooling. It does not separately examine the petition's due-process argument or the equitable reformation vehicle, and it does not acknowledge the missing appendix or the limitations of a one-sided petition record. It states that no opposition was filed rather than limiting that claim to the supplied docket. Placement on a long-conference list is ordinary scheduling and cannot alone establish particular disinterest. The final 0.5% adjustment is asserted rather than developed. These are reasoning limitations, not penalties for brevity, tool choice, or an otherwise correct outcome call.

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

The log records 25 calls, all marked `unobserved`, with result-capture coverage 0.0. I do not infer failed or empty results from their missing dates or digests. The visible requests read the September 16 snapshot, petition/QP and aggregate statpack, or perform local output/validation operations; no request seeks a current case result or post-decision coverage. The prose describes the upcoming conference and contains no already-decided facts. The visible petition read is limited to its first 100 lines, which further limits evidence of detailed source engagement but is not leakage. On this affirmative query/prose evidence and the September 17 forward timing, there is no sign of a decided case being provisioned forward. This assessment is explicitly limited by uncaptured results; the capture pattern itself is not a data defect.
