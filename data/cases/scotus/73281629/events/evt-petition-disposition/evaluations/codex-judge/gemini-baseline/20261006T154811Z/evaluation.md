# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a cert-stage evaluation of the blinded prediction from run 20260916T170237Z. The supplied outcome records denial on October 5, 2026, actual_granted = 0, and no noted dissent from denial. The October 5 evaluator snapshot also records the denial. The prediction's denied label is an exact match: correct = 1. With P(grant) = 0.28, Brier = (0.28 - 0)^2 = 0.0784.

The prediction froze elevated under sal-v4 in Term 2025. Those fields match the committed statpack's sal-v4 table, so the baseline uses the bracketed reached population, not terminal elevated and not the evaluator's context. Pooling every displayed strictly earlier Term gives these rate/weighted-resolved pairs: 2024, 17.9%/336; 2023, 17.5%/354; 2022, 19.0%/300; 2021, 20.5%/342; 2020, 16.1%/397; 2019, 13.8%/334; 2018, 15.9%/347; 2017, 17.5%/400. Their resolved-weighted rate is 484.386 / 2810 = 0.17237935943060498. The numerator is reconstructed from rounded displayed percentages, not an exact integer grant count. The table renders all ten of its ten Terms; 2025 and 2026 are excluded, leaving eight eligible rows and no rendered-window discrepancy to flag.

These are the supplied committed table's denial-reweighted live/historical-slice estimates, not a newly queried or refreshed corpus. Skill = 1 - 0.0784 / baseline^2 = -1.6384297643600387. Thus the label was right, but the 28% grant probability incurred more loss than the eligible band baseline on this denial. This is a single-event comparison, not a calibration or performance claim.

## Reasoning quality: 0.50

The rationale uses the appropriate reached-band concept, identifies the Court's request for a response after waiver, and recognizes uncertainty about the opposition's vehicle objections. It does not mistake the extension application for a grant of certiorari. These are useful elements of a probabilistic account.

The central upward adjustment is nevertheless inadequately tested. The rationale treats an acknowledged nine-to-one split as established when the supplied questions presented state the petitioner's position and the opposition expressly contests both the methodological split and the narrower document-specific conflict. The provisioned opposition and petition appendix offer substantive material on the unpublished memorandum, document-specific findings, and differing factual settings; the candidate's log shows no read of those texts, and its rationale says it examined only the QP and docket in detail. That limited investigation leaves the most consequential premise unsupported by adversarial analysis. The move from roughly 15–20% to 28% is not quantitatively justified, and the response request is not clearly separated from information already represented by the elevated-band prior.

The grade concerns the rationale's evidentiary discipline and support for its number, not the fact that a 28% event failed to occur. An unexplained denial establishes neither side's substantive legal theory. The forecast document and the structured claim probabilities are not scored here or folded into this quality grade.

## Leakage and scope

The harness log labels the prediction forward and dates its calls to September 16, before the October 5 resolution. Its snapshot read targets September 15; the corpus query requests a general sample of granted cases rather than this case's outcome. Nothing in the visible queries or reasoning discloses the later denial. All 21 call results are unobserved, so capture coverage of 0.0 limits the audit: null dates are not proof that a query returned nothing. On the available timing, query, and prose evidence, retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false. The evaluator's decided snapshot is not treated as the candidate's input.

No vote accuracy or semantic grades apply to this cert cell. Mechanical claim scores, provenance, and prediction linkage are left to the harness. No independent big-case assessment is supplied.
