# Evaluation: claude-baseline

**P(grant) 0.13, predicted denied. Correct = 1, Brier = 0.0169.**

## Cell
Cert stage, `response-requested` moment, forward mode. Outcome: **denied** on 2026-11-09 (`actual_granted` 0), no noted dissent, no CVSG. The docket shows the BIO filed Oct 1, the reply Oct 9, distribution on Oct 21 for the 11/6/2026 conference, and denial at that first post-response conference with no relist. `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are the harness's to stamp (against the stamped segment base rate for the frozen `baseline` band, sal-v4). Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so I wrote no `semantic_grades`. Base-rate use is graded against the build `statpack-at` resolved for this candidate (sha 7bcde3b105cb, landed 2026-10-28), not the committed pack.

## Leakage
Forward. The prediction ran 2026-10-29, before the 2026-11-09 resolution, so it could not have retrieved the outcome. Neither the log nor the reasoning shows this case's disposition. `influenced_prediction`: not_applicable.

## Big case
My read is 0.3: a recurring takings-ripeness issue with organized amicus support, on a single-lot dispute from an unpublished opinion. The Court denied it quietly.

## Reasoning quality: 0.70
Strengths:
- The anchor is correct: the baseline reached rate pooled over 2017–2025 is about 5%, matching the resolved build's per-Term range of 4.0–5.9%.
- It names each upward signal (CFR after waiver, six amici, PLF counsel and topic) and discounts the amicus bucket, correctly, as terminal-measured and collinear with relists.
- It identifies the right vehicle weaknesses: a fact-bound unpublished finality holding, QP 2 not affecting the 12(b)(6) result, and a generously counted split.
- Its "where to discount me" section is honest.

Weaknesses: it is thinner on record specifics than the other two and does not engage the district-court factual record or the Burford remark. The "doubles to triples" CFR multiplier is asserted, not grounded. Its net 13% is reasonably calibrated.

## Predicted reasoning: 0.72
Central claims: denial on vehicle grounds; redistribution and then denial at the **first** post-response conference (about a 1-in-4 relist chance); no CVSG; a dissent from denial unlikely. All four were borne out, and the timing claim is the most specific of the three documents and exactly matched the 11/6 conference. The QP 1 and summary-route content is conditional on a grant and unresolved. It is specific and right, but on the modal path.
