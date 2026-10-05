# Evaluation: codex-baseline

## Outcome and scores

The supplied **cert** outcome is `denied`, resolved October 5, 2026, with binary grant value **0**. codex-baseline's `denied` label is correct: **1**. Its probability **0.01** gives Brier score **0.0001**.

The frozen prediction context is **baseline / sal-v4 / Term 2025**, matching the heading of the committed `metrics/statpack.md` band table. Use the **risk_set** basis and the bracketed reached values, not the terminal baseline band or the evaluator's decided-docket context. Pooling all rendered prior Terms **2017–2024** gives **592.925 / 11,580 = 0.05120250431778929** from the displayed percentage/denominator pairs: 5.7%/1,271; 5.9%/1,312; 5.8%/1,192; 5.6%/1,500; 4.5%/1,739; 4.6%/1,399; 4.6%/1,524; and 4.7%/1,643. Brier skill is **0.961856758794282**.

The table renders all 10 of its 10 Terms; 2025 and 2026 are excluded because they are not strictly prior. There is no window-truncation or version-mismatch flag. The numerator is percentage-reconstructed, not an integer grant count. The candidate reports 593/11,580 from the underlying exact JSON rates; the very small difference from my mandated rendered-table calculation is rounding, not a substantive baseline error.

This calculation uses the committed pack's live/historical-slice, denial-reweighted estimates, not a fresh corpus query. The prediction context dates its snapshot September 16, 2026. No present-day corpus freshness or population-wide predictive performance is inferred.

## Reasoning quality: 0.94

The rationale is unusually well tied to the supplied record. It distinguishes the government's respondent status from a federal petitioner, one distribution from a completed relist, and a response waiver from a merits concession. It expressly limits its no-conflict inference to the petition actually supplied rather than claiming an exhaustive nationwide search.

Its vehicle analysis is supported by the provisioned appellate appendix: pages 13a–15a apply deferential review to documentary factfinding, reserve legal questions for de novo review, and discuss an alternative predominantly factual mixed-question rationale. Pages 18a–19a discuss expert testimony, the late reliability objection, and the rejection of one non-development rationale despite affirmance on other grounds. These details directly test the petition's proposed documentary-only vehicle rather than simply repeating its framing.

The statistical reasoning also separates a reached-band prior from terminal procedural aggregates and avoids treating the latter as prospective transition probabilities. The rationale acknowledges truncated materials and unsuccessful external verification. Those qualifications make its source claims appropriately bounded.

The residual limitation is that 1% remains a judgmental rather than empirically fitted adjustment; neither a matched comparison set nor a comprehensive conflict review establishes its precise magnitude. That does not invalidate the direction of the adjustment. The subsequent unexplained denial is consistent with the rationale but cannot verify what motivated the Court. The score reflects `reasoning.md` alone, not the forecast document or the outcomes of auxiliary claims.

## Leakage and scoring boundaries

The harness log records **forward** mode and a September 17 prediction, before the October 5 denial. **31/48 calls have captured results**; **17 web calls are unobserved**. I assess those unobserved calls from their queries rather than accepting absent dates or digests as proof of empty results. Their targets are general Rule 52, civil-rules, and Supreme Court rules resources, not searches for this petition's resolution. The candidate's report of unusable web results is a disclosure, not independent telemetry confirmation.

The other visible calls read the provisioned case, aggregate statpack data, and helpers, or attempt general-rule retrieval. The statpack-only history lookup is not a search for this case's outcome. Nothing in the logged queries or reasoning presents the petition as already decided. Accordingly, `retrieved_outcome_material = false`, influence is `not_applicable`, and leakage is not suspected.

No cert vote score, judgment score, or semantic grade is supplied. The forecast is context only; the harness scores quantitative claims and stamps provenance. No independent big-case score is supplied.
