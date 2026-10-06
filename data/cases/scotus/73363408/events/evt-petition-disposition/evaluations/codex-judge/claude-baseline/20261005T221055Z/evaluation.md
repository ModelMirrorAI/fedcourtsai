# Evaluation: claude-baseline

## Outcome and numerical scores

This event resolved at the **cert** stage: **denied**, actual_granted **0**, on **October 5, 2026**. claude-baseline names **denied** at P(any grant) **0.003**, earning correct **1** and Brier **0.000009**. The provisioned October 5 snapshot is a decided record, not the predictor's September 16 baseline.

The candidate freezes **baseline / sal-v4 / Term 2025**, matching the committed statpack heading. The **risk_set** baseline pools the bracketed reached rates from every displayed prior Term: 2024, 5.7%, n=1271; 2023, 5.9%, n=1312; 2022, 5.8%, n=1192; 2021, 5.6%, n=1500; 2020, 4.5%, n=1739; 2019, 4.6%, n=1399; 2018, 4.6%, n=1524; 2017, 4.7%, n=1643. The weighted numerator is **592.925**, weighted resolved denominator **11,580**, and baseline **0.05120250431778929**. This uses rounded denial-reweighted estimates, not exact integer grant counts. Terms 2025 and 2026 are excluded; the table renders 10 of 10 Terms, so no undisplayed-window discrepancy arises. I made no fresh corpus query and obtained no corpus pull vintage; the number describes the committed table only.

Brier skill is **1 - 0.000009 / 0.05120250431778929^2 = 0.9965671082914854**. This is a one-case score, not a calibration claim.

## Reasoning quality: 0.68

The rationale correctly computes the prior-Term risk-set anchor and identifies the mismatch between the petition's criminal-appeal analogies and the civil finality/notice issue. It recognizes that an eight-case originating-court sample is too small to carry substantial weight, discloses that its pro se/waiver adjustments are not supported by dedicated statpack cuts, and keeps its grant estimate above zero for uncertainty. Those are meaningful strengths.

Several claims exceed the record. Most concretely, the rationale suggests the federal claim was first raised in the petition for state supreme court review. The supplied petition, pages 12–14, instead describes a February 19, 2025 appellate response asserting constitutional notice objections and an April 22 reconsideration motion asserting constitutional claims, both before the May 27 petition for review. Those are the petitioner's representations, not independently verified preservation findings, but they directly weaken the late-raising inference. Calling the state ground definitively adequate and independent without the underlying orders similarly promotes an unresolved vehicle concern into an established bar.

The rationale also generalizes the waiver beyond the named insurer/adjuster and states that no BIO exists because respondents waived; the record supports absence from the supplied documents, not that causal certainty. It asserts a very low pro se comparative grant rate without a matched empirical cut, and treats caption complexity and format-correction history as additional negatives without demonstrating their incremental predictive value. These partly overlapping signals do not tightly calibrate the reduction from 5.12% to 0.3%.

The actual denial agrees with the forecast but supplies no explanation establishing those asserted barriers. The quality score rewards the genuine record engagement and correct anchor while discounting material overstatement. It does not score the conditional route probabilities, forecast rhetoric, or correctness of predicted court reasoning.

## Leakage and provenance

The harness says **forward**; logged activity on September 16 precedes the October 5 resolution. Capture coverage is **1.0**, but staged result digests are not the full returned contents. The general corpus query is disclosed in retrieval.md, including its reported transfer line, and the rationale says the recency-ranked priors did not inform the estimate. No visible material identifies this petition as already decided. The accurate October 5 timing forecast is not by itself evidence of foreknowledge.

The 21:05:22Z shell call also selects and reads a prediction example through a cross-docket wildcard. Its identity is masked; the record does not establish whether it was the candidate's own earlier work or another source, and I did not attempt to identify or retrieve it. The target and returned content are not recoverable from the digest alone. This is noted as a provenance limitation, not presumed outcome leakage or a proven contract violation, and is flagged for visibility. On the evidence provided, retrieved_outcome_material is **false**, influenced_prediction **not_applicable**, and leakage_suspected **false**.

The independent stakes score is **0.12**, formed before viewing candidate stakes scores: a possible generally applicable notice rule, but a narrow procedural vehicle and a denial without a substantive ruling.

Only reasoning.md determines reasoning_quality. The forecast was read as context, not graded. No cert-vote accuracy, semantic grades, quantitative claim scores, process version, or other harness-owned stamps are supplied.
