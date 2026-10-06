# Evaluation: codex-baseline

## Result and reasoning quality

- Exact disposition match: **1**.
- Brier: **0.0256** = 0.16 squared.
- Brier skill against the risk-set baseline: **-8.7646697486638**. On this denial, the 16% forecast incurs more squared error than the approximately 5.12% baseline. This is a single-event comparison, not an estimate of general predictive skill.
- Reasoning quality: **0.89**.

The rationale gives a careful, evidence-bounded analysis. It distinguishes a scheduled first conference from an actual relist, uses the frozen salience band and strictly-prior reached population, and expressly avoids treating terminal relist/CVSG cuts as independent transition probabilities. It separates petitioners' asserted stakes from audited amounts and identifies which briefs, appendices, and authorities it did not independently examine.

Its treatment of the asserted split is discriminating: foreign-law avoidance authority under Section 1521(a)(7) need not resolve limitations under Sections 546(e) and 561(d), and different legal mechanisms need not produce conflicting judgments. It fairly recognizes why a statutory-bar versus preemption distinction could matter for foreign law while explaining why the briefs do not establish a square conflict. The opposition's conflict and vehicle sections support this account of the advocacy. The rationale also avoids overstating complex alternative grounds as proved dispositive barriers. The denial is consistent with these reservations but does not confirm them as the Court's actual reasons.

The chief weakness is the size of the increase from roughly 5% to 16%: it remains an acknowledged subjective adjustment, without a quantitatively calibrated comparison establishing that magnitude. Failed independent authority checks also limit confidence in the legal characterizations. Those limitations keep the grade below the top of the scale without replacing analysis quality with hindsight accuracy. The candidate reports 593/11,580 from the machine-readable pack; this evaluator follows the prompt's rendered-table surface instead, producing the slight rounding difference of 592.925/11,580. That is not a different Term window or band population.

## Scoring basis

The cert-stage outcome records `denied`, `actual_granted = 0`, resolved October 5, 2026. Correctness is the exact disposition match; Brier is the squared grant probability. The outcome supplies no explanation for denial, so agreement with denial does not establish that the Court adopted any particular vehicle or statutory argument.

All baseline calculations use this candidate's frozen `context`: Term 2025, `baseline`, `sal-v4`, matching the committed `metrics/statpack.md` heading. The risk-set baseline pools the bracketed reached figures for every displayed strictly-prior Term, OT2017–OT2024. In descending Term order, the rate/weighted-denominator pairs are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. The displayed-rate weighted numerator is 592.925 and denominator is 11,580, giving **0.05120250431778929**. That numerator is an approximation from rounded published percentages, not an integer count. The table renders all 10 of its 10 Terms; OT2025 and OT2026 are excluded. There is no rendered-window divergence or salience-version mismatch. These are the supplied committed pack's denial-reweighted live/historical-slice estimates, not a refreshed corpus measurement.

The forecast document was read for context only. Neither it nor the mechanical claims block enters reasoning quality; claim scores are reserved for the harness. Cert votes are not scored, and this stage declares no semantic set, so vote accuracy, judgment correctness, and semantic grades are omitted. No independent big-case score is supplied.

## Leakage assessment

Forward log, captured-result coverage 25/27 (approximately 0.9259). September 16 calls precede the October 5 resolution. Two web rows are unobserved and concern a general Section 561(d) statutory query/page; their missing results do not prove that nothing returned. Other visible requests concern provisioned briefs, committed rates, and a preexisting Condor citation. The prose reports unsuccessful research but does not know or presuppose this petition’s disposition. No affirmative indication of outcome retrieval or mis-provisioning.

Assessment: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. This is the forward-mode assessment on the available evidence, not a claim that a missing document date or missing result proves absence.
