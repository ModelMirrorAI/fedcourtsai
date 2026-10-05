# Evaluation: codex-baseline

Case scotus/73500221; event evt-petition-disposition; prediction run 20260917T181231Z; evaluation run 20261005T221055Z.

## Result and reasoning quality

The candidate correctly predicts denial with P(grant)=0.012. Its rationale carefully distinguishes the private petitioner's frozen band from the municipal respondent, the future conference from a completed consideration, and a terminal relist frequency from a forward hazard. It describes the state savings-statute and limitations obstacle rather than treating Knick as automatically eliminating the consequences of a completed state adjudication. The supplied petition confirms the dispute over whether that adjudication was on the merits; the candidate's logged, dated appendix requests are consistent with its stated effort to examine the lower court's treatment directly.

The reasoning fairly presents the alleged uncompensated occupation as the best counterweight, marks allegations as allegations, limits its no-split claim to the petition inspected, and identifies selective appendix review and the missing opposition brief as limitations. It explicitly calls the adjustment from about 5.12% to 1.2% subjective and avoids presenting weighted denominators as an independent random sample. These are strengths in reasoning.md, not credit for the separate forecast document or claims block. The remaining limitation is that the exact adjustment is not empirically estimated and the full appendix is not reproduced in the evaluator's inputs for independent comparison. The record supports reasoning_quality=0.93, not certainty about the Court's unexpressed grounds.

Correct = 1. Brier = (0.012 - 0)^2 = 0.000144. Brier skill = 1 - 0.000144 / (0.05120250431778929 - 0)^2 = 0.9450737326637662.

## Baseline and scope

This is a cert-stage evaluation, not a merits evaluation. The scored candidate's own frozen context records baseline, sal-v4, and Term 2025. The committed metrics/statpack.md heading also names sal-v4. I use the bracketed reached rates, not the terminal leading rates or the evaluator's decided-docket context: base_rate_basis = risk_set.

The strictly-prior rendered pool is OT2017-OT2024. In ascending Term order the reached rates and weighted resolved denominators are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their denominator-weighted mean is 0.05120250431778929 over weighted n=11,580. This calculation uses the displayed, rounded percentages, so it is approximate rather than a reconstruction of unpublished precision. The caption renders 10 of 10 Terms; excluding 2025 and 2026 is the required prior-Term cut, not a truncated-window discrepancy. These are denial-reweighted live/historical-slice estimates, not an independent random sample. I used the committed pack as supplied, did not refresh or query the corpus, and make no current-corpus freshness claim; a build timestamp was not supplied in the inspected table.

The disposition and Brier are scored against outcome.json: denied, actual_granted=0, resolved October 5, 2026. The denial records no explanation adjudicating the petition's legal theory. Correctness therefore confirms the outcome forecast, not any asserted reason the Court denied review. One successful low-probability call establishes neither calibration nor general forecasting skill.

Reasoning quality concerns reasoning.md alone. I read predicted_reasoning.md for context but did not grade that document or the quantitative claims. Claim scores and provenance/context stamps are left to the harness. Vote accuracy and semantic grades are omitted because this is a cert event. No independent big-case assessment is supplied.

## Leakage assessment

The transcript records 35 calls, 32 captured and three unobserved. The unobserved web queries concern Knick or the exact already-filed May 18 appendix. I do not adopt the candidate's reported empty web results as independently proven: their capture markers leave them unobserved. The dated appendix requests and the Tenth Circuit query bounded before February 18 concern pre-petition material; they do not seek the Supreme Court petition's subsequent disposition. Later captured shell-query slices corroborate appendix-fetch activity without reproducing its entire text. There is no observed query or reasoning that discloses the October 5 outcome as known in September. Under the genuinely unresolved forward rule, influence is not_applicable and leakage_suspected=false.
