# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage event, resolved by denial on October 5, 2026. codex-baseline's `denied` label matches exactly, giving **correct = 1**. With P(any grant) = 0.015 and `actual_granted = 0`, Brier loss is **0.000225**. The denial supplies an outcome, not an explanation endorsing any particular vehicle objection.

## Baseline and skill

The scored prediction's frozen context carries Term 2025, `baseline`, and `sal-v4`; the statpack's salience heading matches. I pool the bracketed baseline `reached` figures for strictly prior Terms: OT2024 5.7%/1271, OT2023 5.9%/1312, OT2022 5.8%/1192, OT2021 5.6%/1500, OT2020 4.5%/1739, OT2019 4.6%/1399, OT2018 4.6%/1524, and OT2017 4.7%/1643. Each denominator is weighted resolved n.

The total denominator is **11,580**, the reconstructed rate **0.05120250431778929**, and the basis `risk_set`. Using this rate squared as baseline loss gives skill **0.9141777072871346**. Rounded, denial-reweighted table figures make the reconstructed rate approximate. The table shows all 10 of 10 Terms; excluding the current and later Terms leaves the eight rows listed above, with no rendering-window divergence. Neither the terminal band nor the overall/circuit rates replace this baseline. I used the committed pack, not a refreshed corpus, and make no corpus-wide freshness claim. The forecast's snapshot is dated September 15 and this evaluation's snapshot October 5, 2026.

## Reasoning quality: 0.92

The rationale is well grounded and appropriately qualified. It distinguishes a single initial distribution from a relist, uses the correct frozen-band risk set, excludes the case's own Term, and warns that terminal relist and CVSG groups are not forward hazards. These are substantive safeguards against misleading calibration, not just a correct final label.

Its central vehicle objection is supported by the petition's own account at printed pages 9–10 and 19–21: the functional theory was held forfeited, while the petitioner argues both preservation and discretionary consideration. The analysis recognizes that an alternative merits discussion does not automatically eliminate this obstacle. It also separates the petition's allegations from findings and examines whether the cited cases' personal conduct actually conflicts with the alleged direction of deputies in an existing proceeding. The petition itself discusses the Mireles counterargument at printed page 19. The candidate identifies its additional authority retrieval and expressly limits its analogy rather than claiming that it decides this case.

The remaining limitation is numerical and evidentiary, not outcome error: the reduction from about 5.12% to 1.5% is judgmental, and the candidate did not independently read the appendix or full underlying opinions. It discloses both limits. A single denial cannot validate that exact adjustment or prove that forfeiture motivated the Court. The high score rewards the quality of the rationale, not certainty about the Court's unstated reasons.

## Leakage and scope

The harness log records `forward`, with 32 calls on September 16 and capture coverage **30/32 = 0.9375**. Two web rows are unobserved. Although the candidate describes those attempts as yielding no usable content, that absence cannot be independently credited from the log. Their queries concern preexisting authorities rather than Bernard's outcome, so the telemetry gap is not affirmative evidence of leakage. The other recorded lookups concern the provisioned record, statpack, or Mireles; the prose does not presuppose this petition's disposition. No already-decided-forward anomaly is shown. I record no observed outcome material, `not_applicable` influence, and a false leakage-suspicion bit.

The forecast document is contextual only. The qualitative score excludes its accuracy and excludes the quantitative claims, which the harness scores. Cert votes and semantic propositions are not scored on this stage. No independent big-case score is supplied.
