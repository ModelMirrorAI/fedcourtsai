# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition cell. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot independently contains the denial entry. codex-baseline predicted `denied` with P(any grant) = 0.005. Thus `correct = 1` and Brier = (0.005 - 0)^2 = **0.000025**. A denial supplies no judicial explanation of the merits and does not establish that the Court adopted the candidate's analysis.

The baseline uses the prediction's frozen `baseline` band, `sal-v4`, and Term 2025, not the evaluator's terminal context. The committed statpack's sal-v4 table matches that version. Its caption renders all ten available Terms, 2017–2026; only 2017–2024 precede this petition's Term. The bracketed reached rates and weighted resolved denominators are: 2017, 4.7%/1,643; 2018, 4.6%/1,524; 2019, 4.6%/1,399; 2020, 4.5%/1,739; 2021, 5.6%/1,500; 2022, 5.8%/1,192; 2023, 5.9%/1,312; 2024, 5.7%/1,271.

Resolved-weighted pooling gives 592.925 / 11,580 = **0.05120250431778929**, with `base_rate_basis = risk_set`. The numerator is a weighted calculation from rounded published percentages, not an observed integer grant count. Skill = 1 - 0.000025 / baseline^2 = **0.9904641896985705**. This is a single-outcome comparison, not evidence of calibration. The minor difference from the candidate's 593 / 11,580 anchor reflects its reported full-precision JSON calculation; this evaluation uses the prescribed rendered table. No remote corpus was queried or refreshed; these figures describe the committed statpack read for this evaluation, not independently verified current corpus state.

## Reasoning quality: 0.92

The rationale connects the two questions presented to a concrete federal-vehicle problem rather than merely invoking low overall grant rates. It distinguishes the petition's allegations from established facts, identifies the state/federal jury-guarantee issue also visible in the petition's own quoted authority, and separately considers the due-process framing. It acknowledges that absent lower-court materials prevent certainty about preservation or trial-court error.

The procedural conditioning is particularly careful: the sealing motion's grant and distribution are separated from the petition's single distribution; waiting for the long conference is not mistaken for repeated consideration. The response waiver is treated as modest evidence rather than a dispositive obstacle. The prior-Term risk-set anchor is identified explicitly, and terminal relist/CVSG tables are not represented as forward transition probabilities. The tenfold reduction to 0.5% remains judgmental rather than empirically calibrated, and the unavailable opposition and lower-court record limit confidence. These limitations prevent a perfect score despite the sound, transparent analysis.

Only `reasoning.md` supplies the qualitative grade. The forecast document was read for context but not scored; structured quantitative claims remain for the harness. Cert votes are not scored, and no semantic grade is declared for this stage. The optional independent stakes assessment is omitted.

## Leakage

The log identifies a forward run. Its 33 calls occur on September 16, before the October 5 resolution. Thirty results are marked captured; three web calls are unobserved. Those web queries concern general doctrine and rules, not a case-specific outcome. I do not infer that they returned nothing from their absent dates or digests, nor independently verify the candidate's report that they failed. The remaining external queries identify an older authority, and the prose treats this petition as pending. There is no affirmative evidence of outcome retrieval or a decided case provisioned forward. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
