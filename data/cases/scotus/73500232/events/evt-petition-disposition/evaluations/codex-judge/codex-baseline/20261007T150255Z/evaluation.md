# Evaluation: codex-baseline

Prediction run: 20260917T181231Z. Predicted denied with P(any grant) = 0.008. Exact disposition correctness = 1; Brier = (0.008 - 0)^2 = 0.00006400; baseline-relative Brier skill = 0.975588325628. Reasoning quality = 0.92. These are single-event scores, not evidence of aggregate calibration or performance.

## Reasoning assessment

The rationale makes a disciplined distinction between allegations, established record facts, and independent verification. It uses the frozen Term and sal-v4 baseline risk set, labels its weighted calculation approximate, and separates terminal relist correlations from forward transition probabilities. It explains why a sympathetic two-day delay does not itself establish a review-worthy conflict and identifies the petition's mixing of procedural settings and district-court authority.

Its discussion of the separate-document theory is specific and appropriately conditional: it connects the petition's characterization of the appealed order as denial of Rule 60 relief to the rule text it reports checking, while expressly reserving the possibility that missing lower-court materials alter the characterization. This evaluation credits that analytical method and qualification, not an independently established lower-court holding. The candidate also avoids converting missing docket entries into a formal waiver or agreement.

The remaining limitation is numerical calibration: the reduction from approximately 5.12% to 0.8% is reasoned but not fitted to a measured comparator population. The appendix and lower-court opinion were unavailable, and the denial supplies no explanation validating any particular doctrinal inference. These limitations prevent a perfect reasoning grade.

## Baseline and scoring scope

This is a cert-stage evaluation against the provisioned outcome.json: denied on October 5, 2026, actual_granted = 0. All candidate predictions were made on September 17, 2026. A bare denial does not supply the Court's rationale and does not establish that any particular legal argument in the prediction was adopted.

The prediction's frozen context is baseline / sal-v4 / Term 2025. The committed metrics/statpack.md heading matches sal-v4. I pool the bracketed baseline reached figures over every displayed Term strictly before 2025: 2017–2024. The weighted resolved denominator is 11,580; multiplying the displayed rounded rates by their denominators yields 592.925 estimated weighted grants and a rate of 0.05120250431778929. This is an approximate rate from rounded, denial-reweighted live/historical-slice figures, not an exact grant count or a refreshed corpus estimate. The table renders 10 of 10 Terms; 2025 and 2026 are excluded. No rendered-window discrepancy or salience-version mismatch requires omission. base_rate_basis is risk_set, using the prediction's frozen context, not the evaluator's terminal context. These figures describe the committed pack consulted in this run; no current corpus freshness is asserted.

reasoning_quality grades reasoning.md alone. predicted_reasoning.md was read for context but not scored, and neither the structured quantitative claims nor forecast accuracy was folded into reasoning quality. claim_scores is left for the harness. Cert votes are unscored; no vote_accuracy or semantic_grades is written. The optional independent stakes assessment is omitted.

## Leakage assessment

Forward mode; result-capture coverage is 27/29 (approximately 0.931). The log shows provisioned-input reads, a Third Circuit docket search bounded before October 2, 2025, and general procedural-rule retrieval. Two web calls are unobserved and cannot be credited as returning nothing, but their queries concern Rule 58 rather than this petition's disposition. Captured direct-fetch calls concern general rule text. No query or reasoning shows this case's October 5 outcome known before prediction.

The September 17 prediction preceded the recorded October 5 resolution. There is no affirmative evidence of a decided case mis-provisioned forward. Accordingly influenced_prediction is not_applicable and leakage_suspected is false; quantitative scores are unchanged by this assessment.
