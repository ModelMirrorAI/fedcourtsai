# Evaluation: gemini-baseline

## Outcome and numerical scores

The supplied cert-stage outcome records **denied** on October 5, 2026, with `actual_granted = 0`. The candidate's predicted label matches, yielding correctness **1**. Its **0.06** grant probability produces Brier loss **0.0036**.

The prediction's frozen context carries Term **2025**, band **baseline**, and version **sal-v4**, matching the committed Markdown table. The applicable `risk_set` rate is the denominator-weighted bracketed **reached** rate over all displayed strictly-prior Terms, **2017–2024**: **592.925 / 11,580 = 0.05120250431778929**. The weighted numerator is an approximation from displayed rounded percentages, not an exact grant count. Terms 2025 and 2026 are excluded; the table renders 10 of 10 Terms, with no rendered-window divergence. I do not substitute the leading terminal rates or the evaluator's band.

Skill is `1 - 0.0036 / 0.05120250431778929^2 = -0.37315668340584673`. This is a correct modal call but slightly worse loss than the matching baseline on this denial. It supports no claim of long-run calibration from one case. The calculations use committed statistics, not freshly queried corpus state. The evaluation's supplied snapshot is dated October 5; the candidate's frozen snapshot date is September 15, 2026.

## Reasoning quality: 0.52

The rationale identifies the two questions presented and uses an approximately appropriate prior-Term reached-rate anchor. It sensibly keeps the grant forecast low while treating capital stakes and the asserted cumulative-prejudice disagreement as potential upward considerations. It also distinguishes a possible intervention from the modal denial.

However, the case-specific analysis is thin. The log records a questions-presented read but no petition or opposition body read. The supplied opposition's printed pages 16–22 articulate preservation, absence of a ruling on the proposed legal question, and disputes over assumed versus established deficiencies; the rationale does not engage those central vehicle arguments. Calling the split known without examining those distinctions overstates what the brief analysis establishes. The proposed-order discussion similarly offers a general conclusion without examining the remand and reconsideration dispute.

The baseline band is also asked to do too much work: its absence of stronger procedural signals is not, by itself, independent evidence of poor vehicle quality. Using the band both as the prior and as a principal reason to keep the probability low risks reusing the same information instead of adding a case-specific adjustment. The 6% forecast is plausible, but its sound numerical proximity to the realized denial does not cure those analytical omissions.

This score concerns only `reasoning.md`; assertions appearing only in the separate forecast document are not additional grounds for a penalty. The unexplained denial does not establish the Court's rationale. No cert votes or semantic claims are scored here, and mechanical claim scoring is left to the harness.

## Leakage and observability

The log records **forward** mode and **0/25 captured results**. That is an observability limitation, not evidence of either failed retrieval or misconduct. Two docket-number searches concern this petition, one unrestricted by court and one specifying SCOTUS; the candidate's retrieval note says no matching docket was found, but the absent results cannot independently substantiate that account. I therefore leave `retrieved_outcome_material` **null**, rather than treating missing dates or digests as proof of clean results.

The forecast was made September 16, before the supplied October 5 resolution. Such docket retrieval is legitimate for a genuinely pending forward case. No query expressly seeks the subsequent decision, and the reasoning does not cite or presuppose a completed disposition. There is no affirmative basis to classify influence as possible or likely merely because telemetry omitted results. Influence is `not_applicable`, and `leakage_suspected = false`; this is a timing-based assessment with explicitly limited result observability, not certification that the searches were empty. The standing capture shape does not warrant a data-quality flag.
