# Evaluation: claude-baseline

## Result and baseline

This is a cert-stage evaluation of the blinded prediction from run 20260917T214606Z. The authoritative outcome records denial on October 5, 2026, with actual_granted = 0. The predicted label is denied, so correct = 1. At P(grant) = 0.012, the Brier score is (0.012 - 0)^2 = 0.000144.

The prediction freezes baseline under sal-v4, Term 2025. The committed metrics/statpack.md heading also names sal-v4. I pool the baseline column's bracketed reached rates over every displayed strictly-prior Term, 2017–2024, rather than deriving a band from the decided docket. The rate/weighted-denominator pairs, newest first, are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. These printed, rounded rates yield 592.925 weighted grant-equivalents / 11,580 = 0.05120250431778929. This is a denial-reweighted live/historical-slice estimate, not a raw count or a newly refreshed corpus measurement. The caption renders 10 of 10 Terms; there is no hidden-window divergence. Terms 2025 and 2026 are excluded. Basis: risk_set. Skill = 1 - 0.000144 / baseline^2 = 0.9450737326637661. That is a single-outcome comparison, not evidence of aggregate calibration.

## Reasoning quality: 0.80

The rationale identifies a plausible low-review-probability vehicle: an unpublished per curiam affirmance, a petition seeking correction of summary-judgment treatment, and a claimed conflict that is not demonstrated as a square outcome-determinative split. It correctly distinguishes the risk-set anchor from the terminal band rate and explains the downward adjustment. It also recognizes that the panel focused on the protected-contractual-activity element rather than deciding every element of ultimate liability.

The main weakness is overstating the independence of the panel's rationale from disputed facts. Appendix pages 6a–7a expressly rely on continued service and the asserted length of the restaurant stay when rejecting severe harassment; those facts cannot simply be dismissed as concerning elements the panel did not decide. The rationale also gives negative weight to counsel's practice profile without a measured association, and turns absence of an opposition in the available record into a firmer statement that none was filed. Its statement that distribution occurred on the response deadline conflicts with its own July 1 deadline and July 15 distribution dates. These limitations reduce the score despite the correct label. The unelaborated denial does not establish why the Court denied review or ratify the lower court's legal analysis.

## Leakage and scope

The log records forward mode and 27/27 captured calls on September 17, before resolution. Its own-docket retrieval is legitimate in that setting; the dated MCP result predates resolution, and the prose reports a pending docket. There is no affirmative evidence of outcome exposure. The prospective October 5 forecast is not treated as leakage merely because it proved correct. I record retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false; captured digests do not permit reconstructing every returned byte.

I read predicted_reasoning.md only for context. Neither that document nor the structured claims contributes to reasoning_quality; claim scoring belongs to the harness. Cert votes and semantic propositions are not scored. No independent big_case grade is supplied. A cell-level data-quality flag records the provisioned petition filing-date inconsistency; no timeliness conclusion or score adjustment rests on choosing between those dates.
