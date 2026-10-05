# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage evaluation of the blinded prediction from run 20260917T181231Z. The supplied outcome records denial on October 5, 2026, with actual_granted = 0. The predicted label was denied, so correct = 1. With P(grant) = 0.018, Brier = (0.018 - 0)^2 = 0.000324.

The prediction froze baseline under sal-v4 and Term 2025. The matching committed statpack heading is sal-v4; I use the baseline column's bracketed reached rates, not its terminal rates or the evaluator's terminal context. Prior-Term inputs (Term: rate, weighted n) are 2024: 5.7%, 1271; 2023: 5.9%, 1312; 2022: 5.8%, 1192; 2021: 5.6%, 1500; 2020: 4.5%, 1739; 2019: 4.6%, 1399; 2018: 4.6%, 1524; 2017: 4.7%, 1643. Their resolved-weighted mean is 0.05120250431778929 over n = 11,580. This calculation uses displayed, rounded percentages and is approximate; it does not copy the candidate's exact JSON-derived rate. The caption renders all 10 of 10 Terms, of which eight precede 2025; no rendered-window omission requires a flag. Terms 2025 and 2026 are excluded despite the outcome's 2026 date. Basis = risk_set; skill = 1 - 0.000324 / baseline^2 = 0.8764158984934738.

These are committed live/historical-slice, denial-reweighted estimates, not a newly refreshed corpus measurement. No corpus blob was queried, and the consulted Markdown supplies no corpus-wide freshness timestamp. The prediction's frozen snapshot date is September 16, 2026. A favorable score on this single denial does not establish calibration or aggregate forecasting skill.

## Reasoning quality: 0.92

The rationale carefully separates the constitutional concern from whether this record presents it cleanly. Its strongest feature is its treatment of competing factual characterizations: the opposition's reproduced appellate opinion, paragraphs 30–34, actually discusses financial testimony, credibility, employment choices and an ability-to-pay conclusion. Paragraph 42 preserves an inability-to-pay defense to incarceration. The candidate recognizes those passages without treating earning capacity as necessarily equivalent to present ability to satisfy the purge conditions. It also distinguishes counsel submitting a proposed incarceration order from counsel independently exercising judicial power.

The preservation and alleged-conflict analysis is appropriately conditional. It acknowledges that not every lower-court submission was available and separates disputes over state law from a clean disagreement on the same federal question. It identifies its historical-authority check and explains its limits rather than asserting that the cited precedent mechanically resolves this petition. The statistical anchor is matched to the frozen band and Term, and the downward adjustment is candidly subjective. The remaining limitation is that the exact 1.8% adjustment has no demonstrated calibration or fitted justification. The denial is consistent with the assessment, but outcome.json supplies no explanation establishing that the Court adopted any of these reasons.

Only reasoning.md is graded. The forecast document was read for context, not scored; quantitative claims remain for the harness. No cert vote accuracy, semantic grades or judgment score is supplied. The optional independent significance assessment is omitted.

## Leakage

The captured log marks this a forward prediction. Its September 17 timestamp precedes the October 5 resolution. All 30 call rows were reviewed: local case reads target the provisioned materials, and external lookups target historical Turner authority. Capture coverage is 90%; the three web results are unobserved, not proven empty or failed. Their queries do not seek this petition or its subsequent history. Neither the log nor the rationale shows this case's own disposition being known. Thus retrieved_outcome_material = false, influenced_prediction = not_applicable and leakage_suspected = false. The historical state-court denial discussed in the rationale is not the SCOTUS disposition being scored.
