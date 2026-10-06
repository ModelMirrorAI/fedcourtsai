# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage disposition evaluation. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The provisioned October 5 snapshot independently contains the entry “Petition DENIED.” codex-baseline predicted denial with P(any grant) = 0.003 on September 17, 2026. Therefore `correct = 1` and Brier = `(0.003 - 0)^2 = 0.000009`.

The prediction freezes `baseline`, `sal-v4`, and docket Term 2025. The committed statpack's sal-v4 heading matches, so the baseline uses the bracketed **reached** rates, not terminal-band rates or the evaluator's decided-docket context. Its caption renders 10 of 10 Terms. All eight displayed Terms strictly before 2025 enter the pool: 2024 (5.7%, n=1271), 2023 (5.9%, 1312), 2022 (5.8%, 1192), 2021 (5.6%, 1500), 2020 (4.5%, 1739), 2019 (4.6%, 1399), 2018 (4.6%, 1524), and 2017 (4.7%, 1643). Terms 2025 and 2026 are excluded even though resolution occurred in 2026.

Resolved-weighting those displayed, rounded percentages gives 592.925 / 11580 = **0.05120250431778929**, with `base_rate_basis = risk_set`. The numerator is a weighted sum reconstructed from displayed percentages, not an observed integer count. Skill = `1 - 0.000009 / baseline^2 = 0.9965671082914854`. The candidate's reported unrounded JSON anchor, 593 / 11580, differs only by display rounding; I use the prompt-prescribed markdown surface rather than substitute its reported calculation. These are committed-pack estimates, not a claim about freshly queried corpus state. No corpus lookup or independent freshness check was made.

## Reasoning quality: 0.92

The rationale carefully distinguishes the petitioner's allegations from established facts. It identifies a weakly developed federal question, no demonstrated conflict, fact-intensive licensing allegations, and a possible appellate-record obstacle. The provisioned petition's sections V and VIII support the description of the disputed missing-record episode, but do not establish all jurisdictional consequences. codex-baseline appropriately treats preservation, finality, and an adequate independent state ground as uncertain without lower-court decisions. It also avoids interpreting absent response material as affirmative proof of a waiver or accepting the petition's medical and fiscal assertions.

The analysis correctly distinguishes the frozen risk-set anchor from terminal no-relist and no-CVSG cuts and labels its downward adjustment as judgmental. The remaining limitation is quantitative: the reduction from approximately 5.12% to 0.3% is not supported by a matched comparison set or calibrated adjustment model. The high grade rewards source discipline and appropriately qualified reasoning, not merely a correct denial. The denial does not establish that the Court adopted any proposed explanation.

## Leakage and scope

The harness log says forward; prediction preceded the supplied resolution. Its 27 calls have 24 captured results and three unobserved general-rule web requests. I do not infer those requests returned nothing from absent dates or digests. Their queries concern Court rules, while the remaining relevant calls concern provisioned inputs, aggregate statistics, and the official rules PDF. No visible query or reasoning passage reveals this petition's later disposition. Forward influence is `not_applicable`; leakage is not suspected.

The later evaluator snapshot is outcome evidence, not proof of what the predictor's earlier snapshot contained. The reported CourtListener caption discrepancy in claude-baseline's materials is flagged at cell level; it does not override this supplied event and outcome. The forecast document was read only for context. Quantitative claims are left to the harness; cert votes and semantic propositions are not scored. No independent big-case assessment is supplied.
