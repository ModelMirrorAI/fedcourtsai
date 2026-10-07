# Evaluation: gemini-baseline

## Result and baseline

The blinded prediction from run 20260918T174135Z is a cert-stage denied call at P(grant) = 0.02. The supplied outcome records denied on October 5, 2026, with actual_granted = 0. Correct = 1 and Brier = (0.02 - 0)^2 = 0.0004.

The baseline uses the prediction's frozen baseline band, sal-v4, Term 2025, not the evaluator's terminal context. The matching sal-v4 table in metrics/statpack.md supplies these strictly-prior reached rates and weighted denominators for 2024 back through 2017: 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, 4.7%/1643. Pooling the printed rounded rates gives 592.925 / 11,580 = 0.05120250431778929, with base_rate_basis = risk_set. The numerator is a weighted estimate, not an integer count. The caption shows all 10 of 10 Terms; every displayed row earlier than 2025 is included, and 2025–2026 are excluded. There is no rendered-window mismatch. This is the committed denial-reweighted live/historical-slice baseline, not a fresh corpus query. Brier skill = 1 - 0.0004 / baseline^2 = 0.8474270351771281. A favorable single-case comparison does not establish calibration.

## Reasoning quality: 0.72

The rationale gives a coherent account of why a petition emphasizing disputed factual treatment and an incompletely demonstrated circuit conflict should sit below the approximately 5.1% risk-set anchor. It connects the low grant probability to the case's review posture rather than simply repeating a denial base rate. This is a sound direction of adjustment, and the actual denial is consistent with it.

The analysis is nevertheless thin on the potentially reviewworthy statutory issue. The supplied petition's pages 9–11 advance an argument about contractual benefits and discriminatory service, while appendix pages 5a–7a make the scope of protected contractual activity central to the panel's decision. The rationale largely labels the matter factual error correction without explaining the panel's recognition of benefits beyond a completed meal, its severe-harassment formulation, or why the competing circuit approaches would not change this case's outcome. It asserts the absence of a clear split without a developed comparison. The reduction from about 5.1% to 2% is plausible but judgmental, not an empirically fitted adjustment. These are evidentiary and analytical limitations, not penalties for brevity. The denial supplies no explanation proving the candidate's proposed reasons were the Court's reasons.

## Leakage and scope

The harness log says forward. All 23 calls are dated September 18, before October 5, but none has an observed result. I assess the queries and prose rather than treating missing dates or digests as clean search returns. The corpus query for this docket and MCP search for docket 25-1340 were permissible while the petition was pending. No visible query or passage reports its disposition as already known. Accordingly, retrieved_outcome_material = false is a no-affirmative-evidence assessment, not a certification of unseen result bytes; influenced_prediction = not_applicable and leakage_suspected = false. Zero result capture is a telemetry limitation, not a candidate fault or a leakage finding.

The forecast document and structured claim probabilities are not scored here and do not alter reasoning_quality. Vote accuracy and semantic grades are inapplicable to this cert cell. No independent big_case grade is supplied. The cell-level filing-date discrepancy is disclosed in flags.json without inferring untimeliness or changing the numerical scores.
