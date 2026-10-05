# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied` with P(grant) = 0.001: exact-label correctness is **1** and Brier loss is **0.000001**.

The frozen Term 2025, `baseline` band, and `sal-v4` version match the committed markdown table. I pool its bracketed reached rates over every displayed strictly prior Term, 2017–2024, using weighted resolved denominators. The pairs, newest first, are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. This yields **0.05120250431778929** over weighted n = **11,580**, `base_rate_basis = risk_set`, baseline loss 0.0026216964484132308, and skill **0.9996185675879429**. The pack describes a denial-reweighted live/historical slice, not a fresh census. All 10 pack Terms are displayed; 2025 and 2026 are excluded because they are not strictly prior. There is no truncated-window divergence.

The candidate reported 593/11,580 using the corresponding unrounded JSON values. My rate uses the rendered markdown percentages as the evaluation contract directs, so its tiny difference from that stated anchor is rounding, not a different population. I did not independently retrieve those JSON counts.

## Reasoning quality: 0.93

The rationale is strong because it separates advocacy from established findings, identifies unavailable lower-court materials and OCR limitations, and maps specific questions and petition passages to its inference. It does not equate an asserted conflict with demonstrated conflicting holdings, nor infer that no conflict could exist anywhere. It explains why pleading, jurisdictional, and other vehicle issues make a grant less plausible without pretending to have adjudicated those issues. It treats waivers and the single distribution as modest evidence rather than a categorical rule and correctly distinguishes the paid private-petitioner population from IFP or federal-petitioner populations.

Its treatment of the baseline is explicit about the frozen Term and the difference between reached and terminal populations. The rationale also distinguishes general selection criteria from a merits adjudication. Its main limitation is calibration: the move from roughly 5.1% to 0.1% remains a judgmental adjustment without an empirical model for comparable petitions. The candidate acknowledges that the exact probability is less secure than the denial label and that missing lower-court material leaves uncertainty. The realized denial supports the categorical forecast but cannot alone establish the claimed probability's calibration or the Court's reasons.

## Leakage and scope

Both context and log say forward. The September 17 calls predate the October 5 outcome. The external queries concern only general Rule 10 materials and official rules pages; none seeks this petition's disposition. The log captures 32 of 35 results. Its three web rows are unobserved, so I do not equate their missing dates or digests with empty results. Their general subject, the timing, and the rationale supply the clean-forward assessment. A local instruction-file search mentions an excluded labeling path in its exclusion expression, not as a content source; that is not evidence of reading labeling artifacts. No outcome-revealing material appears in the visible record. I record `not_applicable`, with leakage not suspected.

The forecast document was read only for context. Reasoning quality excludes forecast and claim accuracy. Mechanical claims remain for the harness, cert votes are unscored, no semantic grading applies, and no independent big-case assessment is supplied. Harness-owned fields remain absent.
