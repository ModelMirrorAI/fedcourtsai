# Evaluation: claude-baseline

## Outcome and scoring scope

This is a cert-stage evaluation of the September 16, 2026 forward prediction. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot likewise records "Petition DENIED." A correct denial forecast does not establish why the Court denied review. No explanatory opinion or individual votes are supplied.

Only `reasoning.md` contributes to reasoning quality. The pointed-to `predicted_reasoning.md` was read for context, not scored. Quantitative claims are left to the harness; no claim scores, semantic grades, or cert-stage vote accuracy are written.

## Baseline and provenance

The prediction freezes `band = baseline`, `salience_version = sal-v4`, and Term 2025. The committed `metrics/statpack.md` heading matches sal-v4, so the basis is `risk_set`, using the bracketed baseline-band reached rates, not terminal rates or this evaluator's context. Every displayed strictly prior Term is included: 2017–2024. The table renders all 10 of its 10 Terms; 2025 and 2026 are excluded, so there is no rendered-window truncation to flag.

The displayed rate/weighted-denominator pairs are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Their resolved-weighted pool is 592.925 / 11580 = 0.05120250431778929. The numerator is derived from rounded displayed percentages, not an integer grant count. This is the committed live/historical-slice, denial-reweighted estimate, not a fresh corpus census. No corpus query was made, and corpus-wide refresh vintage was not established. Case-outcome provenance is the provisioned October 5 snapshot and outcome artifact.

Skill is `1 - Brier / baseline^2` because the observed binary is zero. These are descriptive scores for one resolved event, not evidence of calibration or population-level performance.

## Quantitative result

The candidate named `denied`, matching the outcome: **correct = 1**. Its grant probability was 0.004, giving **Brier = 0.000016** and **Brier skill = 0.9938970814070851**.

## Reasoning quality: 0.86

The rationale is substantially grounded in the provisioned petition and procedural history. It distinguishes an absent opposition from an absent recorded waiver, identifies the constitutional-preservation problem from the petition itself, separates the grant-family anchor from grant-side routes, and explains why a diffuse, individualized challenge supplies a weaker vehicle than the average reached-baseline petition. The correct prior-Term risk-set selection and explicit adjustment support the low probability without simply equating baseline status with inevitable denial.

Its strongest feature is the uncertainty section: the lower-court order and appendix were unavailable, the petition is only one party's account, and the retrieved corpus comparators were not useful. It does not pretend those unrelated priors establish a fitted probability.

Some formulations exceed that evidence. The main adjustment speaks categorically of an adequate and independent procedural ground, although the missing appellate opinion prevents establishing the ground's precise character; the later caveat mitigates but does not erase that overstatement. The unqualified statement that a GVR needs an intervening decision is also more categorical than the narrower, supportable observation that no specific GVR hook was identified. Terminal relist and originating-court aggregates are offered as corroboration without a clear warning against using selected terminal populations as live conditional rates. The adjustment to 0.4% remains judgmental rather than empirically calibrated. These limitations keep an otherwise strong analysis below the highest quality range. Denial confirms the label, not those inferred judicial reasons; forecast accuracy and claim probabilities are not folded into this qualitative score.

## Leakage

**Mode: forward; retrieved outcome material: false on the available evidence; influence: not_applicable; leakage suspected: false.** Capture coverage is **25/25**. The case-specific CourtListener docket lookup occurred September 16 and carries a retrieved document date of May 4, 2026. The retrieval note describes an unterminated docket last changed June 17, no entry results, and unsuccessful searches for the lower-court order. The general corpus lookup returned unrelated priors, according to the note. Nothing in the captured call metadata or reasoning shows this petition's October 5 denial was already known. Case-specific current-docket retrieval is allowed for a genuinely pending forward cell; it is not leakage merely because it goes beyond the baseline snapshot. The log supplies digests and metadata rather than the full returned bodies, so the finding is limited to the supplied evidence.
