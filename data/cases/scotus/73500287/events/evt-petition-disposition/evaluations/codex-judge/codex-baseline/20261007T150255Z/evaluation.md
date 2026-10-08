# Evaluation: codex-baseline

## Outcome and scoring scope

This is a cert-stage distribution cell. The provisioned outcome records denial on October 5, 2026, with `actual_granted = 0`, one distribution, no CVSG, and no noted dissent from denial. The candidate predicted `denied`, so `correct = 1`. The unexplained denial does not establish that the Court adopted any candidate's proposed reasons.

Only `reasoning.md` receives the qualitative grade. I read the pointed-to `predicted_reasoning.md` for context but do not grade that forecast or the quantitative claims. Claim scores belong to the harness. Vote accuracy and semantic grades are omitted on this cert cell. No independent big-case assessment was formed before viewing the candidates' scores, so that optional field is omitted.

## Common baseline

The scored prediction freezes `context.band = baseline`, `context.salience_version = sal-v4`, and `context.term = 2025`. These, not the evaluator's terminal context, select the baseline. The committed `metrics/statpack.md` heading matches sal-v4. I pool its bracketed reached rates, weighted by their resolved denominators, over all displayed Terms strictly before 2025:

| Term | Reached rate | Weighted resolved n |
| --- | --- | --- |
| 2017 | 4.7% | 1,643 |
| 2018 | 4.6% | 1,524 |
| 2019 | 4.6% | 1,399 |
| 2020 | 4.5% | 1,739 |
| 2021 | 5.6% | 1,500 |
| 2022 | 5.8% | 1,192 |
| 2023 | 5.9% | 1,312 |
| 2024 | 5.7% | 1,271 |

The denominator is 11,580 and the resulting rate is 0.05120250431778929, with `base_rate_basis = risk_set`. This is an approximation from published rounded percentages, not an integer grant-count reconstruction. The caption renders 10 of 10 Terms, so there is no hidden-window divergence to flag. Terms 2025 and 2026 are excluded. The table describes denial-reweighted live/historical-slice estimates, not a census or an independently refreshed corpus. I made no live-corpus freshness claim or corpus query. codex-baseline's cited exact JSON-based rate differs slightly because it uses unrounded inputs; that is not a substantive disagreement with this required Markdown-table calculation.

## Quantitative result

P(grant) = 0.035, so Brier = (0.035 - 0)^2 = **0.001225**. Skill against the common baseline is **0.5327452952299549**, calculated as 1 - 0.001225 / baseline^2. This single realized score does not establish calibration or aggregate performance. Its higher probability yields a worse Brier on this denial than the other candidates' probabilities, but that alone is not a defect in legal reasoning.

## Reasoning quality: 0.90

This rationale carefully defines its information set and separates party allegations from independently checked material. It correctly distinguishes the sealing-motion distribution and grant from the petition's cert trajectory, uses the frozen sal-v4 band and strictly-prior-Term risk set, and explicitly rejects terminal procedural frequencies as prospective hazards. Those are substantive safeguards against overstating the docket's signal.

The asserted split receives balanced treatment: the candidate recognizes the petition's claimed broader channel-market implications while examining the fractured historical comparator and distinguishing the pleaded aftermarket theory from this summary-judgment record. It expressly limits the inference drawn from the historical rehearing concurrence and attributes the unreviewed lower-court materials to the petition, rather than pretending that the petition's account is neutral. The captured historical citation and opinion calls support that research account, without giving this evaluator the entire original returned text. The provisioned petition's summary-judgment history and quoted core-customer discussion support the rationale's cautious framing.

The chief limitation is that the downward move from roughly 5.12% to 3.5% is judgmental without a calibrated likelihood model or comparable-case estimate. The lower-court opinion, full appendix, and amicus text were not independently examined, limiting the depth of its preservation and vehicle analysis. Those limits are candidly disclosed. This grade rewards the soundness and uncertainty discipline of `reasoning.md`, not its length, the unscored forecast, the claim probabilities, or a supposed judicial endorsement of the analysis. A bare cert denial supplies no such endorsement.

## Leakage

The log is forward. All recorded work precedes the October 5 denial, and the historical precedent lookup is not retrieval of this petition's subsequent history. The two unobserved web rows name general certiorari rules and the Court's rules PDF, not the target petition. Their absent results cannot independently confirm the candidate's report that they returned no usable content, but the queries themselves are not outcome-seeking. Coverage is 0.9333333333333333; other-class tool names are neutral capture normalization, not suspicious evidence. The transcript's explicit exclusion of the prohibited labeling directory in a file-discovery command is not a read of that directory. Nothing shows this case's disposition surfaced as already decided. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
