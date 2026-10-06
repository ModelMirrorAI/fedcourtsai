# Evaluation: gemini-baseline

Case scotus/73500221; event evt-petition-disposition; prediction run 20260917T181231Z; evaluation run 20261005T221055Z.

## Result and reasoning quality

The candidate correctly predicts denial with P(grant)=0.01. Its rationale identifies the matching roughly 5.1% prior, the response waiver, the procedural obstacle arising from the prior state adjudication, and the absence of an identified broad conflict. These support a low grant estimate independently of hindsight.

The analysis is materially less precise about the obstacle than the supplied question presented and petition: the immediate issue is whether the prior action failed otherwise than on the merits for Oklahoma's savings statute, rather than simply a generic res judicata or issue-preclusion bar. The rationale labels the waiver strong evidence of frivolousness or poor vehicle quality without supporting that strength, and treats a response request as necessarily generating a relist even though those are different procedural events. It gives little account of the petitioner's competing compensation argument or why exactly 1%, rather than another low number, follows. These limitations, not the correctness of the eventual denial or the separate claim probabilities, set reasoning_quality at 0.62.

Correct = 1. Brier = (0.01 - 0)^2 = 0.0001. Brier skill = 1 - 0.0001 / (0.05120250431778929 - 0)^2 = 0.961856758794282.

## Baseline and scope

This is a cert-stage evaluation, not a merits evaluation. The scored candidate's own frozen context records baseline, sal-v4, and Term 2025. The committed metrics/statpack.md heading also names sal-v4. I use the bracketed reached rates, not the terminal leading rates or the evaluator's decided-docket context: base_rate_basis = risk_set.

The strictly-prior rendered pool is OT2017-OT2024. In ascending Term order the reached rates and weighted resolved denominators are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their denominator-weighted mean is 0.05120250431778929 over weighted n=11,580. This calculation uses the displayed, rounded percentages, so it is approximate rather than a reconstruction of unpublished precision. The caption renders 10 of 10 Terms; excluding 2025 and 2026 is the required prior-Term cut, not a truncated-window discrepancy. These are denial-reweighted live/historical-slice estimates, not an independent random sample. I used the committed pack as supplied, did not refresh or query the corpus, and make no current-corpus freshness claim; a build timestamp was not supplied in the inspected table.

The disposition and Brier are scored against outcome.json: denied, actual_granted=0, resolved October 5, 2026. The denial records no explanation adjudicating the petition's legal theory. Correctness therefore confirms the outcome forecast, not any asserted reason the Court denied review. One successful low-probability call establishes neither calibration nor general forecasting skill.

Reasoning quality concerns reasoning.md alone. I read predicted_reasoning.md for context but did not grade that document or the quantitative claims. Claim scores and provenance/context stamps are left to the harness. Vote accuracy and semantic grades are omitted because this is a cert event. No independent big-case assessment is supplied.

## Leakage assessment

The harness log records forward mode and 29 calls on September 17, all result-unobserved. I assessed the queries rather than treating missing result dates as clean or failed returns. The log includes corpus queries and two caption searches beyond the single lookup summarized in retrieval.md; those results cannot be reconstructed from the supplied transcript. No query or prose identifies this petition's October 5 disposition as already known, and the rationale speaks prospectively about review. The event was unresolved at the prediction date on the supplied ground truth. Forward influence is therefore not_applicable and leakage_suspected=false, with the stated capture limitation. No inference about actual returned search content is made.
