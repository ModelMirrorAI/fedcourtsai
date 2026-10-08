# Evaluation: claude-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline's September 17 prediction named `denied` and assigned any-grant probability 0.04. Thus `correct = 1` and Brier = `(0.04 - 0)^2 = 0.0016`.

The baseline uses the prediction's frozen `baseline` band, `sal-v4`, and Term 2025, not the evaluator's terminal context. The committed statpack heading matches that version. Pooling every displayed strictly-prior Term's bracketed baseline reached rate gives:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The executed resolved-weighted calculation is 0.05120250431778929 over n = 11,580; `base_rate_basis = risk_set`. The table renders 10 of 10 Terms, so there is no rendered-window truncation. Terms 2025 and 2026 are excluded. The percentages are rounded, making the pooled rate an approximation to the underlying count-based rate. Skill = `1 - 0.0016 / 0.05120250431778929^2 = 0.38970814070851245`. This is a single-event comparison, not evidence of general predictive skill. These are committed statpack figures read October 7, not a claim about freshly queried corpus state; no corpus lookup was made.

## Reasoning quality: 0.85

The grade applies only to `reasoning.md`. The analysis connects the response request to increased review interest but weighs it against a particularly relevant reported lead-case denial, the unpublished and derivative appellate disposition, the absence of a demonstrated circuit conflict, and multiple potential vehicle obstacles. The petition excerpts provisioned to this evaluation support the unpublished disposition and its reliance on Curtis. The candidate separates the two notices for the same conference from a genuine additional conference and explains the probability adjustment rather than merely invoking a low cert base rate. Its retrieval account includes both oppositions, the reply, and the lower-court appendix; the captured queries corroborate those retrieval routes.

The limitations are substantive rather than a penalty for residual grant probability. The response-request multiplier is acknowledged to come from outside literature and is not calibrated to this particular class. The analysis sometimes states respondents' positions more categorically than its cited record justifies. A denial of review in Curtis is useful selection evidence but does not establish Supreme Court agreement with the underlying theory. The solo-practitioner and caption criticisms receive weight without a demonstrated connection to the review question. These features keep otherwise detailed analysis below full credit. The actual denial supplies no merits rationale that could validate those legal premises retrospectively.

## Leakage assessment

The harness log identifies this as forward and records calls on September 17, before the October 5 resolution. It captures pre-decision opposition/reply retrieval, the appendix, a June 1 orders list for Curtis, related-case docket inquiries, and general response-request research. The candidate expressly treats the Curtis denial as related-case evidence, not this petition's result. There is no affirmative evidence that Roberts's own later disposition was retrieved or presupposed. Accordingly, retrieved outcome material is false, influence is `not_applicable`, and leakage suspected is false.

All marker-bearing calls are captured, although the staged log contains digests and query slices rather than complete result bodies. Null document-date fields are not independent proof that every result was harmless. The conclusion rests on the forward timing, observed queries, and reasoning together. The evaluator's October 5 snapshot is not substituted for the predictor's September 17 baseline.

## Scope

The forecast document was read for context only. Neither it nor the mechanical claims contributes to reasoning quality; claim scores remain for the harness. No cert votes or semantic claims are graded. No independent big-case assessment is supplied. Harness-owned stamps and retrieval telemetry are left unwritten.
