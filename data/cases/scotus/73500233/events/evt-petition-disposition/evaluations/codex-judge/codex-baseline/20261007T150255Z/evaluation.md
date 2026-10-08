# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage petition disposition. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The September 17 prediction calls denied at P(any grant) = 0.01. Thus `correct = 1` and Brier = (0.01 - 0)^2 = 0.0001. The outcome records one distribution, no CVSG and no noted dissent; it supplies no explanation of the Court's reasons. A correct denial forecast does not establish that the Court adopted the predictor's substantive analysis.

The frozen prediction context, not the evaluator's decided-docket context, supplies Term 2025, baseline band and sal-v4. The committed statpack heading matches sal-v4. I use the bracketed reached figures with their weighted resolved denominators for every displayed strictly-prior Term: 2024 (5.7%, 1271), 2023 (5.9%, 1312), 2022 (5.8%, 1192), 2021 (5.6%, 1500), 2020 (4.5%, 1739), 2019 (4.6%, 1399), 2018 (4.6%, 1524), and 2017 (4.7%, 1643). The sum of rate times denominator is 592.925 and the denominator is 11580; the risk-set baseline is approximately 0.05120250431778929. The numerator is an approximation from rounded percentages, not an exact observed grant count. Brier skill is 1 - 0.0001 / baseline^2 = 0.961856758794282.

These are committed live/historical-slice, denial-reweighted estimates, not a newly refreshed corpus measurement. The table reports 10 of 10 Terms rendered; excluding 2025 and 2026 leaves eight eligible rows, with no hidden-window divergence to flag. The skill is descriptive of this one resolved forecast, not an aggregate performance claim.

## Reasoning quality: 0.90

The rationale is specific and carefully qualified. It connects the lack of an identified conflicting holding, the unpublished lower decision, counsel's agreement to admission and the ineffective-assistance posture to uncertainty about a clean review vehicle. The staged petition's account supports the preservation concern, but the candidate appropriately does not convert it into a proven jurisdictional bar. It separates petitioner's advocacy from an independently established lower-court record.

Its discussion of the retrieved historical Dowling authority distinguishes acquitted-conduct analysis from the pending-prosecution counsel and self-incrimination questions, rather than claiming a perfect doctrinal match. I assess that distinction as presented in the rationale, without independently retrieving the authority. It also recognizes that the summer interval before the September conference is not a sequence of relists and uses the response waiver as a procedural signal rather than proof of frivolousness. The matching prior-Term risk-set anchor and explicit limitations make the downward adjustment intelligible.

The remaining deduction reflects the judgmental size of the reduction from approximately 5.12% to 1%, without a measured conditional model, and the absence of opposition and underlying-opinion text for adversarial verification. The bare denial cannot independently validate those analytical premises. I grade `reasoning.md` only: the forecast document was read for context, but neither it nor the structured quantitative claims contributes to this grade.

## Leakage and scope

The harness log identifies forward mode. Prediction and calls occurred on September 17, before the October 5 resolution. The rationale describes an unresolved petition, and no logged retrieval shows this case's disposing order. General-authority retrieval is not this case's outcome material. Capture coverage is 26/28; the two unobserved web calls cannot substantiate the candidate's report of empty results. Their query targets nevertheless do not seek this petition's disposition, and neither the log nor prose suggests a mis-provisioned decided case. I record outcome material false, influence not_applicable and leakage_suspected false, with the capture limitation explicit.

No vote accuracy or semantic grades are written on this cert cell. Mechanical claim scoring and provenance stamps are left to the harness. I omit the optional independent big-case assessment because I did not fix a stakes judgment before seeing the candidate's score.
