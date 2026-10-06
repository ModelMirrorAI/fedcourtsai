# Evaluation: claude-baseline

Case: scotus/73281633. Event: evt-petition-disposition. Candidate run: 20260916T170237Z. Evaluation run: 20261006T154811Z.

## Outcome and quantitative score

The provisioned `outcome.json` records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The candidate predicted **denied**, with P(grant) = **0.11**, on September 16, 2026. Exact-label correctness is **1**. Brier = (0.11 - 0)^2 = **0.0121**. With the risk-set baseline below, Brier skill = **-3.615332185892**.

## Reasoning quality: 0.76

The rationale is substantially balanced: it uses the frozen baseline risk set, distinguishes terminal no-relist rates from a live petition's prior, weighs amici and recurring doctrinal questions against interlocutory posture, and takes the opposition's challenge to the asserted split seriously. It explains the subjective move to 11% and candidly identifies the missing reply and unverified circuit authorities.

A material source-reading error limits the grade. The rationale says the Second Circuit affirmed both the delay-based irreparable-harm ground and the public-interest ground, treating them as two independent vehicle obstacles. The provisioned petition appendix, 29a n.9, expressly declines to decide whether the five-month delay belonged in the district court's calculus. The appellate irreparable-harm discussion partly depends on the merits assessment. Appendix 30a does support the alternative public-interest ground, so a genuine vehicle concern remains, but the two-independent-grounds formulation overstates it. The generalization about the Court's doctrinal appetite and the inference from a negative docket search to no companion petition also deserve caution, as the rationale partly acknowledges. These are assessments of the candidate's analytical document, not grades of its forecast document or auxiliary claim probabilities. The denial is compatible with its analysis without proving that analysis was the Court's rationale.

## Baseline and scoring scope

This is a cert-stage evaluation, not a merits judgment. Each candidate froze `context.band = baseline`, `context.salience_version = sal-v4`, and `context.term = 2025`. The matching sal-v4 table in the committed `metrics/statpack.md` supplies the bracketed **reached** rates, so `base_rate_basis` is `risk_set`; the evaluator's terminal context is not used.

Pool all displayed Terms strictly before 2025: 2024 (5.7%, n=1271), 2023 (5.9%, n=1312), 2022 (5.8%, n=1192), 2021 (5.6%, n=1500), 2020 (4.5%, n=1739), 2019 (4.6%, n=1399), 2018 (4.6%, n=1524), and 2017 (4.7%, n=1643). The resolved-weighted rate is 592.925 / 11580 = **0.05120250431778929**. The numerator is a weighted sum reconstructed from rounded published percentages, not an exact grant count. The table caption says 10 of 10 Terms are displayed, so there is no hidden-window divergence to flag. Terms 2025 and 2026 are excluded. These are the committed pack's denial-reweighted historical-slice estimates as read for this evaluation, not a fresh corpus query or a claim of current per-case coverage. The candidates' approximately 5.1% anchors are consistent with this scale; evaluation arithmetic uses the present rendered table, not a candidate's asserted exact numerator.

For the denial, the baseline Brier is the square of that rate. Negative single-case skill means the candidate's elevated grant probability did worse on this denial than the naive baseline; it is not a claim of aggregate model performance or calibration.

No cert vote accuracy or judgment accuracy is scored. No semantic set is declared at this stage, so no semantic grades are written. The linked forecast document was read for context only; neither it nor the quantitative claims block contributes to reasoning quality. Mechanical claim scoring and provenance stamps remain the harness's responsibility. No independent big-case assessment is supplied.

## Leakage assessment

Forward prediction made September 16, 2026, before the October 5 denial. All 38 logged calls have captured results. Dated retrievals are February 11, 2025, September 11, 2026, April 2, 2026, and March 31, 2026, all before resolution. The own-case docket lookup is described as not terminated, last modified July 1; broad corpus and Central Hudson searches concern priors or potential companions. The Chiles opinion is another case, not this petition's disposition. No own-case outcome is disclosed or presupposed.

The supported assessment is forward / `not_applicable`, with no affirmative own-case outcome retrieval and `leakage_suspected = false`. This is an evidence-bounded finding, not a claim that absent telemetry proves empty retrieval.
