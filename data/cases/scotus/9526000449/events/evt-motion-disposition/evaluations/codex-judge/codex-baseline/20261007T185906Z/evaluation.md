# Evaluation: codex-baseline

## Outcome and scores

The event is **interim / arrival**. The supplied outcome records `denied` on
October 5, 2026, and `actual_granted = 0`. codex-baseline's October 3 disposition
matches exactly: `correct = 1`. With P(grant) = 0.06,
`brier_score = (0.06 - 0)^2 = 0.0036`.

The outcome supports the denial label, not an inference that the Court
resolved any particular substantive argument against the applicant.

## Reasoning quality: 0.88

The rationale is unusually careful about the distinction between observation
and inference. It identifies the frozen arrival boundary, treats apparent
self-representation as an inference, and explicitly declines to infer the
federal question, lower-court reasoning, harm, or urgency from an unreadable
filing. It correctly distinguishes no response at arrival from an adverse
failure to request a response over time. It also distinguishes unavailable
advocacy from deficient advocacy.

Its baseline analysis uses prior application Terms, excludes the prediction's
own Term, distinguishes unparsed cases from zero grant rates, and explains
coverage and selection limitations. The downward adjustment is expressly
subjective rather than a fitted subgroup estimate. Preserving uncertainty
instead of using the extraction failure as evidence against relief is sound
even though a smaller probability would have scored better on this one
denial.

The residual weakness is that the private caption and apparent
self-representation do not quantitatively identify a 6% grant probability.
No substantive filing or usable authority was recovered, so this remains a
largely prior-driven assessment rather than a case-specific legal analysis.
The document acknowledges those limits; the remaining uncertainty prevents
a near-perfect quality score, rather than warranting a finding of unsound
analysis.

Only `reasoning.md` determines this qualitative grade. The forecast document
was read for context, not scored. Accuracy of the structured escalation
claims and timing forecast does not enter this grade.

## Baseline and exclusions

Baseline and skill are the interim harness's responsibility, so neither is
written here and `base_rate_basis` remains null. The prediction freezes Term
2026 with no band. The committed statpack's prior-Term substantive counts
include 14 grants in 70 resolutions for 2024 and 17 in 226 for 2025; earlier
eligible rows add no parsed resolutions. These rows support the rationale's
anchor and clear the registered 50-resolution floor. A missing section or
insufficient pool is not apparent, but the actual stamp has not run in this
evaluation. Counts describe the committed pack only; I did not query current
corpus state. Uneven parse coverage and the mismatch between pooled and
selected prediction populations remain limitations.

This stage prohibits vote accuracy and declares no semantic claim set.
Vote scores, semantic grades, and harness-owned mechanical claim scores are
absent. I omit the optional independent stakes assessment.

## Leakage and input limits

Forward mode is recorded in the harness log. Its October 3 calls precede the
October 5 disposition. The general-authority search and the opening
application's PDF URL do not seek or demonstrate a resolved outcome. No
reasoning passage treats the application's own denial as already known.
Outcome retrieval is assessed false, influence not applicable, and leakage
suspected false.

Nineteen of 21 call results are captured. The two web calls are unobserved;
the candidate says they returned nothing usable, but null result metadata
cannot independently establish that. Their visible requests, rather than an
assumption of failed retrieval, support the assessment. The application URL's
October 2 date is later than the frozen September 28 baseline, not later than
resolution, and is permissible in a forward cell.

All candidates report unavailable application text. The evaluator's current
manifest reports OCR-derived nonempty text and its current file is 50,786
bytes. I inspected that metadata and size, not the body, and do not treat the
current version as evidence that codex-baseline failed to read an available
filing. The cell-level flags preserve this input-provenance limitation.
