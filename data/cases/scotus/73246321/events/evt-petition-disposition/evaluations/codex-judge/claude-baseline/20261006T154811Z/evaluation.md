# Evaluation: claude-baseline

## Outcome and scoring scope

This is a cert-stage distribution-moment evaluation. The authoritative outcome records denial on October 5, 2026, with actual_granted = 0. The provisioned October 5 docket snapshot corroborates that disposition. The denial establishes the result, not the Court's reasons for it.

Only reasoning.md supplies the reasoning-quality assessment. The pointed-to predicted_reasoning.md was read for context but is not scored; neither its accuracy nor the quantitative claims enters reasoning_quality. Mechanical claim scores are left to the harness. Cert votes are not scored, and this stage declares no semantic set. No independent big_case assessment is supplied because candidate stakes scores were visible before an independent assessment was formed.

## Baseline

The prediction freezes Term 2025, baseline, sal-v4. The committed statpack's sal-v4 heading matches, so base_rate_basis is risk_set. I pool the bracketed baseline reached rates over every displayed Term strictly before 2025, not the terminal rates and not the evaluator's current context. Printed (rate, weighted resolved n) pairs are: 2024 (5.7%, 1271), 2023 (5.9%, 1312), 2022 (5.8%, 1192), 2021 (5.6%, 1500), 2020 (4.5%, 1739), 2019 (4.6%, 1399), 2018 (4.6%, 1524), and 2017 (4.7%, 1643). Their denominator-weighted rate is 0.05120250431778929 over n = 11,580. This reconstructs a baseline from rounded published cells, not unrounded underlying counts. The caption renders 10 of 10 Terms; 2025 and 2026 are excluded, so no rendered-window divergence arises.

This is the committed live/historical-slice, denial-reweighted estimate for the private-petitioner risk set, not a census-wide or terminal-band rate. No fresh corpus query was made and no corpus-wide pull vintage is asserted. Case evidence is the supplied October 5, 2026 snapshot; the predictions' frozen snapshots are dated September 16, 2026 and are not themselves staged here. The current decided snapshot is not evidence of what a predictor saw.

## Quantitative result

Predicted disposition denied exactly matches actual disposition denied: correct = 1. P(grant) = 0.005; Brier = (0.005 - 0)^2 = 0.00002500. Brier skill = 1 - 0.00002500 / (0.05120250431778929 - 0)^2 = 0.990464189699. These are single-event scores against the stated baseline, not evidence of cohort-level predictive skill.

## Reasoning quality: 0.78

The analysis gives a reproducible, correctly conditioned prior and explains why this short, case-specific petition merits a substantial downward adjustment. It distinguishes one scheduled conference from repeated consideration, notes the response waiver, identifies the lack of a developed conflict in the petition, and explicitly acknowledges the missing appendix, OCR limitations, and inconsistent dates. Its nonzero probability recognizes residual uncertainty.

The principal weakness is overstatement of the lower-court procedural ground. The petition expressly calls the October 2024 dismissal untimely but merely says the May 2025 application was dismissed. Without the lower-court orders, characterizing the operative judgment as an untimeliness dismissal and asserting an established adequate-and-independent-state-ground bar goes beyond the supplied evidence. The categorical assertion that the Court does not review state enforcement of deadlines also does not engage the petition's constitutional challenge to that enforcement. The small convenience sample of recent denied cases, including applications according to its own retrieval note, cannot calibrate this paid-cert probability. These are limits of the reasoning even though the denial call was correct; the result does not establish the asserted jurisdictional rationale.

## Leakage assessment

The harness log records forward mode and result_capture_coverage = 1.0. Logged work reads the September 16 baseline and petition, the statpack, and a general recent-denials corpus query. That query's legible document date is September 10, 2026, before this petition's October 5 resolution. Its retrieval note reports unrelated priors. No logged query seeks this case's later disposition and the prose does not claim to have seen it. The forecast's October 5 date is explicitly a prospective estimate from the scheduled conference, not evidence of a retrieved order. Directory listings and a status command excluding a labeling path are not reads of outcome-bearing labeling contents. No evidence of an already-decided case being provisioned forward appears.

Accordingly, retrieved_outcome_material = false on the observed evidence, influenced_prediction = not_applicable, and leakage_suspected = false. This is not a claim that every possible source of prior knowledge is observable.
