# Evaluation: claude-baseline

## Result and reasoning quality

The candidate forecast denial with P(grant) = 0.035: `correct = 1`, Brier = 0.001225, and skill = 0.5327452952299549. Its downward adjustment beats the matched baseline on this realized denial; this is a descriptive single-cell comparison, not evidence of general forecasting skill.

Reasoning quality: **0.80**. The analysis uses the correct frozen salience-band risk set and prior-Term window, then distinguishes an asserted legal conflict from case-specific harmless-error application. The provisioned Appendix A, pp. 21a–26a, supports its concern that the Sixth Circuit assumed the demanding burden and relied on a fact-bound harmlessness analysis. It gives the waiver and absence of a response request weight without treating a future request as impossible, and explains how such a request would change the probability. Its explicit admissions that external verification failed and that the appended opinion was only partly read appropriately qualify its claims.

The limitations are material but not fatal. Calling the split 'real' is stronger than the independently verified evidence supports. The negative adjustment based on the law firm's supposed lack of repeat Supreme Court practice is not substantiated by the supplied analysis or a matched empirical rate. The inferred identities and effect of companion petitions remain speculative even though the uncertainty section acknowledges them. The long summer interval without a response request is also not equivalent to repeated Court consideration. These weaknesses reduce the analysis score independently of the favorable realized Brier. The candidate reports that broad corpus queries returned mostly irrelevant applications and did not move its estimate; that is appropriately not presented as supporting evidence.

## Leakage assessment

The log records `forward`; all 29 rows are captured (coverage 1.0). Calls occurred September 17, 2026, before the October 5 denial. The case-caption and docket-number MCP searches are expressly marked `throttled`, supporting the account that those calls did not retrieve live docket material. The broad corpus-query row carries a September 10 retrieved-document date, earlier than this event's resolution; the candidate describes unrelated grants and denials rather than its own petition's disposition. Ordinary current-docket searches were permissible while this forward event was genuinely unresolved.

Neither the log nor the rationale shows this case's Supreme Court denial surfacing before prediction. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. The clean assessment rests on the visible calls, timing and reasoning, not on the absence of candidate flags, which are not staged.

## Scoring basis

This is a cert-stage petition-disposition cell. The committed outcome records denial on October 5, 2026, with `actual_granted = 0`; it does not supply the Court's substantive reasons. Correctness is the exact disposition-label match, and Brier is the square of the stated grant probability. A correct denial forecast does not establish that the Court adopted the predictor's legal rationale.

The scored prediction freezes Term 2025, band `baseline`, and `salience_version = sal-v4`. The rendered `metrics/statpack.md` table has the matching sal-v4 heading. I use its bracketed reached rates, not terminal rates or the evaluator's decided-docket context. The pooled rows are OT2024 5.7%/1,271; OT2023 5.9%/1,312; OT2022 5.8%/1,192; OT2021 5.6%/1,500; OT2020 4.5%/1,739; OT2019 4.6%/1,399; OT2018 4.6%/1,524; OT2017 4.7%/1,643. These are denial-reweighted live/historical-slice estimates, not a census grant rate.

The resolved-weighted calculation from the displayed, rounded percentages is 592.925 / 11,580 = 0.05120250431778929, with `base_rate_basis = risk_set`. The fractional numerator is a weighted calculation from rounded rates, not an observed grant count. OT2025 and OT2026 are excluded. The caption renders 10 of 10 available Terms, so there is no rendered-window truncation to flag. This describes the provisioned committed statpack, not a fresh corpus query. Skill is `1 - Brier / baseline^2` for this denial.

Only `reasoning.md` is graded for reasoning quality. I read the pointed-to forecast document for context, but do not grade its predictions or the quantitative claims. Claim scores and provenance stamps remain the harness's. No vote accuracy or semantic grades are written on this cert-stage cell. I omit the optional independent stakes assessment rather than form one after viewing candidates' stakes scores.
