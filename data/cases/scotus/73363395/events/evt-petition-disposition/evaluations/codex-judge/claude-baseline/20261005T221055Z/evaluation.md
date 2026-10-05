# Evaluation: claude-baseline

## Outcome and numerical scores

The authoritative cert-stage outcome is denial on October 5, 2026, with `actual_granted = 0`. claude-baseline predicted `denied` and P(any grant) = 0.006. Therefore **correct = 1** and **Brier = (0.006 - 0)^2 = 0.000036**. The denial supplies no merits explanation against which to validate the candidate's proposed legal rationale.

The prediction freezes `baseline` under `sal-v4`, Term 2025. The committed table matches that version; the proper population is its bracketed reached risk set. The table renders all ten available Terms, 2017–2026, and the strictly-prior window is 2017–2024. The eligible rate/weighted-n pairs are: 2017, 4.7%/1,643; 2018, 4.6%/1,524; 2019, 4.6%/1,399; 2020, 4.5%/1,739; 2021, 5.6%/1,500; 2022, 5.8%/1,192; 2023, 5.9%/1,312; 2024, 5.7%/1,271.

The resolved-weighted baseline is 592.925 / 11,580 = **0.05120250431778929**, recorded on the **risk_set** basis. The numerator reflects rounded displayed rates, not an observed integer grant count. Skill = 1 - 0.000036 / baseline^2 = **0.9862684331659415**. This is a single-outcome score, not a calibration conclusion. These calculations use the committed statpack as read during evaluation, with no independent remote corpus refresh or freshness claim.

## Reasoning quality: 0.82

The rationale identifies a concrete obstacle in the petition's federal framing, ties it to language actually present in the petition's quoted state authority, and gives a case-specific account of the lower-court dispute. The captured queries support that it sought and read the antecedent opinion, while its prose distinguishes the unhelpful generic corpus results from the sources that informed its estimate. It correctly chooses the prior-Term reached baseline and acknowledges that the extreme 0.6% probability retains residual uncertainty.

Several inferences are too categorical. The questions presented separately invoke the Seventh and Fourteenth Amendments; describing both as a Seventh Amendment claim and dismissing the due-process framing as the same grievance compresses an issue that deserved separate analysis. The reported absence of a federal question in the appellate opinion does not by itself establish that it was never pressed below, although the candidate partially qualifies that inference with "appears." Its suggestion that revised filings and delayed docketing indicate substantive weakness is speculative, and its Florida-origin bucket is broader than this precise procedural vehicle. Statements that the petition is below the median on every dimension and that the true probability is not above 1% exceed the empirical support supplied.

Those limitations reduce the grade without negating the useful legal and record-based analysis. I do not treat the favorable outcome as confirmation of each asserted obstacle. The precise probability adjustment remains judgmental rather than fitted.

This score concerns `reasoning.md` only. The forecast document is contextual and unscored; its timing, route language, and the structured quantitative claims receive no separate or implicit grade here. Claim scoring belongs to the harness. Cert votes and semantic claims are not scored. The optional independent stakes assessment is omitted.

## Leakage

All 23 logged calls are captured and dated September 16, before the October 5 resolution, and the mode is forward. The case-caption search metadata identifies the January 2, 2025 lower-court decision; the target docket lookup has May 19, 2026 metadata. The candidate describes an unterminated docket last modified June 17, rather than a known cert disposition. The subsequent opinion reads concern that lower-court decision, not the Court's later denial. Reading this open docket and antecedent opinion is legitimate forward retrieval, not leakage merely because the caption matches. No observed query, document date, or reasoning reveals the eventual disposition as already known. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
