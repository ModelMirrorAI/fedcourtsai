# Evaluation: codex-baseline

## Outcome and quantitative scores

The provisioned outcome records denial on October 5, 2026, with actual_granted = 0. codex-baseline forecast denied with P(any grant) = 0.012. Thus correct = 1, Brier = 0.000144, and Brier skill = 0.945073732663766 against the pooled baseline below. The outcome has no observed votes and no merits judgment.

## Reasoning quality: 0.92

The analysis earns 0.92 for separating the cert question from the merits, treating the petition's assertions as advocacy, and connecting the downward adjustment to specific vehicle and attention signals. It distinguishes the sealing-motion grant from a cert grant, ordinary long-conference scheduling from relisting, and motion-specific nonparticipation from a known petition recusal. Its discussion of a particular preservation obstacle is carefully limited rather than treating every question as forfeited. It explains why the published lower decision provides some positive weight without establishing a clean conflict.

Its prior-Term risk-set anchor is methodologically appropriate; the small difference between its 593/11580 calculation and my 592.925/11580 reflects its reported use of unrounded JSON versus my contract-specified rendered percentages. The analysis explicitly labels terminal relist/CVSG cuts as descriptive rather than transition probabilities and discloses that the final adjustment is judgmental. Remaining limitations are the uncalibrated magnitude of the reduction, incomplete administrative materials, and lower-opinion characterizations not independently re-fetched in this evaluation. A correct denial does not establish the truth of either party's ERISA position or the Court's reasons for denying review.

## Baseline and scoring scope

This is a cert-stage cell. All candidates froze `context.band=baseline`, `context.salience_version=sal-v4`, and docket Term 2025. The committed `metrics/statpack.md` heading matches that version. I use its bracketed reached-band risk-set rates, not the terminal rates and not this evaluator's decided-docket context.

The strictly prior displayed Terms are 2017–2024: 4.7% × 1643, 4.6% × 1524, 4.6% × 1399, 4.5% × 1739, 5.6% × 1500, 5.8% × 1192, 5.9% × 1312, and 5.7% × 1271. Their resolved-weighted pool is 592.925 / 11580 = 0.05120250431778929. The numerator is reconstructed from rounded displayed percentages, not an integer count of grants. These are denial-reweighted live/historical-slice estimates. The caption renders 10 of 10 Terms; excluding 2025 and 2026 leaves all eight eligible displayed rows, with no rendered-window truncation. These figures describe the committed pack supplied to this evaluation, not an independently refreshed corpus.

`correct` compares the disposition labels exactly. Brier is probability squared because actual_granted is zero; skill is 1 minus Brier divided by the squared pooled baseline. Positive skill here describes this single denial only, not demonstrated calibration or aggregate performance. Cert votes are not scored. No judgment score or semantic grades apply. The forecast document was read for context only; neither it nor the structured claim probabilities contributes to reasoning_quality. Mechanical claim scores and provenance stamps remain the harness's work.

## Independent significance

I assessed significance at 0.20 from the provisioned questions and outcome before reading the candidate scores. The proposed ERISA notice and QDRO questions have potential relevance beyond one claimant, but the presented dispute concerns a particular benefit arrangement and the realized disposition supplies no merits holding. This is a stakes assessment, not agreement with any candidate's score.

## Leakage assessment

Forward prediction dated September 17, 2026, before the October 5 denial. The logged case-specific search is restricted to ca4, docket 24-1959, filed before December 9, 2025, followed by reads of lower-court opinion 11216613. No query or prose shows this petition's disposition. Capture coverage is 35/37; the two unobserved web calls concern general certiorari rules. Their null results do not prove failure; their queries, not assumed empty responses, support the assessment. No evidence of mis-provisioned decided-case material.

I therefore record retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false. The evaluator's October snapshot is not used to infer which entries the candidate received. The candidate's own frozen context and captured queries identify its September information set. No outcome material was fetched independently during this evaluation.
