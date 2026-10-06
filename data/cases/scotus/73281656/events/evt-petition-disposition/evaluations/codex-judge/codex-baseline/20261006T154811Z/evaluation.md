# Evaluation: codex-baseline

## Outcome and numerical scores

The supplied cert outcome is **denied**, resolved October 5, 2026, with `actual_granted = 0`. The predicted label is also `denied`: correctness is **1**. The forecast's **0.13** grant probability produces Brier loss **0.0169**.

The scored prediction freezes **baseline**, **sal-v4**, and Term **2025**. The committed Markdown statpack matches that version. Pooling the bracketed baseline reached rates for displayed Terms **2017–2024**, weighted by their resolved denominators, gives **592.925 / 11,580 = 0.05120250431778929**. The numerator reflects rounded displayed percentages, not an exact count. I exclude 2025 and 2026; the table displays 10 of 10 Terms, so no rendered-window divergence needs a flag. This is a `risk_set` baseline, not the terminal-band rate and not a rate selected from the evaluator's context.

Skill is `1 - 0.0169 / 0.05120250431778929^2 = -5.446207763766336`. The candidate's reported exact-JSON anchor of approximately 0.051209 differs slightly because my calculation uses the contract's displayed Markdown percentages. That rounding distinction is not a substantive population or version mismatch. Correctly choosing the modal label did not beat the lower-probability baseline on this denied petition. The result is an event-level loss comparison, not a claim about long-run calibration. I consulted the committed statpack, not a refreshed corpus; this evaluation's case snapshot is dated October 5, while the prediction froze September 15, 2026.

## Reasoning quality: 0.92

The rationale carefully distinguishes allegations from established facts. It addresses both questions presented, explains why a disagreement about cumulative prejudice might matter, and then engages the opposition's preservation objection and alternative characterization of the lower court's actual analysis. The cited opposition pages 16–22 support the existence of those contested vehicle issues. The discussion does not convert the respondent's characterization into a proven jurisdictional defect. It also acknowledges the missing reply and the limits of not independently reading the appendix or underlying appellate briefs.

The proposed-order discussion separates troubling process allegations from an uncontested legal conflict, accounting for the parties' competing descriptions of reconsideration and the comparator's procedural differences. The probability rationale explicitly avoids treating capital stakes as grant probability, terminal relist counts as forward hazards, or correlated marginal cuts as independent multipliers. It openly reports failed external verification rather than asserting it occurred.

The residual weakness is quantification: the increase from approximately 5.12% to 13% remains a subjective judgment, without a matched historical cohort to establish its size. Some doctrinal comparisons necessarily rest on the parties' submissions. Those are real limitations, but the record-based analysis and uncertainty treatment are strong. The larger realized Brier loss is not itself a reason to lower analytical quality. Nor does an unexplained denial establish that the Court accepted the respondent's legal arguments.

Only `reasoning.md` informs this qualitative grade. The forecast document and quantitative claims remain unscored here. Vote accuracy and semantic grades are omitted because the event is cert; mechanical claim scores remain the harness's responsibility.

## Leakage

The log reports **forward**, with **32/34 captured results**. The September 16 prediction precedes the October 5 resolution. Its two unobserved web calls concern general Thornell precedent, so the absent dates or digests cannot establish that they returned nothing; the queries nevertheless do not seek this petition's disposition. Other logged reads concern supplied case documents, schemas, and committed statistics, with a general-precedent lookup also recorded. The reasoning distinguishes the old cert proceeding and an extension grant from the present petition. Neither the logged queries nor the analysis reveals this event's outcome. I record influence `not_applicable`, no observed outcome material, and `leakage_suspected = false`.
