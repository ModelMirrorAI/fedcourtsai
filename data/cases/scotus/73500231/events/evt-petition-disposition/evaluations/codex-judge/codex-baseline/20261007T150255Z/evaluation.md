# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage evaluation of prediction run `20260917T181231Z`. The supplied `outcome.json` records `denied`, `actual_granted = 0`, resolved October 5, 2026; the provisioned October 5 snapshot independently contains “Petition DENIED.” The forecast's `denied` label matches exactly: **correct = 1**. With P(grant) = 0.004, **Brier = (0.004 - 0)^2 = 0.000016**.

The prediction freezes docket Term 2025, band `baseline`, version `sal-v4`. The committed `metrics/statpack.md` band heading matches, so the baseline uses **risk_set**, not the terminal rate or the evaluator's decided-docket context. Pool the displayed baseline reached rows strictly before Term 2025: 2024 5.7%/1,271; 2023 5.9%/1,312; 2022 5.8%/1,192; 2021 5.6%/1,500; 2020 4.5%/1,739; 2019 4.6%/1,399; 2018 4.6%/1,524; 2017 4.7%/1,643. The weighted denominator is 11,580 and the weighted rate is **0.05120250431778929**. These are denial-reweighted, paid-segment live/historical-slice estimates calculated from rounded displayed percentages, not reconstructed exact grant counts. Terms 2025 and 2026 are excluded despite the 2026 resolution date. The caption renders 10 of 10 Terms, so no hidden-window divergence is indicated.

Baseline Brier is 0.002621696448413231; **skill = 1 - 0.000016 / baseline Brier = 0.9938970814070851**. This is a single-event score, not evidence of cohort calibration. Source vintage is the committed pack supplied to this cell and the October 5 case snapshot; no live corpus refresh or corpus-wide freshness claim is made.

## Reasoning quality: 0.90

The rationale connects its downward adjustment to this petition's preclusion theory, repeated employment litigation, response waiver and lack of demonstrated doctrinal conflict rather than treating pro se status alone as dispositive. It carefully distinguishes an alleged conflict with precedent from a developed conflict between appellate rules. The supplied petition's questions and reasons-for-granting sections support that characterization of the petition's argument.

The rationale identifies what its historical-authority checks reportedly established, gives pinpoint locations, and acknowledges that it did not independently inspect the lower-court appendix. The captured log supports that those historical-authority lookups occurred; this evaluator did not independently retrieve their full texts. Particularly useful safeguards are the distinction between the separate injunction denial and cert disposition, the distinction between one summer distribution and a relist, and the explicit limits on what the absent appendix could establish. It also recovered the incomplete questions extract from the full petition. These are substantive evidence-handling strengths, not credit merely for a correct outcome or for making tool calls.

The remaining limitation is that moving from a roughly 5.12% heterogeneous band prior to 0.4% is judgmental: the rationale supplies no estimated conditional frequency for this combination of case features. The underlying court and administrative records also remain unverified. Those limits keep the score below perfect. The bare denial resolves the forecast label but does not establish that the Court adopted the candidate's legal explanation.

## Leakage and scope

The harness log identifies **forward** mode; calls occurred September 17, before this petition's October 5 resolution. The log and prose reveal no already-decided cert outcome. Historical-authority and general-rules queries do not seek this petition's disposition. Capture coverage is 0.9: three web rows are **unobserved**, so their null dates/digests do not prove failure or empty results. Their query content, the observed historical lookups and the rationale support `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. The provisioned July 16 injunction denial is a different event and is not cert leakage.

I read the forecast document only for context and did not grade it or the quantitative claims. No semantic set is scored on this cert event, and individual cert votes are not scored. No independent big-case assessment was formed before reading the candidates, so that optional field is omitted. The cell-level flag records the questions-extract defect; it does not block scoring.
