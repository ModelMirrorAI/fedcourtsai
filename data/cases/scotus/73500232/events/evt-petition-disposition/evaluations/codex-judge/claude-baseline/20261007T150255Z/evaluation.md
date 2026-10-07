# Evaluation: claude-baseline

Prediction run: 20260917T181231Z. Predicted denied with P(any grant) = 0.006. Exact disposition correctness = 1; Brier = (0.006 - 0)^2 = 0.00003600; baseline-relative Brier skill = 0.986268433166. Reasoning quality = 0.78. These are single-event scores, not evidence of aggregate calibration or performance.

## Reasoning assessment

The analysis correctly identifies an individual, fact-bound appeal-extension dispute and distinguishes an asserted split from demonstrated conflicting holdings. It interrogates the petition's use of a district-court decision as circuit authority and acknowledges that the lower-court opinion could not be independently retrieved. Its explicit sal-v4 risk-set anchor, approximate pooling, and disclosure that the pro se adjustment is judgment rather than a measured subgroup rate make the probability traceable.

Several steps are overstated. A missing response entry supports only an inference about the visible docket, not certainty that no response was filed or equivalence to an express waiver. The inferred return-for-correction history is conjectural. Calling a CVSG impossible overstates the record, and the categorical treatment of the asserted split exceeds the independently verified authority. The substantial adjustment from roughly 5.12% to 0.6% remains subjective. These limitations reduce reasoning quality without changing the correct outcome score.

## Baseline and scoring scope

This is a cert-stage evaluation against the provisioned outcome.json: denied on October 5, 2026, actual_granted = 0. All candidate predictions were made on September 17, 2026. A bare denial does not supply the Court's rationale and does not establish that any particular legal argument in the prediction was adopted.

The prediction's frozen context is baseline / sal-v4 / Term 2025. The committed metrics/statpack.md heading matches sal-v4. I pool the bracketed baseline reached figures over every displayed Term strictly before 2025: 2017–2024. The weighted resolved denominator is 11,580; multiplying the displayed rounded rates by their denominators yields 592.925 estimated weighted grants and a rate of 0.05120250431778929. This is an approximate rate from rounded, denial-reweighted live/historical-slice figures, not an exact grant count or a refreshed corpus estimate. The table renders 10 of 10 Terms; 2025 and 2026 are excluded. No rendered-window discrepancy or salience-version mismatch requires omission. base_rate_basis is risk_set, using the prediction's frozen context, not the evaluator's terminal context. These figures describe the committed pack consulted in this run; no current corpus freshness is asserted.

reasoning_quality grades reasoning.md alone. predicted_reasoning.md was read for context but not scored, and neither the structured quantitative claims nor forecast accuracy was folded into reasoning quality. claim_scores is left for the harness. Cert votes are unscored; no vote_accuracy or semantic_grades is written. The optional independent stakes assessment is omitted.

## Leakage assessment

The log records forward mode and full result-capture coverage (1.0). Calls concern the provisioned September 17 record, general granted-case comparators, and a lower-court search captured as throttled. No call or rationale shows this petition's October 5 disposition already known. A forecast naming October 5 as the expected order-list date is not itself evidence of retrieval. One logged command reads an unrelated case's prediction as an apparent format example; it does not establish retrieval of this case's outcome and was not followed by this evaluator.

The September 17 prediction preceded the recorded October 5 resolution. There is no affirmative evidence of a decided case mis-provisioned forward. Accordingly influenced_prediction is not_applicable and leakage_suspected is false; quantitative scores are unchanged by this assessment.
