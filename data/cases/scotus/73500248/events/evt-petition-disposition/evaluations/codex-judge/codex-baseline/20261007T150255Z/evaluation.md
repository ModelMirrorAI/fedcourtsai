# Evaluation: codex-baseline

## Outcome and quantitative scores

The event is **cert-stage**. The provisioned `outcome.json` records denial on **October 5, 2026**, with `actual_granted = 0`. The candidate's `denied` label is correct, so **correct = 1**. Its P(any grant) of **0.025** produces **Brier = (0.025 - 0)^2 = 0.000625**. A denial establishes no substantive holding on the proposed statutory interpretation.

The baseline is selected from the prediction's frozen **baseline / sal-v4 / Term 2025** context, not the decided docket's evaluation context. The committed statpack heading matches that version. I use the bracketed reached rates for all displayed Terms strictly before 2025: 2017 **4.7%, n=1,643**; 2018 **4.6%, n=1,524**; 2019 **4.6%, n=1,399**; 2020 **4.5%, n=1,739**; 2021 **5.6%, n=1,500**; 2022 **5.8%, n=1,192**; 2023 **5.9%, n=1,312**; 2024 **5.7%, n=1,271**. This gives **592.925 / 11,580 = 0.05120250431778929**, with `base_rate_basis = risk_set`. The numerator is reconstructed from rounded displayed percentages, not an observed integer grant count. The pack describes denial-reweighted paid-segment live/historical-slice estimates.

The table renders ten of ten pack Terms; only eight precede this case's Term. There is no truncated-window or version mismatch to flag. The predictor reports using corresponding exact machine-readable counts, **593 / 11,580**, while this evaluation follows the rendered Markdown rates. The tiny rounding difference is not a calibration error. No exact-count file was consulted by this evaluator. The skill calculation is **1 - 0.000625 / 0.05120250431778929^2 = 0.7616047424642627**. This single-event skill value does not establish aggregate forecasting ability.

## Reasoning quality: 0.94

The rationale is carefully grounded and discriminating. It separates the broad attack on the 150% cap from conflicts concerning appellate work, pre-incarceration conduct, and nonmonetary relief. It explains why the latter do not create a conflict over this trial-fee award. The provisioned petition's Appendix A, pages 4a–5a, supports the key premise: the panel was bound by circuit precedent and described agreement among the circuits. The rationale also recognizes the opposing considerations—a preserved, discrete legal question, a consequential fee reduction, and a nonfrivolous textual objection—rather than making uniform precedent conclusive.

The candidate treats the waiver and absence of a response request as missing affirmative signals, not proof that the respondent agrees or that denial is compelled. Its discussion of Murphy distinguishes the allocation issue from a direct holding on the challenged cap; this appropriately limits what that cited authority is claimed to establish. I assess that limitation as expressed in the rationale and have not fetched Murphy anew. The explanation connects a strictly prior risk-set anchor to a judgmental downward adjustment, identifies broader marginal tables as contextual rather than forward transition probabilities, and states the limits of its snapshot and absent opposition.

The remaining limitation is quantification: the move from approximately 5.12% to 2.5% is judgmental and not estimated from a matched conditional sample. The candidate openly acknowledges this, so it warrants a modest reservation rather than a large penalty. The quality score concerns the analysis, not its correct outcome label or the success of any ancillary forecast.

## Leakage and scope

The harness records **forward** mode and 28 calls on September 17, before the October 5 resolution. Capture coverage is **26/28 = 0.9285714285714286**. The two unobserved web-search calls concern Murphy and the statutory provision. Their missing dates or digests do not establish empty results; the retrieval note's assertion of no usable content remains a self-report. The other query slices show provisioned-record reading, calibration work, and citation/snippet retrieval about the 2018 authority. No query or rationale reveals this petition's subsequent Supreme Court disposition.

The rationale expressly distinguishes the appended lower-court affirmance from the event being predicted. The evaluator's October 5 snapshot is not treated as the predictor's September 17 baseline. On the log and prose, `retrieved_outcome_material = false`, influence is `not_applicable`, and `leakage_suspected = false`.

Only `reasoning.md` receives a reasoning-quality grade. The forecast document is contextual, quantitative claims remain for the harness, and no cert votes or semantic grades are scored. Harness-owned fields are omitted. The committed pack, not a newly queried remote corpus, supplies the evaluation baseline; no independent corpus-freshness claim is made.
