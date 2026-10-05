# Evaluation: gemini-baseline

## Outcome and numerical scores

The cert-stage outcome is **denied**, actual_granted **0**, resolved **October 5, 2026**. gemini-baseline predicts **denied** at P(any grant) **0.001**: correct **1**, Brier **0.000001**. The provisioned October 5 snapshot confirms the resolution; it is not substituted for the predictor's September 16 information set.

The frozen prediction context is **baseline / sal-v4 / Term 2025**. The matching committed statpack's bracketed reached rates supply the proper **risk_set** baseline. Pooling all displayed Terms strictly before 2025 gives: 2024, 5.7% with n=1271; 2023, 5.9% with n=1312; 2022, 5.8% with n=1192; 2021, 5.6% with n=1500; 2020, 4.5% with n=1739; 2019, 4.6% with n=1399; 2018, 4.6% with n=1524; 2017, 4.7% with n=1643. The weighted numerator **592.925** divided by weighted denominator **11,580** yields **0.05120250431778929**. This is an approximation from rounded denial-reweighted percentages, not a reconstructed integer grant count. The table renders 10 of 10 Terms; 2025 and 2026 are excluded. No fresh corpus query or pull vintage was obtained, and this baseline describes the committed table only.

Brier skill is **1 - 0.000001 / 0.05120250431778929^2 = 0.9996185675879428**. The candidate's own 3.9% anchor is not substituted for the contract's prior-Term baseline. Excellent single-denial Brier performance does not independently establish calibration or soundness.

## Reasoning quality: 0.60

The rationale identifies relevant features: the unusual civil-appeal notice question, a pro se petition, the lack of a developed review-worthy conflict in its account, and a response waiver. A low grant estimate is consistent with the eventual denial. It does not invent a merits decision to justify that forecast.

There are important limits. First, the rationale explicitly anchors on **OT2025's 3.9%** reached rate, whereas this Term-2025 petition requires pooling **strictly prior** Terms. That is a baseline-selection error even though the frozen band and version themselves are valid. Because this prediction was forward, the error is not evidence that its future outcome was known.

Second, the explanation is thin relative to its 0.1% confidence. It does not explain the scale of the downward adjustment or distinguish the underlying tort dismissal from dismissal of the later appeal as untimely. It makes broad assertions about what the petition alleges without showing a petition-text read in the visible log: the QP, snapshot, and document manifest were requested, but petition.txt was not. The claim that a waiver confirms lack of viability is stronger than the record alone supports; the snapshot identifies a waiver by the insurer and adjuster, not a substantive response to the federal theory. The constitutional issue is summarized rather than closely tested against the procedural history.

The denial confirms the label, not these causal or categorical assertions. The score therefore gives credit for directionally relevant analysis without letting the smallest correct-denial probability substitute for evidentiary depth.

## Leakage and retrieval discrepancy

The log identifies **forward** mode. Its calls run on September 16, before the October 5 resolution. Result-capture coverage is **0.0**, which is an observability limit, not a defect by itself. Null result dates cannot establish that nothing was found.

At 21:47:52Z the log records `fedcourts query --court scotus --decided-before 2026-09-16 --limit 5 --full`. The candidate's retrieval.md instead reports no retrieval beyond provisioned inputs and the statpack. The query's result, success, transfer volume, and any opinion hydration are unobserved, so neither successful retrieval nor an empty/failed result is established. I flag the omitted query durably. Its pre-resolution date filter and the absence of outcome-presupposing prose do not support an inference of this case's outcome leaking. Thus retrieved_outcome_material is **false** on the observed evidence, influenced_prediction **not_applicable**, and leakage_suspected **false**; this is not a certification of unseen results.

The independent stakes score is **0.12**, formed from the QPs and outcome before inspecting candidate stakes numbers. A potentially broader notice rule is presented through a narrow Wisconsin procedural dispute that ended without a substantive ruling.

Only reasoning.md is qualitatively scored. The forecast and structured quantitative claims remain ungraded here. Cert votes and semantic propositions are not scored on this stage, and harness-owned stamps are omitted.
