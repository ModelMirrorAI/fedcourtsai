# Evaluation: claude-baseline

## Outcome and numerical scoring

This is cert, not merits. The supplied outcome is denial on October 5, 2026, `actual_granted = 0`, with no noted dissent and no recorded votes. claude-baseline's `denied` prediction is an exact match, so `correct = 1`. Its 0.30 probability includes the requested summary mootness vacatur, and the Brier loss is `(0.30 - 0)^2 = 0.09`.

The frozen prediction context supplies `elevated`, `sal-v4`, and Term 2025. That version matches the committed statpack's heading; no band is re-derived from the decided docket. The bracketed reached rates for every displayed prior Term are: 2017 17.5%/400; 2018 15.9%/347; 2019 13.8%/334; 2020 16.1%/397; 2021 20.5%/342; 2022 19.0%/300; 2023 17.5%/354; 2024 17.9%/336. Pooling gives 484.386 divided by 2,810, or `segment_base_rate = 0.172379359430605`, on the `risk_set` basis. The numerator is reconstructed from rounded displayed percentages, not an exact grant count, and the pool is a denial-reweighted live/historical-slice estimate. The caption renders all 10 of 10 Terms, of which 2025 and 2026 are excluded; no truncated-window flag is needed. This is an artifact-based calculation, not a claim about a newly refreshed corpus.

The denial baseline loss is approximately 0.02971464356, so `brier_skill_score = 1 - 0.09 / 0.02971464356 = -2.028809678474534`. Correctly choosing the modal label coexists with a worse loss than the baseline on this single outcome; no broader performance inference follows.

## Reasoning quality: 0.82

The rationale recognizes the procedural target and addresses all four government objections rather than treating the underlying habeas issue as the question the Court must decide. In particular, it gives weight to petitioner-initiated early termination and the government's opposition while identifying the response request and the possible summary remedy as countervailing signals. It distinguishes the second recorded distribution from a genuine completed-conference relist, uses the correct frozen-band prior-Term baseline, and explicitly discloses both the missing reply and the limitations of its legal searches. It does not turn zero search hits into proof that no competing authority exists.

Several adjustments nonetheless rely on asserted practice rather than demonstrated conditional evidence: the estimated effect of a response request, the Court's supposed degree of deference to the government on vacatur, and the weight of elite counsel. The claimed offset between a mechanically elevated band and the unpriced response request is plausible but unmeasured. Describing the timing as textbook or clean also needs qualification because the opposition disputes when mootness arose and whether it was voluntarily caused. The reasoning acknowledges those objections, but its upward adjustment to 30% is still a judgmental synthesis rather than a supported subgroup rate. The account of precedent rests partly on titles and remembered practice, not retrieved holdings; no finding that those authorities are false is necessary to recognize that evidentiary limit.

The supplied petition corroborates the chronology and the government's agreement to early termination, but neither that agreement nor the eventual unexplained denial resolves the equitable controversy for this evaluation. This score grades the rationale's soundness and uncertainty handling, not its forecast document, auxiliary claims, or mere success in selecting denial.

## Leakage and scope

The log records `forward` and full capture coverage: 31 of 31 results marked captured. Calls and prediction occurred September 17, 2026, before the October 5 denial. The external queries concern GVR priors, Munsingwear authorities, doctrinal percolation after Jones, and the indexed August 6, 2025 lower-court decision under Bell v. Streeval. That lower decision is not the Supreme Court petition's outcome. Visible retrieved dates are all before resolution, including June 30, 2026 for a different case. The reasoning does not presuppose a decided petition. Outcome-material retrieval is false on this evidence, influence is `not_applicable`, and `leakage_suspected` is false. Result digests are audit markers rather than full texts; the assessment rests on the dated query targets and staged prose, not an independent rerun of those searches.

Votes are unscored at cert, and no semantic set applies. The forecast document was read for context; mechanical claim scores and provenance stamps remain for the harness. No independent big-case assessment is supplied.
