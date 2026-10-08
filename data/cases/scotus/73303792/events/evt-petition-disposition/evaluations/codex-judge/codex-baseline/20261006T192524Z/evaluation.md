# Evaluation: codex-baseline

## Outcome and quantitative scores

The cert-stage outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicts `denied`, giving **correct = 1**. Its grant probability **0.006** gives Brier loss **0.000036**.

The candidate froze **baseline**, **sal-v4**, and Term **2025**. The committed sal-v4 table supports the `risk_set` basis. Pooling its baseline bracketed reached entries for all displayed strictly prior Terms, 2017–2024, gives **11,580** weighted resolved petitions. In descending Term order the inputs are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. These rounded percentages imply **592.925** grant-family equivalents and baseline **0.05120250431778929**. Skill is `1 - 0.000036 / baseline^2` = **0.9862684331659415**.

The candidate reports 593/11,580 using unrounded JSON fields. I follow this evaluation contract's rendered Markdown rates; the negligible numerical difference is consistent with display rounding. The caption shows ten of ten Terms, so there is no shortened-window discrepancy. Terms 2025 and 2026 are excluded, and I do not substitute the evaluator's terminal band. The numbers describe the committed denial-reweighted table, not a current remote-corpus measurement. No independent corpus freshness claim or aggregate-performance inference is made.

## Reasoning quality: 0.91

The rationale is notably careful about both substantive vehicle assessment and what the available record can establish. It distinguishes a paid pro se petition from an IFP petition, a summer wait from repeated conferences, and an extension of filing time from interest in the cert petition. Its low grant probability is tied primarily to the claimed multiple grounds below and the weakness of the asserted conflict, rather than to party status alone.

The candidate addresses the petition's characterization of VanderKodde and describes a targeted check of that older authority, while explicitly distinguishing the majority from a concurrence. The staged retrieval note and query slices document an authority lookup; I did not independently fetch that opinion, so I do not represent its substantive holding as separately verified in this evaluation. The supplied petition itself supports the rationale's narrower account that its narrative invokes pleading insufficiency, immunity, amendment futility, and filing restrictions. The candidate treats those as possible independent obstacles, not conclusively established bars, because the appendix is unavailable. It also distinguishes overlapping negative signals instead of multiplying unsupported independent penalties and acknowledges that a response could still be requested.

The remaining limitations are the one-sided OCR-derived record and the judgmental magnitude of the adjustment from approximately 5.1% to 0.6%. The analysis does not empirically calibrate that exact number or fully verify all claimed conflicts. Those constraints prevent a perfect score, but they are disclosed rather than hidden. The October denial confirms the categorical prediction, not the Court's unstated reasons.

Only `reasoning.md` supports the qualitative grade. The forecast was read for context, not scored; its subsidiary events and the structured claims are reserved for the harness's separate calculations. No vote accuracy or semantic grades belong on this cert-stage event. I omit an independent big-case assessment because the candidate's own stakes scores were encountered before such an assessment was formed.

## Leakage

The harness log records forward mode and **29/32 captured results** (coverage **0.90625**), all from September 16, 2026, before the target denial. Its three unobserved web calls concern generic certiorari rules. The candidate says they supplied no usable content, but the log cannot independently establish that: I assess their queries, not null result metadata. Those queries do not seek the target's result.

The remaining visible retrieval concerns provisioned materials, aggregate base rates, and an older cited authority. A directory-search command explicitly excludes the labeling-artifact path; naming an exclusion is not a read of its contents. The earlier petition's May 2025 denial is identified as a different docket and explicitly not used as this petition's outcome. There is no evidence of the October 5 disposition surfacing prematurely. I retain the forward default: outcome material **false**, influence **not_applicable**, and suspicion **false**.
