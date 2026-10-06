# Evaluation: claude-baseline

## Outcome and quantitative scores

This cert-stage prediction, run 20260917T181231Z, calls denied. The supplied outcome records denied on October 5, 2026, and actual_granted = 0. Thus correct = 1 and Brier = (0.015 - 0)^2 = 0.000225.

The prediction's frozen context is baseline, sal-v4, Term 2025. The committed sal-v4 table's bracketed reached rates supply a risk_set baseline. I pool the following displayed prior-Term rate/n pairs: 2024 5.7%/1271, 2023 5.9%/1312, 2022 5.8%/1192, 2021 5.6%/1500, 2020 4.5%/1739, 2019 4.6%/1399, 2018 4.6%/1524 and 2017 4.7%/1643. The resolved-weighted mean is 0.05120250431778929 over n = 11,580. Because the printed percentages are rounded, this is an approximate baseline. Skill = 1 - 0.000225 / baseline^2 = 0.9141777072871346. The table renders 10 of 10 Terms; all eight preceding 2025 are used, and 2025–2026 are excluded. No band is re-derived from the resolved docket and no terminal rate is substituted.

The statistics are the committed live/historical-slice, denial-reweighted estimates. I did not query or refresh a corpus blob; the consulted Markdown provides no corpus-wide freshness timestamp. The candidate's frozen snapshot is dated September 16, 2026. Single-case positive skill is not an aggregate performance or calibration finding.

## Reasoning quality: 0.85

The rationale gives a concrete explanation for discounting the matched prior: potential failure to present the federal issue below, disputed ability-to-pay facts, the suspended sanction, and an asserted split involving materially different state-law or enforcement contexts. The supplied opposition's preservation discussion and its reproduced appellate paragraphs 30–34 and 42 support these as genuine vehicle concerns. The candidate does not merely infer denial from the subject being family law, and it acknowledges the constitutional interest and its reliance on reproduced materials.

Some language is stronger than the available record warrants. Calling nonpreservation decisive and saying the federal claim first appeared at a particular stage risks treating an incomplete procedural record as conclusive, although the uncertainty section partially corrects this. The inference about counsel's Supreme Court experience from small-firm representation is weakly substantiated. General assertions about petition quality and long-conference behavior also receive little support. The 1.5% adjustment is reasoned but not quantitatively calibrated. These limitations reduce the analysis score independently of its correct outcome label and low Brier loss.

The supplied denial does not identify the Court's rationale and cannot establish that the proposed preservation or vehicle explanations were its actual reasons. This score grades reasoning.md alone. The forecast document and quantitative claims are not independently scored; claim_scores belongs to the harness. Cert votes are never scored, and no merits semantic or judgment grades apply. The optional independent significance assessment is omitted.

## Leakage

The log labels this forward and contains 25 calls with 100% capture coverage. The September 17 forecast precedes the October 5 resolution. The case-specific reads are provisioned inputs; the logged corpus query asks for eight recent granted SCOTUS matters without naming this petition. Its retrieval note says the results were unrelated and did not change the forecast. No web lookup, target-outcome search, or rationale reading this petition's disposition as already known appears. The record therefore supports retrieved_outcome_material = false, influenced_prediction = not_applicable and leakage_suspected = false. Null extracted document dates are not treated as independent proof that the returned material was empty.
