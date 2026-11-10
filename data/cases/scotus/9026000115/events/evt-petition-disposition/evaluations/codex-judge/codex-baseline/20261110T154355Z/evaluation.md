# Evaluation: codex-baseline

## Outcome and quantitative accuracy

This is a cert-stage event. The petition was denied on November 9, 2026, following its sole distribution for the November 6 conference. The outcome records no CVSG and no noted dissent from denial. The predicted disposition, denied, matches exactly: correct = 1. Against actual_granted = 0, the 0.025 grant probability gives Brier = (0.025 - 0)^2 = 0.000625. These values are independently elicited here; the harness recomputes them. Cert votes are not scored, and no semantic or quantitative-claim grades are supplied.

## Reasoning quality: 0.92

The rationale carefully separates the petitioner's advocacy from the appended courts' findings. It identifies the potential general issue under Groff while explaining why this record is an unattractive vehicle: duplicative error-correction questions, no developed square split, an unpublished affirmance, and procedural obstacles to introducing the expert evidence. The staged petition corroborates its principal points: appendix A, A14-A18, describes diligence and disclosure problems; A19-A28 applies the undue-hardship standard to the healthcare setting; appendix C supplies the short unpublished affirmance; appendix D records rehearing denial without a requested poll. These are substantive reasons to discount review, not merely a prediction that the usual denial will recur.

The rationale also avoids treating waiver as a concession or the denial as approval of the lower court's merits analysis. It distinguishes a conditional summary route from an unconditional probability and explains its information limits. The remaining limitation is calibration: the specific downward adjustment is judgmental, without comparable-case evidence or a demonstrated mapping from these vehicle features to a numerical forecast. This grade assesses reasoning.md alone, not the forecast document, claims block, significance estimate or favorable Brier result.

## Base-rate provenance

I reconstructed the candidate's eligible statpack using statpack-at. The recovered build is 886549a3ac32bdba039691b6d2ca7dc57bb72561, landed October 13, 2026, digest sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde; no alternative build was reported. Its sal-v4 table supports the rationale's use of the reached/risk-set column and strictly prior 2017-2025 Term rows rather than the current Term or the terminal-band column. I do not substitute today's sal-v8 context for the prediction's frozen sal-v4 context. No separate evaluation anchor is calculated or quoted: comparison is to the stamped segment base rate, and baseline, basis and skill are left to the harness.

## Predicted reasoning

Grade: 0.95. The central forecast was specific about both disposition and path: denial, no additional distributions, no CVSG, and action shortly after the November 6 conference in November. Those commitments match the staged docket and outcome, including the November 9 denial. The prediction of no noted dissent also matches the explicit outcome field. This is more informative than an unelaborated denial forecast. The terse docket does not independently establish the absence of every possible statement respecting denial, so that extension earns no additional credit. Conditional predictions about a granted question and summary versus plenary review were never tested and receive neither credit nor penalty. The small distance from the top reflects the conventional rather than highly individualized procedural forecast; no undisclosed merits ground is inferred from denial.

## Leakage

Forward mode; leakage_suspected = false; influence = not_applicable. The prediction was made October 18, before the November 9 resolution. I reviewed all 47 captured-log entries. Local reads concern the provisioned predecision material and aggregate context; the six unobserved external calls concern Groff or general Court rules. Their queries do not seek this petition's result. Unobserved results are not treated as verified failures, notwithstanding the candidate's account of unsuccessful lookup attempts. Nothing in the log or reasoning shows this petition was already resolved when provisioned or that its disposition surfaced. The evaluator's November 9 snapshot is not evidence about what the candidate's October 18 snapshot contained.

## Significance

My independent significance assessment is 0.22: the potential doctrinal issue has cross-case relevance, but the particular vehicle is narrow and the denial established no new merits rule.
