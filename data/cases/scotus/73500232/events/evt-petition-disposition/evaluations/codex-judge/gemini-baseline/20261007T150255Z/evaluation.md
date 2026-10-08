# Evaluation: gemini-baseline

Prediction run: 20260917T181231Z. Predicted denied with P(any grant) = 0.001. Exact disposition correctness = 1; Brier = (0.001 - 0)^2 = 0.00000100; baseline-relative Brier skill = 0.999618567588. Reasoning quality = 0.58. These are single-event scores, not evidence of aggregate calibration or performance.

## Reasoning assessment

The rationale correctly emphasizes the fact-bound missed-deadline dispute, pro se presentation, initial distribution, and lack of an affirmative response-request signal. Those observations coherently support denial rather than national doctrinal review.

The statistical anchor is materially mislabeled: a roughly 1.2% zero-relist figure is not the prior-Term sal-v4 baseline risk-set rate. A terminal zero-relist subset is not the population of petitions currently at their first distribution, and the rationale does not distinguish plain grants from all grants including GVRs. It neither evaluates the petition's claimed conflict nor explains why the separate-document question fails as a vehicle. Generic search results about appeal extensions cannot establish how rarely comparable petitions receive Supreme Court review. The very large downward adjustment to 0.1% is weakly quantified, and the categorical confidence is not earned by the short analysis. The smaller realized Brier error is not evidence that this reasoning is superior.

Retrieval documentation needs qualification: retrieval.md says no corpus lookups executed, but the harness log contains an attempted corpus-query command and a query-help call. Every result is unobserved, so the attempt cannot be treated as a successful lookup, a confirmed failure, or an empty return. This discrepancy is flagged for provenance, not treated as outcome leakage.

## Baseline and scoring scope

This is a cert-stage evaluation against the provisioned outcome.json: denied on October 5, 2026, actual_granted = 0. All candidate predictions were made on September 17, 2026. A bare denial does not supply the Court's rationale and does not establish that any particular legal argument in the prediction was adopted.

The prediction's frozen context is baseline / sal-v4 / Term 2025. The committed metrics/statpack.md heading matches sal-v4. I pool the bracketed baseline reached figures over every displayed Term strictly before 2025: 2017–2024. The weighted resolved denominator is 11,580; multiplying the displayed rounded rates by their denominators yields 592.925 estimated weighted grants and a rate of 0.05120250431778929. This is an approximate rate from rounded, denial-reweighted live/historical-slice figures, not an exact grant count or a refreshed corpus estimate. The table renders 10 of 10 Terms; 2025 and 2026 are excluded. No rendered-window discrepancy or salience-version mismatch requires omission. base_rate_basis is risk_set, using the prediction's frozen context, not the evaluator's terminal context. These figures describe the committed pack consulted in this run; no current corpus freshness is asserted.

reasoning_quality grades reasoning.md alone. predicted_reasoning.md was read for context but not scored, and neither the structured quantitative claims nor forecast accuracy was folded into reasoning quality. claim_scores is left for the harness. Cert votes are unscored; no vote_accuracy or semantic_grades is written. The optional independent stakes assessment is omitted.

## Leakage assessment

Forward mode; result-capture coverage is 0.0. Queries address the provisioned September 17 inputs and general Rule 4(a)(5) authorities, including an attempted date-bounded corpus query. Unobserved results are not empty results; the reported search count is only the candidate's account. Neither query text nor reasoning indicates retrieval or knowledge of this petition's October 5 denial. The unobserved telemetry is a limitation, not a defect or evidence of leakage.

The September 17 prediction preceded the recorded October 5 resolution. There is no affirmative evidence of a decided case mis-provisioned forward. Accordingly influenced_prediction is not_applicable and leakage_suspected is false; quantitative scores are unchanged by this assessment.
