# Evaluation: claude-baseline

## Outcome and mechanical scores

The committed October 5, 2026 outcome is `denied`, with `actual_granted = 0`. claude-baseline predicted `denied` at P(grant) = 0.003 on September 17: **correct = 1; Brier = 0.000009**. I follow the event's declared `cert` stage while flagging that its docket actually describes an original mandamus petition.

The prediction freezes band `baseline`, version `sal-v4`, Term 2025. The statpack's matching sal-v4 table supports the bracketed reached population and therefore `base_rate_basis = risk_set`. The strictly prior displayed rows are 2024: 5.7%, n=1271; 2023: 5.9%, n=1312; 2022: 5.8%, n=1192; 2021: 5.6%, n=1500; 2020: 4.5%, n=1739; 2019: 4.6%, n=1399; 2018: 4.6%, n=1524; 2017: 4.7%, n=1643. Their rate-times-denominator sum is 592.925 over 11,580, giving **0.05120250431778929**. This is an approximation from rounded displayed rates, not an exact grant count.

Brier skill is `1 - 0.000009 / baseline^2` = **0.9965671082914854**. The caption reports 10 of 10 Terms shown, so no rendered-window discrepancy requires a flag; 2025 and 2026 are excluded. I use the prediction's frozen context, never a terminal band inferred from the decided docket. These are committed-pack figures, not fresh corpus measurements. The ordinary paid-cert benchmark is not an empirical mandamus success rate, and a favorable single-case score establishes neither calibration nor general skill.

## Rationale quality: 0.72

The rationale makes its evidence trail explicit, identifies the extraordinary-writ posture, distinguishes that posture from the cert reference population, and uses a correctly versioned, strictly-prior risk-set anchor. It discusses the extraordinary-relief threshold rather than treating the caption alone as dispositive. The disclosures that the petition and appellate opinion were unreadable, and that the corpus results did not supply useful matched priors, are valuable limitations.

Several categorical conclusions exceed that foundation. A prior appeal and dismissal are relevant context, but the rationale asserts that the adequate-remedy element is facially unmet without having read the particular request or opinion. It offers an unsupported frequency below one in a thousand, relies too strongly on self-representation, celebrity-adjacent parties, and universal waivers, and does not establish that the petition presents no important legal question. The expressly stated 0.3% tail for hypothetical parser errors is not grounded in observed error frequencies and does not substantiate the substantive chance of relief. These are reasons to discount the analysis even though denial was the correct call.

The grade covers `reasoning.md` only. The outcome is a bare denial and does not confirm the rationale's account of why relief was refused. I do not grade the forecast document, ancillary probabilities, or mechanical claims, and leave claim scores to the harness. This cert-stage cell receives no vote accuracy, semantic grades, or judgment comparison.

## Leakage and limitations

The harness records `forward` and 1.0 result-capture coverage across 32 calls. The candidate's searches concern the underlying litigation; its cited appellate date is October 10, 2025, not this petition's October 5, 2026 resolution. CourtListener calls are marked throttled. The candidate reports failed or contentless opinion fetches; capture alone is not proof that usable opinion text was obtained, and the logged digest/date fields are not a substitute for that text. No query or rationale establishes retrieval of this petition's already-decided outcome.

The prospective October 5 order-date forecast is not, by itself, evidence of reading the later denial. Likewise, the disclosed encounter with an earlier prediction JSON is a forecast exposure, not outcome material; I do not infer its content or recast it as outcome leakage. Influence is `not_applicable`; leakage is not suspected. The evaluator's newly staged petition material is not retroactively treated as material this candidate possessed.

My independent significance score is 0.05, formed before candidate scores from the staged questions presented, snapshot, and outcome. The next-friend and party-joinder requests have individual stakes but no demonstrated broadly applicable doctrinal consequence. This is a separate read, not an agreement metric.
