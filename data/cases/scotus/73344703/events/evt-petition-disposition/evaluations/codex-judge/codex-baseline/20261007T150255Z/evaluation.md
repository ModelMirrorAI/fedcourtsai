# Evaluation: codex-baseline

## Result and numerical score

The cert-stage outcome records `denied`, `actual_granted = 0`, on October 5, 2026. The September 16 prediction names `denied`, so **correct = 1**. With P(any grant) = 0.01, **Brier = (0.01 - 0)^2 = 0.0001**. The result does not establish why the Court denied review or endorse the lower court's analysis.

The prediction's frozen baseline band, sal-v4 version, and Term 2025 match the committed statpack's sal-v4 table. I use its bracketed reached population, not the leading terminal rate and not the evaluator's decided-docket context. The strictly prior displayed rows, in Term order 2024 through 2017, are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643 (rate/weighted resolved n). Their weighted numerator is 592.925 and denominator 11,580, producing **segment base rate = 0.05120250431778929**, **base_rate_basis = risk_set**, and **Brier skill = 1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282**.

These are denial-reweighted private-petitioner risk-set estimates reconstructed from rounded displayed percentages, not exact raw-count frequencies. The table renders 10 of 10 Terms; removing the case's own 2025 Term and later 2026 leaves all eight eligible displayed rows. There is no narrower-rendered-window discrepancy. This single-event skill comparison is not a calibration or general-performance finding.

The source is the committed statpack supplied to this evaluation, not a live corpus refresh. The prediction froze a September 16 snapshot, while the evaluator's snapshot is named October 5. I made no corpus lookup or corpus-wide freshness measurement and make no claim about current corpus state.

## Reasoning quality: 0.92

The rationale clearly separates record facts, petition allegations, and unresolved vehicle questions. It gives a reproducible, strictly prior-Term reached-rate anchor and explains why this petition's fact-specific error-correction posture warrants a substantial downward adjustment. The supplied petition supports its distinction between correctly cited standards and alleged evidentiary misapplication, and its observation that the speech claim arises through a private tort dispute rather than a straightforward constitutional claim.

The discussion is careful about what the missing opposition and lower-court opinions prevent it from establishing. In particular, it treats finality and adequate-independent-state-ground concerns as unresolved rather than declaring jurisdictional defects from the petition alone. Its account of antecedent precedent distinguishes contextual reasoning from controlling holdings and does not equate federal summary-judgment examples with automatic entitlement to review of this state tort action. It also distinguishes absent visible attention signals from independently verified absence and terminal descriptive rates from forward hazards.

The remaining limitations are meaningful but modest: the exact reduction from approximately 5.12% to 1% is qualitative rather than empirically fitted, and the substantive vehicle analysis necessarily depends on one party's presentation. Denial does not prove every concern correct, and the favorable Brier result does not validate the precision of 1%. The quality score rewards the rationale's discipline and support, not merely the correct label, length, or number of tools used.

## Leakage assessment

The harness records forward mode, with all 36 calls on September 16, before the October 5 resolution. The recorded requests address provisioned files, the statpack, general Court rules, and older general precedents. No query seeks this petition's later disposition, and the reasoning does not read the result from its baseline. There is no evidence of an already-decided case routed forward. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

The log captures 31 of 36 results. Five web-call results are unobserved; the candidate reports no usable content, but the log cannot independently prove those calls were empty or failed. Their recorded targets concern general rules rather than this case. Collapsed `other` tool labels are not suspicious in themselves. A logged instruction-file search explicitly excludes the prohibited labeling-artifact path; that exclusion is not a read of it. The assessment rests on timing, query content, and the reasoning, not on missing predictor flags or null document dates.

## Unscored fields

The pointed-to forecast document was read for context but not scored. The reasoning-quality assessment excludes the separate forecast and the mechanical or semantic propositions as graded objects. Mechanical claims remain harness-owned; cert votes and semantic claims receive no evaluator score on this stage. No harness-owned stamps are written.
