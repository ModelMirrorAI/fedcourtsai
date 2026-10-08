# Evaluation: gemini-baseline

## Outcome and quantitative scores

The event is cert-stage. The ground truth is `denied` on October 5, 2026, with `actual_granted = 0`. The candidate's exact disposition matches, giving **correct = 1**. At grant probability **0.01**, its Brier loss is **0.0001**.

The prediction's own frozen context supplies Term **2025**, band **baseline**, and **sal-v4**, matching the committed table. I pool all displayed prior-Term bracketed reached rates, 2017–2024, using their weighted resolved denominators: 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643, respectively in descending Term order. The denominator is **11,580**; multiplication of the rounded published rates gives **592.925** grant-family equivalents. The resulting `risk_set` baseline is **0.05120250431778929**. Skill is `1 - 0.0001 / baseline^2` = **0.961856758794282**.

The table renders all ten of ten Terms, so no window truncation needs a flag. The case's own Term and 2026 are excluded. The evaluator's current context does not supply the band. The candidate's rough 5.5% anchor is somewhat high relative to the rendered strictly-prior pool and is not accompanied by a calculation. This is a committed-table estimate, not a refreshed corpus claim; I made no corpus query and cannot certify remote freshness. A favorable single-cell skill value does not establish aggregate forecast skill.

## Reasoning quality: 0.65

The short rationale makes a coherent downward adjustment based on self-representation, the response waiver, and the absence of a demonstrated vehicle-worthy conflict. It identifies the petition's two main subjects rather than treating every section 1983 petition identically. These observations are relevant to the forecast, and the categorical denial is correct.

Its limitations are substantive rather than simply its length. It asserts that no vehicle-worthy split is indicated without examining the split presentation or the authorities offered for it. It does not analyze the multiple asserted grounds below, preservation, or the possibility that a favorable jurisdictional ruling would leave other grounds intact. It omits the important evidentiary qualification that the petition is one-sided and the lower-court appendix was not provisioned. The quoted base rate is approximate without a pooling calculation, and the choice of 1% rather than another low probability is not developed. These omissions make the analysis reasonable but only moderately supported.

The outcome does not identify the Court's reasons for denial. The reasoning-quality score therefore does not treat denial as confirmation of the doctrinal assertions. I read the forecast document but did not score it or import its subsidiary predictions into reasoning quality. Quantitative claims are harness-owned; votes and semantic grades are not scored on this cert event.

## Leakage

The harness labels the prediction **forward**. Its **23 calls** are all marked **unobserved**, giving result-capture coverage **0.0**. This is a telemetry limitation, not a defect, and I do not construe null document dates or absent result digests as failed or empty retrievals.

The query slices show provisioned-input reads, a statpack read, schema/contract reads, and output or validation operations on September 16, 2026. They do not request the target's later docket, disposition, or an outcome-bearing source. The reasoning contains no target resolution and remains a prospective low-probability assessment. There is no positive evidence of a decided case mis-provisioned forward before the October 5 denial. Thus `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, supported by queries and prose rather than a claim to have inspected uncaptured results.
