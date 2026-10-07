# Evaluation: gemini-baseline

Case: scotus/73281633. Event: evt-petition-disposition. Candidate run: 20260916T170237Z. Evaluation run: 20261006T154811Z.

## Outcome and quantitative score

The provisioned `outcome.json` records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The candidate predicted **denied**, with P(grant) = **0.12**, on September 16, 2026. Exact-label correctness is **1**. Brier = (0.12 - 0)^2 = **0.0144**. With the risk-set baseline below, Brier skill = **-4.492626733623**.

## Reasoning quality: 0.45

The rationale correctly starts near the historical baseline and keeps denial as its modal outcome despite the commercial-speech issues and four amicus filings. It identifies plausible reasons for above-baseline attention without making grant the favorite.

Its central uplift, however, rests on describing the split as clean and well-developed without demonstrating incompatible holdings or engaging with the opposition's competing account. The staged call queries show reads of the questions presented, snapshot and manifest but no explicit petition or opposition text read; because results are unobserved, that is a limit on what can be verified, not proof of what the candidate knew. The written rationale itself omits the preliminary-injunction posture, the need for a fuller record, and the alternative public-interest ground apparent at petition appendix 30a. Amicus interest is not itself a demonstration of vehicle quality. The appeal to the no-relist bucket also fails to distinguish a terminal no-relist population from a live first-distribution risk set. The approximately 5% initial prior is reasonable, but the move to 12% is inadequately supported. Correctly forecasting denial does not repair those analytical omissions, and the unexplained outcome does not establish which cert considerations mattered.

## Baseline and scoring scope

This is a cert-stage evaluation, not a merits judgment. Each candidate froze `context.band = baseline`, `context.salience_version = sal-v4`, and `context.term = 2025`. The matching sal-v4 table in the committed `metrics/statpack.md` supplies the bracketed **reached** rates, so `base_rate_basis` is `risk_set`; the evaluator's terminal context is not used.

Pool all displayed Terms strictly before 2025: 2024 (5.7%, n=1271), 2023 (5.9%, n=1312), 2022 (5.8%, n=1192), 2021 (5.6%, n=1500), 2020 (4.5%, n=1739), 2019 (4.6%, n=1399), 2018 (4.6%, n=1524), and 2017 (4.7%, n=1643). The resolved-weighted rate is 592.925 / 11580 = **0.05120250431778929**. The numerator is a weighted sum reconstructed from rounded published percentages, not an exact grant count. The table caption says 10 of 10 Terms are displayed, so there is no hidden-window divergence to flag. Terms 2025 and 2026 are excluded. These are the committed pack's denial-reweighted historical-slice estimates as read for this evaluation, not a fresh corpus query or a claim of current per-case coverage. The candidates' approximately 5.1% anchors are consistent with this scale; evaluation arithmetic uses the present rendered table, not a candidate's asserted exact numerator.

For the denial, the baseline Brier is the square of that rate. Negative single-case skill means the candidate's elevated grant probability did worse on this denial than the naive baseline; it is not a claim of aggregate model performance or calibration.

No cert vote accuracy or judgment accuracy is scored. No semantic set is declared at this stage, so no semantic grades are written. The linked forecast document was read for context only; neither it nor the quantitative claims block contributes to reasoning quality. Mechanical claim scoring and provenance stamps remain the harness's responsibility. No independent big-case assessment is supplied.

## Leakage assessment

Forward prediction made September 16, 2026, before the October 5 denial. All 22 logged calls are unobserved, so null dates and digests establish neither empty results nor successful retrieval. Assessable queries concern provisioned inputs, aggregate statistics, a dated corpus-prior query, and a generic Central Hudson circuit-split search, not this petition's outcome. The reasoning treats the petition as awaiting conference and does not presuppose its disposition. No affirmative leakage evidence; result-level verification is limited.

The supported assessment is forward / `not_applicable`, with no affirmative own-case outcome retrieval and `leakage_suspected = false`. This is an evidence-bounded finding, not a claim that absent telemetry proves empty retrieval.
