# Evaluation: codex-baseline

## Result and reasoning quality

The candidate forecast denial with P(grant) = 0.06: `correct = 1`, Brier = 0.0036, and skill = -0.37315668340584676. Its probability was slightly above the matched baseline, so it scores worse than that baseline on this realized denial despite getting the modal label right. That single-case comparison is not a general performance claim.

Reasoning quality: **0.91**. The analysis distinguishes the petition's asserted conflict from the actual reasoning of the appended Sixth Circuit decision. The provisioned petition's Appendix A, pp. 21a–26a, supports the candidate's important vehicle qualifications: the district court had not supplied a harmlessness determination; the panel assumed the most stringent burden; and it considered both the limited connection of the extraneous material to Maund and the other evidence. The candidate also explains why a reported deliberation-focused jury-tampering precedent need not establish a clean conflict for inadvertently supplied exhibits. This is substantive discrimination rather than treating the petition's advocacy as settled law.

Its use of the frozen reached baseline is sound. The cited unrounded 593/11,580 anchor is very slightly different from my rendered-percentage calculation; the difference is rounding, not a different band or Term window. The modest upward adjustment for the asserted conflict is explained alongside the waiver and lack of additional attention. The precise 6% adjustment remains judgmental rather than empirically estimated, and only one contrasting authority was checked; these limit the score without making the rationale unsound. The candidate explicitly recognizes document truncation, incomplete authority verification, and the difference between elapsed summer time and a relist.

## Leakage assessment

The captured log records `forward`, with September 17, 2026 calls, before the October 5 denial. Its 30 rows have 28 captured results and two unobserved web-search results (coverage 0.9333333333333333). The visible web queries concern historical Olano doctrine, not this petition's outcome. The unobserved markers do not prove the searches returned nothing; the candidate's account of unusable results is self-report, not a captured-result finding. The historical Dutkel lookup, local petition reads and statpack reads do not show this case's Supreme Court disposition being retrieved or presumed.

No evidence of outcome-revealing retrieval or a decided case mis-provisioned as forward appears in the log or reasoning. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. The lower-court judgment is pre-cert evidence, not the event's outcome.

## Scoring basis

This is a cert-stage petition-disposition cell. The committed outcome records denial on October 5, 2026, with `actual_granted = 0`; it does not supply the Court's substantive reasons. Correctness is the exact disposition-label match, and Brier is the square of the stated grant probability. A correct denial forecast does not establish that the Court adopted the predictor's legal rationale.

The scored prediction freezes Term 2025, band `baseline`, and `salience_version = sal-v4`. The rendered `metrics/statpack.md` table has the matching sal-v4 heading. I use its bracketed reached rates, not terminal rates or the evaluator's decided-docket context. The pooled rows are OT2024 5.7%/1,271; OT2023 5.9%/1,312; OT2022 5.8%/1,192; OT2021 5.6%/1,500; OT2020 4.5%/1,739; OT2019 4.6%/1,399; OT2018 4.6%/1,524; OT2017 4.7%/1,643. These are denial-reweighted live/historical-slice estimates, not a census grant rate.

The resolved-weighted calculation from the displayed, rounded percentages is 592.925 / 11,580 = 0.05120250431778929, with `base_rate_basis = risk_set`. The fractional numerator is a weighted calculation from rounded rates, not an observed grant count. OT2025 and OT2026 are excluded. The caption renders 10 of 10 available Terms, so there is no rendered-window truncation to flag. This describes the provisioned committed statpack, not a fresh corpus query. Skill is `1 - Brier / baseline^2` for this denial.

Only `reasoning.md` is graded for reasoning quality. I read the pointed-to forecast document for context, but do not grade its predictions or the quantitative claims. Claim scores and provenance stamps remain the harness's. No vote accuracy or semantic grades are written on this cert-stage cell. I omit the optional independent stakes assessment rather than form one after viewing candidates' stakes scores.
