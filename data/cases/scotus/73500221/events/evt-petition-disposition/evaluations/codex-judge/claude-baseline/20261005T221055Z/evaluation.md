# Evaluation: claude-baseline

Case scotus/73500221; event evt-petition-disposition; prediction run 20260917T181231Z; evaluation run 20261005T221055Z.

## Result and reasoning quality

The candidate correctly predicts denial with P(grant)=0.01. The rationale connects the savings-statute/earlier-merits-adjudication problem to poor vehicle quality, identifies the lack of a developed conflict in the petition, distinguishes the takings grievance from the threshold procedural obstacle, and explains both the downward adjustment and a residual chance of interest. It candidly says it relied on the petition's account when the lower-opinion lookup was throttled, rather than claiming to have read an unavailable opinion.

Two qualifications prevent a higher score. The rationale uses the terminal relist-zero population as additional support for the headline 1% estimate even though a currently once-distributed petition can still advance; that selected terminal population is not its forward risk set. Statements that the Court does not grant to review the state-law question, that unpublished decisions are poor vehicles, and that counsel's practice profile is a negative signal are stated more categorically than the supplied evidence warrants. The legal vehicle analysis is nevertheless developed and mostly grounded, warranting reasoning_quality=0.82. I do not grade the separate conditional forecast or claim probabilities.

Correct = 1. Brier = (0.01 - 0)^2 = 0.0001. Brier skill = 1 - 0.0001 / (0.05120250431778929 - 0)^2 = 0.961856758794282.

## Baseline and scope

This is a cert-stage evaluation, not a merits evaluation. The scored candidate's own frozen context records baseline, sal-v4, and Term 2025. The committed metrics/statpack.md heading also names sal-v4. I use the bracketed reached rates, not the terminal leading rates or the evaluator's decided-docket context: base_rate_basis = risk_set.

The strictly-prior rendered pool is OT2017-OT2024. In ascending Term order the reached rates and weighted resolved denominators are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their denominator-weighted mean is 0.05120250431778929 over weighted n=11,580. This calculation uses the displayed, rounded percentages, so it is approximate rather than a reconstruction of unpublished precision. The caption renders 10 of 10 Terms; excluding 2025 and 2026 is the required prior-Term cut, not a truncated-window discrepancy. These are denial-reweighted live/historical-slice estimates, not an independent random sample. I used the committed pack as supplied, did not refresh or query the corpus, and make no current-corpus freshness claim; a build timestamp was not supplied in the inspected table.

The disposition and Brier are scored against outcome.json: denied, actual_granted=0, resolved October 5, 2026. The denial records no explanation adjudicating the petition's legal theory. Correctness therefore confirms the outcome forecast, not any asserted reason the Court denied review. One successful low-probability call establishes neither calibration nor general forecasting skill.

Reasoning quality concerns reasoning.md alone. I read predicted_reasoning.md for context but did not grade that document or the quantitative claims. Claim scores and provenance/context stamps are left to the harness. Vote accuracy and semantic grades are omitted because this is a cert event. No independent big-case assessment is supplied.

## Leakage assessment

All 27 calls have captured results. Two case-caption searches are marked throttled, matching the candidate's account of failed lower-opinion and live-docket checks. Broad granted/denied corpus queries were for population shape; the one extracted document date is February 11, 2025, not a post-resolution date for this petition. A logged generic artifact-example lookup does not establish exposure to this case's outcome, and I did not follow its paths. Neither the rationale nor the logged queries presuppose the October 5 denial. September 17 precedes resolution, so ordinary forward retrieval is permissible and influence is not_applicable. Capture metadata is not a full reproduction of result contents, but there is no affirmative outcome-exposure evidence.
