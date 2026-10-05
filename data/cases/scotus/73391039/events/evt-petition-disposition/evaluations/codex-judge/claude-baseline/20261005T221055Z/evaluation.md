# Evaluation: claude-baseline

The prediction names `denied`, exactly matching `outcome.json` (`actual_granted=0`, resolved October 5, 2026). Thus `correct=1`, Brier `(0.005-0)^2=0.000025`, and skill against the specified baseline is 0.9904641896985705.

## Reasoning quality: 0.84

The analysis makes a substantive, case-specific distinction between mandatory relief after a judgment is shown void and the antecedent dispute over whether this judgment was void at all. It connects that distinction to the petition's account of the prior appellate preclusion ruling, the fact-intensive disagreement about the pleaded property interest, an unreported decision, sanctions, and respondent waivers. It selects the correct frozen-band, prior-Term anchor and explicitly discloses that the lower-court opinion and an opposing submission were not independently available. Those are strong analytical features independent of the successful denial call.

Two limitations keep the grade below the top range. First, the section headed “The claimed split is not one” understates the petition's actual framing: printed pages 11–12 expressly describe a conflict with this Court's precedent rather than circuit versus circuit. The analysis does address the precedent theory elsewhere, but failure to demonstrate a circuit split alone does not answer that theory. Second, categorical assertions about how often pro se paid petitions succeed, the composition of grants, and how strongly waivers imply no risk are not supported by a measured comparable cohort in the material it used. Its terminal relist discussion acknowledges the selection problem, yet still leans on that bucket to justify the magnitude of the downward adjustment. The 0.5% point estimate remains judgmental rather than empirically calibrated.

The bare denial supports the outcome call but does not establish that the Court adopted this account of voidness, law of the case, or vehicle quality.

## Leakage assessment

`mode=forward`, `retrieved_outcome_material=false`, `influenced_prediction=not_applicable`, and `leakage_suspected=false`. The 21-call log has capture coverage 1.0. Its lower-court searches and corpus queries precede the event's resolution and do not show this petition's disposition. The candidate reports that the lower-court searches found no usable opinion and the corpus priors were not comparable; I do not treat those self-reports as additional retrieved evidence. The 2024 cert denial mentioned in the petition is earlier procedural history. The forecast's October 5 date does not itself establish leakage. Nothing warrants a mis-provisioned-forward finding.

## Baseline and scoring scope

This is a cert-stage cell. The prediction froze `band=baseline`, `salience_version=sal-v4`, and docket-number Term 2025. The committed `metrics/statpack.md` heading matches that version. I use `base_rate_basis=risk_set` and the bracketed reached rates, not terminal-band rates or the evaluator's decided-docket context.

The prior-Term pool includes every displayed row before 2025: OT2017–OT2024. In ascending order the reached rates and weighted resolved denominators are 4.7%/1,643; 4.6%/1,524; 4.6%/1,399; 4.5%/1,739; 5.6%/1,500; 5.8%/1,192; 5.9%/1,312; and 5.7%/1,271. Their resolved-weighted mean is 592.925 / 11,580 = 0.05120250431778929. The fractional numerator is reconstructed from rounded published percentages, not an exact grant count. The table reports 10 of 10 Terms rendered, so there is no rendered-window truncation to flag; OT2025 and OT2026 are excluded. These are denial-reweighted live/historical-slice estimates, not a complete-population rate. I did not consult or refresh a live corpus and make no claim about its current freshness; the outcome and case context are the provisioned October 5, 2026 record.

The realized binary is zero, so the baseline Brier is the squared base rate and skill is `1 - brier_score / base_rate**2`. A favorable score on this single denial is not evidence of population calibration or aggregate forecasting performance.

Only `reasoning.md` contributes to reasoning quality. I read the pointed-to forecast document for context but do not grade its prose, timing, or individual claims. Mechanical claim scores are left to the harness. Cert votes are not scored; judgment accuracy and semantic grades do not apply. I omit the optional independent stakes assessment because no such read was fixed before encountering the candidate's stakes assessment in its prose. Harness-owned context and process/version stamps are not written.
