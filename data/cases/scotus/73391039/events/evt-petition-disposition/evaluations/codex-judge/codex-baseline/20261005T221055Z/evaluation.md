# Evaluation: codex-baseline

The prediction names `denied`, exactly matching `outcome.json` (`actual_granted=0`, resolved October 5, 2026). Thus `correct=1`, Brier `(0.006-0)^2=0.000036`, and skill against the specified baseline is 0.9862684331659415.

## Reasoning quality: 0.93

The analysis carefully separates the abstract procedural importance of Rule 60(b)(4) from this petition's suitability as a vehicle. It identifies that mandatory vacatur presupposes a genuinely void judgment and explains why a disagreement about the pleaded property interest or preclusion does not itself establish that threshold. It fairly acknowledges the petition's stated conflict-with-this-Court theory instead of treating absence of a circuit split as dispositive. It links its analysis to identified petition passages and reports a targeted check of the cited Espinosa discussion, while treating the missing appendices and the petition's portrayal of the lower courts as evidentiary limitations rather than resolved facts.

The probability discussion uses the appropriate frozen salience version and prior-Term reached population. It avoids treating terminal relist and CVSG frequencies as prospective hazards, avoids stacking overlapping population cuts, and explains why a local-government respondent does not make these private petitioners a state-petitioner case. It recognizes that the prior 2024 cert denial is different procedural history. These are substantive strengths in its rationale, not rewards for its auxiliary forecasts.

The remaining limitation is quantitative: the move from about 5.12% to 0.6% is an informed judgment, not a measured conditional rate for a demonstrated comparable cohort. The unavailable appendices also leave its vehicle assessment provisional. Its quoted 593 / 11,580 anchor comes from the accompanying unrounded JSON, according to its retrieval record; my contract-directed Markdown pool is 592.925 / 11,580 because the displayed percentages are rounded. That immaterial precision difference is not a faulty band or window choice and is not penalized.

The October 5 denial resolves the disposition, not the correctness of either side's merits theory; no reasoned Supreme Court endorsement is inferred.

## Leakage assessment

`mode=forward`, `retrieved_outcome_material=false`, `influenced_prediction=not_applicable`, and `leakage_suspected=false`. The log contains 38 calls, 29 captured and 9 unobserved. Its legal-context queries concern Espinosa and general procedural authority. The repeated unobserved request for an opinion path bearing another docket number, 24-808, is not a query for No. 25-1308 and does not demonstrate retrieval of this case's outcome. The candidate reports that the web attempts yielded no usable text, but that claim cannot be independently confirmed from unobserved results; I neither treat their null dates as proof of empty results nor infer a holding from the path. The prose relies on the earlier authority and the pending record, and nothing shows this petition's October 5 disposition was already known. General external context while this forward event remained open was permitted.

## Baseline and scoring scope

This is a cert-stage cell. The prediction froze `band=baseline`, `salience_version=sal-v4`, and docket-number Term 2025. The committed `metrics/statpack.md` heading matches that version. I use `base_rate_basis=risk_set` and the bracketed reached rates, not terminal-band rates or the evaluator's decided-docket context.

The prior-Term pool includes every displayed row before 2025: OT2017–OT2024. In ascending order the reached rates and weighted resolved denominators are 4.7%/1,643; 4.6%/1,524; 4.6%/1,399; 4.5%/1,739; 5.6%/1,500; 5.8%/1,192; 5.9%/1,312; and 5.7%/1,271. Their resolved-weighted mean is 592.925 / 11,580 = 0.05120250431778929. The fractional numerator is reconstructed from rounded published percentages, not an exact grant count. The table reports 10 of 10 Terms rendered, so there is no rendered-window truncation to flag; OT2025 and OT2026 are excluded. These are denial-reweighted live/historical-slice estimates, not a complete-population rate. I did not consult or refresh a live corpus and make no claim about its current freshness; the outcome and case context are the provisioned October 5, 2026 record.

The realized binary is zero, so the baseline Brier is the squared base rate and skill is `1 - brier_score / base_rate**2`. A favorable score on this single denial is not evidence of population calibration or aggregate forecasting performance.

Only `reasoning.md` contributes to reasoning quality. I read the pointed-to forecast document for context but do not grade its prose, timing, or individual claims. Mechanical claim scores are left to the harness. Cert votes are not scored; judgment accuracy and semantic grades do not apply. I omit the optional independent stakes assessment because no such read was fixed before encountering the candidate's stakes assessment in its prose. Harness-owned context and process/version stamps are not written.
