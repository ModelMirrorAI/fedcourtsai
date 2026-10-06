# Evaluation: codex-baseline

## Outcome and mechanical scores

codex-baseline's September 17 prediction names `denied`, with P(grant) = 0.005. The committed outcome is `denied`, `actual_granted = 0`, dated October 5, 2026. Thus **correct = 1; Brier = 0.000025**. The event explicitly declares `cert`; its actual mandamus posture is a flagged reference-population mismatch, not grounds for changing the recorded stage or scoring rule.

I use the candidate's frozen `baseline` band, `sal-v4` version, and Term 2025. The matching statpack heading permits the `risk_set` basis and bracketed reached figures. The eligible rows are 2024: 5.7%, n=1271; 2023: 5.9%, n=1312; 2022: 5.8%, n=1192; 2021: 5.6%, n=1500; 2020: 4.5%, n=1739; 2019: 4.6%, n=1399; 2018: 4.6%, n=1524; 2017: 4.7%, n=1643. Pooling gives 592.925 rate-weighted outcomes over 11,580, or **0.05120250431778929**. The numerator is reconstructed from rounded table percentages and is not an exact grant count.

Brier skill is `1 - 0.000025 / baseline^2` = **0.9904641896985705**. This evaluation follows the required rendered Markdown table, whereas the candidate reports using unrounded JSON rates, giving 593/11,580; that tiny numerical difference is rounding, not a band, version, or population error. The caption displays all 10 of 10 Terms, and I exclude 2025 and 2026, so there is no rendered-window mismatch. These are committed-pack estimates, not a newly refreshed corpus measurement. The ordinary paid-cert baseline is not a matched mandamus cohort, and this denial does not demonstrate general calibration or skill.

## Rationale quality: 0.90

The rationale carefully separates docket observations, missing information, and judgmental adjustments. It identifies the extraordinary-writ versus cert-population mismatch, states a concrete procedural threshold, and explains why waivers are modest posture evidence rather than admissions, defaults, or proof of meritlessness. It explicitly refuses to treat missing lower-court metadata as an absence of lower proceedings or failed text extraction as an absence of substantive issues.

The empirical starting point uses the correct frozen band and strictly prior Terms, while distinguishing risk-set rates from terminal buckets and identifying the absence of a matched extraordinary-writ sample. Its retained uncertainty is tied to unreadable substantive material rather than asserted knowledge of the eventual result. These are strengths of the analysis independent of its correct denial prediction.

The remaining limitation is material: no petition substance was actually read, no matched cohort calibrates the downward adjustment, and the exact 0.5% remains a judgment rather than an empirically supported estimate. The denial itself supplies no explanation confirming the candidate's proposed threshold rationale. Those limits prevent a maximal quality grade. I do not penalize the candidate for lacking petition text that was staged only in this evaluation's record.

Only `reasoning.md` contributes to this score. The forecast document and ancillary probabilities are unscored here; mechanical claim scores remain the harness's. No vote accuracy, judgment comparison, or semantic grades are written for this cert-stage event. The candidate's own significance choice is not part of rationale quality.

## Leakage and limitations

The log records `forward`, with 22 of 28 results captured (coverage 0.7857142857142857). Six web calls are unobserved; their absent document dates or digests do not establish that they returned nothing. Their queries are confined to generic rules and the exact historical petition PDF. Captured shell-call records corroborate subsequent direct-fetch attempts, while the candidate reports that all petition pages yielded no text. There is no current-docket query, outcome-seeking search, or prose showing this petition's disposition had already occurred.

Influence is `not_applicable`, and leakage is not suspected. This finding rests on forward timing, query targets, and the rationale, not on treating unobserved results as empty. The evaluator's decided snapshot does not establish what the earlier predictor snapshot contained.

My independent significance read is 0.05, formed from the evaluator's questions presented, snapshot, and outcome before reading candidate scores. The individual next-friend and party-joinder dispute has no demonstrated broad doctrinal footprint. It is not an agreement score and does not penalize the candidate's decision not to assign its own significance number.
