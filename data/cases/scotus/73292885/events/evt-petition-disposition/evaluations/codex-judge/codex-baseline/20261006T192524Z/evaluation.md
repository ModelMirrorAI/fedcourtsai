# Evaluation: codex-baseline

## Outcome and numerical score

The cert-stage outcome is denied on October 5, 2026, with actual_granted = 0. The candidate predicted denied at P(any grant) = 0.012. Thus correct = 1 and Brier = (0.012 - 0)^2 = 0.000144.

The frozen context carries baseline, sal-v4, and Term 2025. I use the matching committed statpack's bracketed reached-baseline percentages and their weighted resolved denominators for every displayed Term before 2025: 2017–2024. The denominator is 11,580; the rate-weighted numerator from the rounded table is 592.925; segment_base_rate = 0.05120250431778929 and base_rate_basis = risk_set. Skill = 1 - 0.000144 / baseline^2 = 0.9450737326637662. The caption renders 10 of 10 Terms, so no shorter-window flag applies. Terms 2025 and 2026 are not pooled.

The candidate used unrounded companion-JSON rates in its own analysis, reporting 593/11,580. My slightly different baseline is explicitly reconstructed from the prompt-designated Markdown table, not a criticism of that calculation. Both numbers describe the committed denial-reweighted pack, not refreshed corpus state. A good score on this one denial does not establish calibration across cases.

## Reasoning quality: 0.90

The rationale separates petition allegations from established facts, explains why a sprawling question does not itself establish a square conflict, and distinguishes potential constitutional importance from the probability that this particular vehicle will attract review. It identifies the frozen band and version, makes the strictly-prior Term selection explicit, and avoids treating terminal relist and CVSG tables as forward transition hazards.

Its treatment of uncertainty is particularly sound: missing opposition text is not converted into a waiver or an invented respondent argument; unknown preservation and lower-court grounds remain unknown; an unusual filing chronology is not asserted to establish untimeliness. The analysis describes a narrower due-process question as potentially meaningful instead of assuming a related firearm precedent disposes of every theory. The staged log records the candidate's earlier-precedent search and a due-process excerpt lookup, although it exposes result digests rather than the underlying passages. I did not independently re-fetch that authority.

The main remaining limitation is the largely qualitative reduction from approximately 5.12% to 1.2%, without a fitted comparison or sensitivity analysis. The underlying opinion and opposition were not substantively assessed, so the vehicle judgment remains provisional. A correct denial does not prove the Court adopted any predicted legal rationale. These limits prevent a perfect grade but do not undermine the careful handling of the available evidence.

The score grades reasoning.md alone. The separate Court forecast and quantitative claims are unscored here, and their accuracy does not feed reasoning_quality. There is no cert vote score or semantic grade. The optional independent stakes assessment is omitted.

## Leakage and input vintage

The log and frozen context say forward; logged calls occur September 16, before the October 5 denial. Visible web targets are general authorities and a specific pre-decision opposition PDF, not this petition's subsequent disposition. The precedent search is date-bounded to June 2024. No reasoning passage presupposes the actual outcome. Outcome material is assessed false, influence not_applicable, and leakage_suspected false.

Capture coverage is 25/32 = 0.78125. Seven web rows are unobserved, three without visible query text. The candidate's statement that attempts produced no usable response is its own account; the unobserved markers do not independently prove that. The grade does not turn missing telemetry into affirmative evidence of empty results.

The candidate's baseline is dated September 16. The evaluator's snapshot is dated October 5 and includes the denial; it cannot establish what the candidate saw. All candidates describe unavailable opposition text at forecast time, while the evaluator manifest records nonempty OCR text fetched October 2. This later enrichment is not charged against the earlier analysis. No fresh corpus or external case lookup was performed for this evaluation.
