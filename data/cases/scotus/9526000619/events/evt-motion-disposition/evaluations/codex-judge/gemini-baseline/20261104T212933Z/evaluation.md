# Evaluation: gemini-baseline

## Outcome and mechanical scores

This is an **interim / arrival** cell. The outcome records denial on November 3, 2026, with `interim_reading: denied` and `interim_granted: 0`. The November 4 snapshot records denial by the Chief Justice. The predicted label `denied` is correct: **correct = 1**. With P(relief) = 0.002, **Brier = (0.002 - 0)^2 = 0.000004**. The legacy binary and finer reading agree here.

The baseline and skill are reserved to the harness. The committed statpack's strictly prior application Terms 2016–2025 have zero finer-resolved applications and 1,366 finer-unread applications. That fails both the 50-resolved floor and unread-zero coverage requirement; no substitute baseline is supplied. Interim votes are not scored. Semantic grades are inapplicable, and quantitative claim scores remain absent for the harness to compute.

## Rationale quality

**Reasoning quality: 0.65.** The rationale correctly selects the interim standard and identifies the missing finer-reading baseline. It undertakes useful related-litigation investigation rather than treating an empty application as proof of no arguments. The evaluator's staged application independently corroborates the foreclosure/possession setting, appellate dismissal, and related federal litigation, although it is an applicant's filing rather than an adjudication of every factual assertion. These are meaningful analytical strengths.

The rationale nevertheless overstates what its evidence establishes. An appeal dismissed for briefing defects does not, without examining adequacy and preservation, settle the independent-and-adequate-state-ground question. The now-readable application specifically contests procedural adequacy, invokes a federal opportunity-to-be-heard claim, and distinguishes later Consent Order performance from the original auction. gemini-baseline lacked that text and is not penalized for failing to quote unavailable arguments; the weakness is declaring negligible uncertainty and virtually no cognizable federal issue despite acknowledging that gap. Likewise, sweeping assertions about Chief Justice handling and selected recent denials do not demonstrate a calibrated 0.2% probability or near-certain conditional denial frequency. The actual denial does not establish the Chief Justice's reasons.

There is also a checkable numerical problem within `reasoning.md`: it reports older-reading prior-Term totals of 237 grants / 1,906 resolved and a pack substantive population of 2,869. The currently committed pack instead supplies 160 / 1,366 for Terms 2016–2025 and 1,490 substantive applications overall. Its attribution of the descriptive grant population overwhelmingly to represented/high-salience applicants is not established by the cited marginal tables. The predictor-time pack itself is not staged, so an earlier-version explanation cannot be excluded; this is a flagged discrepancy, not proof of fabricated data. No older-reading rate is adopted as this evaluation's baseline. The reasoning grade rests only on the rationale's evidentiary discipline, not on the forecast document or structured claim results.

All three candidates report empty application text at prediction time, whereas this evaluation now has OCR (`empty_text: false`, `ocr_derived: true`). That provisioning difference is flagged separately.

## Predicted reasoning

**Forecast quality: 0.90.** The central procedural forecast was specific and successful: direct Chief Justice denial, no response request, no referral, no amicus submissions, and disposition three to ten days after October 30 docketing. Denial occurred November 3, four days later. The one-line/no-writing forecast cannot be fully verified without the order body or writing record. The proposed doctrinal explanation also remains unresolved: an unexplained docket denial neither confirms nor refutes acceptance of a procedural bar. Hypothetical merits analysis is not scored as a decided holding. Unresolved grounds are not marked as misses, and the rationale's separate methodological shortcomings are not imported into this forecast grade.

## Leakage assessment

The log says forward mode. All 43 calls are `outcome_only`: tool completion is observable but returned text is not. I do not treat null dates/digests as proof that nothing was retrieved or regard this standing capture shape as a defect. The queries include target-party searches and reading a related federal opinion dated October 5, 2026; forward retrieval of such background is legitimate. The retrieval note reports submission/docketing, not the target application's denial, and the reasoning contains no affirmative admission or presupposition of that result. No outcome exposure is established on the available query/prose evidence, so influence is `not_applicable` and leakage suspicion false, subject to the returned-content limitation. Prediction and resolution both occurred November 3, but no resolution time establishes their order; the shared date alone is not a misroute finding.

## Stakes

My independent significance assessment is 0.08. The OCR application shows serious personal housing consequences and a federal procedural claim, but a narrow, individualized requested remedy rather than established systemic reach.
