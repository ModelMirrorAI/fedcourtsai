# Evaluation: codex-baseline

## Outcome and quantitative scores

The blinded prediction from run 20260916T201911Z names denied with P(grant) = 0.16. This is a cert-stage event; the supplied outcome records denial on October 5, 2026, actual_granted = 0, consistent with the evaluator's October 5 snapshot. Exact-label correct = 1 and Brier = (0.16 - 0)^2 = 0.0256.

The baseline follows the candidate's frozen elevated band, sal-v4 version, and Term 2025, not the evaluator's decided context. The committed sal-v4 table's bracketed reached rates support risk_set. The eligible displayed rate/weighted-resolved pairs are 2024, 17.9%/336; 2023, 17.5%/354; 2022, 19.0%/300; 2021, 20.5%/342; 2020, 16.1%/397; 2019, 13.8%/334; 2018, 15.9%/347; 2017, 17.5%/400. Their pooled rate is 484.386 / 2810 = 0.17237935943060498. Terms 2025 and 2026 are excluded. The caption renders ten of ten Terms, so there is no truncated-window discrepancy to flag.

The rendered percentages imply a rounded-data numerator rather than an exact integer grant count. The candidate reports consulting the JSON companion for 484/2810 = 0.17224199288256228; I use the prompt-required rendered table for this evaluation. That small precision difference is not a different population or an analytical error. These baseline figures are committed denial-reweighted live/historical-slice estimates, not freshly queried corpus state. Skill = 1 - 0.0256 / baseline^2 = 0.1384719136783547. This is an improvement over this baseline on this denial, not evidence by itself of broader calibration or forecasting skill.

## Reasoning quality: 0.87

The rationale anchors to the correct versioned risk-set population, excludes the petition's own Term, and avoids treating overlapping terminal relist and CVSG cuts as independent predictors. It distinguishes two docket distributions from two completed conferences, an important limitation on how much procedural attention the record demonstrates.

Its substantive discussion treats both litigants' split characterizations as advocacy. It recognizes the appellate memorandum's actual reliance on the information-based rule and also the document-specific features emphasized by the opposition. Rather than treating unpublished status as eliminating an issue grounded in en banc precedent, it presents that status as a vehicle concern. The modest reduction from the baseline to 16% is coherently explained through that balance. The supplied petition appendix and opposition support the described competing positions; an unexplained cert denial does not adjudicate which interpretation is correct.

The rationale's source discipline is a strength: it distinguishes snapshot date from source recency, acknowledges the truncated appendix, and explicitly declines to infer the unextracted reply's contents. Its main limitation is incomplete consideration of that reply, which could change the presentation of the asserted split or vehicle objections. The exact 16% remains a judgmental adjustment, without an independently estimated likelihood contribution for each factor. Those limitations reduce confidence in completeness and precision without making the analysis unsound or rewarding the realized denial after the fact.

This grade is confined to reasoning.md's analysis of the headline number. The structured claims and predicted_reasoning.md are not independently scored or folded into the quality grade.

## Leakage and scope

The harness records forward mode, September 16 calls, and capture coverage 27/28 (approximately 0.9643). Its sole unobserved web request names the September 2 reply PDF already linked in the snapshot. A null retrieved date and missing captured result cannot establish that nothing was returned; the candidate's statement that extraction failed is treated as a disclosure, not as independent result telemetry. The request's target and timing nevertheless make it legitimate pre-resolution forward retrieval even if it returned the filing. No visible query or rationale discloses the October 5 denial, and the September 16 snapshot read is not confused with the evaluator's later snapshot.

Thus retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false. The unrelated class label other on shell-like calls is not treated as suspicious. A path-exclusion pattern used while looking for instruction files is not a read of excluded labeling artifacts.

This cert cell receives no vote accuracy or semantic grades. Mechanical claim scores, provenance stamps, and prediction linkage are left to the harness. No independent big-case assessment is supplied.
