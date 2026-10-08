# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage evaluation of the blinded prediction from run `20260916T170237Z`. The authoritative outcome records `denied`, `actual_granted = 0`, and resolution on October 5, 2026, corroborated by the provisioned October 5 snapshot. The predicted label matches: **correct = 1**. P(any grant) = 0.07 gives **Brier = 0.0049**.

The prediction froze Term 2025, band `baseline`, and version `sal-v4`, matching the committed statpack's band table. Use the bracketed `reached` population with **base-rate basis = risk_set**, not the terminal population or the evaluator's current context. All displayed Terms strictly before 2025 are 2017–2024. Their rounded rate/weighted-n pairs are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Weighting yields 592.925 / 11,580 = **0.05120250431778929**. This is an approximate rate derived from printed percentages, not an exact observed integer numerator. The table reports 10 of 10 Terms shown, so excluding 2025–2026 leaves no rendered-window discrepancy.

The baseline squared error is approximately 0.002621696448413231. Therefore **Brier skill = -0.8690188190801803**. The denial forecast is correct, but 7% was farther from the realized binary zero than the baseline. This one-event result does not demonstrate poor calibration or invalidate the legal analysis. The calculation uses the committed pack, not a refreshed remote corpus; no assertion of current corpus-wide freshness is made.

## Reasoning quality: 0.92

The rationale is careful about both its population and its evidence. It reconstructs the correct prior-Term reached-band anchor and avoids treating terminal relist rates as forward transition probabilities or independent multipliers. It distinguishes allegations accepted at the pleading stage from trial findings, and it separates the assumed constitutional violation from the clearly-established-law inquiry.

Its vehicle analysis is especially strong. The panel's reliance on the obvious-clarity method is documented at petition appendix 10a. The rationale nevertheless recognizes that the appellate brief invoked Lewis and intentional misuse, rather than treating respondent's preservation objection as a conclusively established forfeiture. The reproduced brief at opposition appendix 19a supports that qualification. It also identifies the unresolved color-of-state-law issue, supported by the concurrence at petition appendix 15a, as a separate obstacle. The missing reply is properly treated as missing evidence, not as proof that no answer existed.

The rationale considers the contrary pull of a divided opinion and arguable inter-circuit tension while explaining why serious allegations alone need not make an attractive certiorari vehicle. Its authority-verification queries are documented in the staged log and retrieval note. The score reflects the reasoning's distinctions and evidentiary discipline, not a new adjudication of the cited precedents. The main limitation is quantitative: the net increase from about 5.12% to 7% is judgmental, and the record does not provide an empirical estimate for how much weight each factor should receive. The denial does not reveal the Court's actual reasons or establish which vehicle concern mattered.

The grade is confined to the headline probability rationale in `reasoning.md`. Ancillary quantitative claims and the separate forecast document are not independently scored or folded into reasoning quality. Cert-stage votes and semantic claims receive no grades; the harness handles mechanical claims. No optional big-case assessment is supplied.

## Leakage assessment

The harness marks the prediction forward. The September 16 run preceded the October 5 denial, and its reasoning consistently treats the event as pending. The 30-call log has 28 captured results and two unobserved web-search rows, for capture coverage 0.9333333333333333. The visible searches concern Lewis and intentional vehicle misuse; authority lookups concern Lewis and Browder, not the target disposition.

The candidate reports that web searches returned no usable results, but the two unobserved markers do not independently establish empty returns. They are assessed by their query scope, which does not seek the target outcome. The remaining queries concern provisioned inputs, the statpack, cited authorities, and operational tasks. No target disposition or post-resolution fact appears in the log or reasoning. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This does not rely on absent predictor flags or confuse the evaluator's October 5 snapshot with the predictor's earlier baseline.
