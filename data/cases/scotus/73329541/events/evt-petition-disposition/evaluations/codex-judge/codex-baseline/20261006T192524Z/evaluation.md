# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage petition disposition, not a merits judgment. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. codex-baseline predicted `denied` with grant probability 0.04: exact-label correctness is **1**, and Brier loss is **(0.04 - 0)^2 = 0.0016**.

The prediction freezes Term 2025, band `baseline`, and salience version `sal-v4`. The committed statpack's matching table renders all 10 of its 10 Terms. Pooling only its bracketed baseline `reached` rates for Terms 2017–2024 gives weighted denominator **11,580** and weighted numerator **592.925**, calculated from the displayed rounded percentages. The resulting **risk-set baseline is 0.05120250431778929**, and skill against the realized denial is **0.38970814070851256**. Terms 2025 and 2026 are excluded. This uses the prediction's frozen band, not the evaluator's terminal context. The small difference from the candidate's 593/11,580 anchor reflects its use of unrounded JSON rates; it is not a substantive baseline error. These are committed-pack, denial-reweighted estimates, not a fresh corpus measurement. No corpus freshness claim is made.

## Reasoning quality: 0.90

The rationale is unusually careful about the distinction between an arguable statutory conflict and a suitable certiorari vehicle. It explains why the requested extension of Bowe is not automatic, distinguishes the subsection and custody-status arguments, and identifies the unpublished COA posture and unusual interstate-custody claim as obstacles. Its assessment of the split is qualified rather than copied wholesale from the petition. The staged retrieval account and log document targeted checks of the relevant authorities, while the reasoning expressly limits what was actually read.

The treatment of missing docket signals is appropriately conservative: no response or amicus appears in the available record, which is not the same as independently proving that none exists. The lower-court account is attributed to the petition, and the missing appendix and incomplete subsequent-treatment survey are disclosed. The modest adjustment from roughly 5.12% to 4% is intelligible, though still judgmental rather than empirically calibrated to comparable vehicles. That residual calibration uncertainty and the incomplete lower-court record prevent a near-perfect grade.

The realized denial is consistent with the prediction but supplies no stated doctrinal rationale; it does not prove that the Court adopted the candidate's statutory analysis. This quality score grades `reasoning.md` only. The forecast document was read for context, not scored, and neither its timing details nor the structured claims contribute to the grade.

## Leakage and scope

The log records forward mode. All 33 call records were reviewed: 30 have captured results and three web calls are unobserved. The candidate's statement that those searches returned nothing visible is not treated as proof of empty results. Their queries concern Bowe and other historical authority, not this petition's eventual denial. No query or staged prose shows the October 5 disposition surfacing during the September 16 forecast. Accordingly, outcome retrieval is assessed false, influence is `not_applicable`, and leakage is not suspected. Result digests are not complete result bodies, so this is an assessment of the staged audit evidence, not a claim of exhaustive visibility.

Cert votes are unscored, and the supplied outcome reports none. No semantic grades, claim scores, or harness-owned stamps are written. The optional stakes assessment is omitted rather than formed after seeing the candidate's own score.
