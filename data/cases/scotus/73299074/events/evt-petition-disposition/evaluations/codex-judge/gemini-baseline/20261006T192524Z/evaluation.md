# Evaluation: gemini-baseline

## Outcome and quantitative scores

The event is provisioned as cert-stage; the actual filing is an original mandamus petition. `outcome.json` records `denied`, `actual_granted = 0`, resolved October 5, 2026, consistent with the provisioned snapshot. The predicted `denied` label is correct: **correct = 1**. P(grant) = 0.005 gives **Brier = (0.005 - 0)^2 = 0.000025**.

The scored prediction's frozen context supplies Term 2025, `baseline`, and `sal-v4`, matching the committed `metrics/statpack.md` heading. I use its bracketed reached rates, not leading terminal rates or the evaluator's context. Prior-Term rate/weighted-denominator pairs are: 2024, 5.7%/1,271; 2023, 5.9%/1,312; 2022, 5.8%/1,192; 2021, 5.6%/1,500; 2020, 4.5%/1,739; 2019, 4.6%/1,399; 2018, 4.6%/1,524; 2017, 4.7%/1,643. Their resolved-weighted mean is **0.05120250431778929** over **11,580**, with **risk_set** basis. Published rates are rounded, so this is an approximate pooled rate. The table shows 10 of 10 available Terms; I exclude 2025 and 2026 and encounter no truncated-window divergence.

**Brier skill = 1 - 0.000025 / 0.05120250431778929^2 = 0.9904641896985705**. This is strong probability-score performance on this denial, not evidence that a 0.5% forecast is calibrated across cases. The mandated cert comparator is not an empirical mandamus baseline; the shared scope flag records that transportability problem. The calculation uses only the committed pack, without a claim of refreshed corpus state.

## Reasoning quality: 0.55

The concise rationale correctly identifies the writ form and explains why a generic cert grant rate should not be accepted without adjustment. It uses the first-distribution posture and recognizes that extraordinary relief should require something beyond ordinary review. Those are relevant reasons for a denial forecast, and it candidly says that it did not have provisioned filed-document text.

However, it does not analyze this petition's central mandate-enforcement theory or the competing readings of whether the prior judgment preserved a federal forum. The provisioned question presented shows why those omissions matter. A null lower-court metadata field is not independently sufficient to establish procedural history; the petition entry is the stronger evidence of the original-writ posture. The rationale mentions a terminal zero-relist bucket near 1.7% without explaining that a petition awaiting its first conference can later relist, making that bucket an imperfect forward comparator. The adjustment to 0.5% is not supported by a measured mandamus population or a case-specific assessment of alternatives and exceptional circumstances.

The correct label and very small Brier score do not cure those analytical gaps, and the bare denial does not validate an unstated legal theory. This grade applies only to `reasoning.md`, not the separate forecast or claims. The forecast was read as required but remains unscored; the harness owns claim scoring. Vote accuracy and semantic grading are inapplicable to this cert-stage event. I supply no independent big-case score.

## Leakage

The captured log's mode is **forward**. All 22 calls are timestamped September 16, 2026, preceding the October 5 resolution. Every call is marked **unobserved**, with result-capture coverage **0.0**. This is a telemetry limitation, not a defect or evidence that searches returned nothing. In particular, I cannot independently confirm the candidate's account that the corpus query failed or determine the exact material returned by the caption/docket search.

The visible queries target the provisioned September 16 snapshot, the committed statpack, prior resolved cases, and this pending case's caption/docket. The case search was permissible forward retrieval before the denial existed; the prose neither cites the later order nor presupposes an already-resolved petition. On that timing and the available query/prose evidence, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is not a claim that uncaptured results were inspected and found empty.
