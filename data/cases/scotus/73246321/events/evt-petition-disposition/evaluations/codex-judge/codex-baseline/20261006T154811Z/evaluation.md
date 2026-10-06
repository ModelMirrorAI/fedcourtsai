# Evaluation: codex-baseline

## Outcome and scoring scope

This is a cert-stage distribution-moment evaluation. The authoritative outcome records denial on October 5, 2026, with actual_granted = 0. The provisioned October 5 docket snapshot corroborates that disposition. The denial establishes the result, not the Court's reasons for it.

Only reasoning.md supplies the reasoning-quality assessment. The pointed-to predicted_reasoning.md was read for context but is not scored; neither its accuracy nor the quantitative claims enters reasoning_quality. Mechanical claim scores are left to the harness. Cert votes are not scored, and this stage declares no semantic set. No independent big_case assessment is supplied because candidate stakes scores were visible before an independent assessment was formed.

## Baseline

The prediction freezes Term 2025, baseline, sal-v4. The committed statpack's sal-v4 heading matches, so base_rate_basis is risk_set. I pool the bracketed baseline reached rates over every displayed Term strictly before 2025, not the terminal rates and not the evaluator's current context. Printed (rate, weighted resolved n) pairs are: 2024 (5.7%, 1271), 2023 (5.9%, 1312), 2022 (5.8%, 1192), 2021 (5.6%, 1500), 2020 (4.5%, 1739), 2019 (4.6%, 1399), 2018 (4.6%, 1524), and 2017 (4.7%, 1643). Their denominator-weighted rate is 0.05120250431778929 over n = 11,580. This reconstructs a baseline from rounded published cells, not unrounded underlying counts. The caption renders 10 of 10 Terms; 2025 and 2026 are excluded, so no rendered-window divergence arises.

This is the committed live/historical-slice, denial-reweighted estimate for the private-petitioner risk set, not a census-wide or terminal-band rate. No fresh corpus query was made and no corpus-wide pull vintage is asserted. Case evidence is the supplied October 5, 2026 snapshot; the predictions' frozen snapshots are dated September 16, 2026 and are not themselves staged here. The current decided snapshot is not evidence of what a predictor saw.

## Quantitative result

Predicted disposition denied exactly matches actual disposition denied: correct = 1. P(grant) = 0.005; Brier = (0.005 - 0)^2 = 0.00002500. Brier skill = 1 - 0.00002500 / (0.05120250431778929 - 0)^2 = 0.990464189699. These are single-event scores against the stated baseline, not evidence of cohort-level predictive skill.

## Reasoning quality: 0.92

The analysis identifies the proper frozen-band risk-set prior, pools only the displayed prior Terms, and acknowledges rounding. It grounds the downward adjustment in the petition's undeveloped conflict and vehicle rather than pro se status alone. It carefully separates the petitioner's account from verified lower-court findings, a respondent's extension from a Court-requested response, and a future scheduled conference from a completed conference or relist.

Most importantly, it treats the absent appendix as limiting what can be concluded about the May 2025 dismissal, preservation, and an adequate independent state ground. Its account of the limited relevance of the petition's cited Haines authority is supported by a logged authority-specific lookup, rather than an outcome search. It avoids converting the docketing-date discrepancy into a proved timeliness defect. The exact 0.5% remains a judgmental adjustment rather than an empirically demonstrated conditional rate, and the missing lower-court orders leave real vehicle uncertainty. Those limitations prevent a perfect reasoning score; the unelaborated denial supplies no judicial endorsement of the proposed explanation.

## Leakage assessment

The harness log records forward mode and result_capture_coverage = 0.9166666666666666. Captured queries concern the provisioned September 16 materials, the statpack, and the Haines authority, not this petition's result. Two web rows are unobserved: a general Rule 10 search and a request for a general Rule 10 page. Their missing results do not establish empty retrieval, notwithstanding the candidate's self-report; their query scope nevertheless contains no case-specific outcome request. The captured authority lookup also is not retrieval of this case's disposition. Nothing in the reasoning presupposes the October 5 outcome. There is no affirmative indication of forward mis-provisioning.

Accordingly, retrieved_outcome_material = false on the observed evidence, influenced_prediction = not_applicable, and leakage_suspected = false. This is not a claim that every possible source of prior knowledge is observable.
