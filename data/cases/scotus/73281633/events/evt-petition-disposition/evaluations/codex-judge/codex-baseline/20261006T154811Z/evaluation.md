# Evaluation: codex-baseline

Case: scotus/73281633. Event: evt-petition-disposition. Candidate run: 20260916T201911Z. Evaluation run: 20261006T154811Z.

## Outcome and quantitative score

The provisioned `outcome.json` records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The candidate predicted **denied**, with P(grant) = **0.09**, on September 16, 2026. Exact-label correctness is **1**. Brier = (0.09 - 0)^2 = **0.0081**. With the risk-set baseline below, Brier skill = **-2.089602537663**.

## Reasoning quality: 0.90

The rationale gives a disciplined, evidence-sensitive explanation for a modest uplift from the prior. It distinguishes the petitioner's asserted circuit conflict from a verified conflict, engages with the opposition's account of the evidentiary record, and gives the interlocutory posture and public-interest ground substantial weight. Particularly strong is its check of the reproduced appellate opinion: the supplied petition appendix, 29a n.9, leaves the five-month-delay issue unresolved, while 30a gives an alternative public-interest assessment even assuming likely merit in the First Amendment claims. The rationale does not incorrectly turn every equities issue into an independent appellate ground.

It also distinguishes frozen risk-set conditioning from terminal buckets and acknowledges that the reply and underlying circuit decisions were not independently examined. The numerical uplift for amici and doctrinal significance remains judgmental rather than estimated, and the incomplete reply/conflict verification limits certainty; those are the principal reasons not to award a near-perfect score. The denial is consistent with the prediction, but the recorded outcome provides no explanation establishing that the Court adopted any of these reasons.

## Baseline and scoring scope

This is a cert-stage evaluation, not a merits judgment. Each candidate froze `context.band = baseline`, `context.salience_version = sal-v4`, and `context.term = 2025`. The matching sal-v4 table in the committed `metrics/statpack.md` supplies the bracketed **reached** rates, so `base_rate_basis` is `risk_set`; the evaluator's terminal context is not used.

Pool all displayed Terms strictly before 2025: 2024 (5.7%, n=1271), 2023 (5.9%, n=1312), 2022 (5.8%, n=1192), 2021 (5.6%, n=1500), 2020 (4.5%, n=1739), 2019 (4.6%, n=1399), 2018 (4.6%, n=1524), and 2017 (4.7%, n=1643). The resolved-weighted rate is 592.925 / 11580 = **0.05120250431778929**. The numerator is a weighted sum reconstructed from rounded published percentages, not an exact grant count. The table caption says 10 of 10 Terms are displayed, so there is no hidden-window divergence to flag. Terms 2025 and 2026 are excluded. These are the committed pack's denial-reweighted historical-slice estimates as read for this evaluation, not a fresh corpus query or a claim of current per-case coverage. The candidates' approximately 5.1% anchors are consistent with this scale; evaluation arithmetic uses the present rendered table, not a candidate's asserted exact numerator.

For the denial, the baseline Brier is the square of that rate. Negative single-case skill means the candidate's elevated grant probability did worse on this denial than the naive baseline; it is not a claim of aggregate model performance or calibration.

No cert vote accuracy or judgment accuracy is scored. No semantic set is declared at this stage, so no semantic grades are written. The linked forecast document was read for context only; neither it nor the quantitative claims block contributes to reasoning quality. Mechanical claim scoring and provenance stamps remain the harness's responsibility. No independent big-case assessment is supplied.

## Leakage assessment

Forward prediction made September 16, 2026, before the October 5 denial. The 32-call log has 30 captured results and two unobserved general-law web calls (Rule 10 search and rules PDF); their queries do not seek this case or its result. Unobserved results are not treated as empty. Local reads concern provisioned briefs, the snapshot, and aggregate statistics. The directory search explicitly excludes the prohibited labeling-artifact subtree; it is not evidence of reading that subtree. No own-case disposition surfaces in the log or prose.

The supported assessment is forward / `not_applicable`, with no affirmative own-case outcome retrieval and `leakage_suspected = false`. This is an evidence-bounded finding, not a claim that absent telemetry proves empty retrieval.
