# Evaluation: gemini-baseline

## Outcome and numerical score

This is a cert-stage petition disposition. The supplied outcome records denial on October 5, 2026, with actual_granted = 0. The candidate predicted denied with P(any grant) = 0.001: correct = 1 and Brier = (0.001 - 0)^2 = 0.000001. A single correct denial does not establish calibration.

The prediction freezes baseline under sal-v4 and Term 2026. The matching sal-v4 table in metrics/statpack.md supplies the bracketed reached rates, not the leading terminal rates. Pooling every displayed strictly prior Term (2017–2025) gives sum(rate * weighted resolved) = 637.385 and weighted resolved = 12,720; the risk-set baseline is 0.05010888364779874. The numerator is reconstructed from rounded displayed percentages, not an observed integer grant count. The table renders 10 of 10 Terms, including the excluded 2026 row, so there is no hidden-window divergence. Skill is 1 - 0.000001 / baseline^2 = 0.9996017364641319. These are committed-pack calculations, not a live-corpus freshness claim.

## Reasoning quality: 0.72

The rationale identifies the three procedural complaints in the supplied questions presented and gives a coherent reason to move below the broad baseline: an individual dissolution dispute, fact-dependent alleged errors, and no demonstrated conflict. It does not confuse prediction accuracy with proof that the petition's allegations are false.

The analysis is comparatively thin on the strongest contrary possibility: an asserted procedural barrier to consideration of a preserved federal claim. The generic domestic-relations discussion does not closely test that contention or distinguish the petitioner's account from verified lower-court findings. The roughly 50-fold reduction from the segment anchor to 0.1% is judgmental, without subgroup evidence or a developed account of uncertainty from missing adverse materials. The outcome agrees with the forecast, but supplies no explanation validating those particular assumptions. The score assesses the rationale's analytical support, not its extremely small realized Brier loss.

## Leakage and scope

The log records forward mode and October 4 calls, preceding the October 5 resolution. Its queries show local input and aggregate-statpack reads rather than a search for this case's outcome; the prose does not presuppose a denial already entered. Result capture is 0.0: every result is unobserved, which is a telemetry limitation, not evidence that calls returned nothing. On the available query and reasoning evidence, retrieved_outcome_material is false and influence is not_applicable; leakage_suspected is false.

The forecast document was read for context only. Neither it nor the structured claims contributes to reasoning_quality; mechanical claim scoring belongs to the harness. Cert votes are not scored, and this stage declares no semantic grades. No independent big-case assessment is supplied because candidate significance judgments were already visible before an independent score was formed.
