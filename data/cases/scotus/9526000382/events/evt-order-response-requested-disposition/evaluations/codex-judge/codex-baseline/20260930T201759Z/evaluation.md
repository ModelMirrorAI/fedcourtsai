# Evaluation: codex-baseline

## Outcome and scores

The event is interim. The September 29, 2026 outcome is denied, actual_granted = 0. The provisioned September 30 snapshot records denial by Justice Sotomayor without prejudice to applicants again seeking relief once state remedies are exhausted. codex-baseline's denied label is correct (1). Its 0.40 grant probability yields Brier = (0.40 - 0)^2 = 0.16.

## Reasoning quality: 0.90

The analysis carefully separates the applicants' representations from independently established facts. It identifies the pending appellate stay motion, the nonfinal posture and uncertain route to immediate intervention, while explaining the possible constitutional injury from the religious-censure directive. It expressly recognizes the missing response, the respondent's interest in civil-court access, and the difference between general stay factors and jurisdiction. The order's exhaustion language supports the main procedural concern; it does not decide the merits of the religious-liberty theories.

The base-rate discussion distinguishes an unconditioned application pool from the selected response-requested population, states coverage limitations, and labels the upward adjustment subjective. The chief weakness is calibration: the move from roughly 10.5% to 40% has no conditioned empirical support, and the strong procedural obstacles leave substantial uncertainty about the size of that adjustment. This does not make the number irrational or justify equating the reasoning score with the Brier score. Clear counterarguments, sourcing limits and conditions that would move the estimate justify a high reasoning score despite the larger realized squared error. General authorities were not independently re-retrieved by this evaluator.

This grade concerns reasoning.md only. The forecast document and quantitative claim block are unscored here, including their referral and amicus forecasts. Claim scoring belongs to the harness.

## Baseline and scope

No segment_base_rate or brier_skill_score is written: this is an interim cell and the harness computes both. base_rate_basis is null. The committed statpack supports a strictly-prior 2016–2025 pool for frozen application-Term 2026: 31 grants / 296 substantive resolutions, above the pooled floor of 50. No refusal is apparent in the displayed counts, but the post-run stamped value is not yet available. These are committed-artifact counts rather than a live corpus refresh. The pool selects machine-matchable dispositions, counts withdrawals/dismissals as ungranted, reads mixed orders denial-first, and has uneven coverage (972 unparsed applications in 2024). It is broader than the escalation-selected scored population and is not response-request conditioned.

Vote accuracy and semantic grades are inapplicable on this interim cell. The optional big-case field is omitted because no independent assessment preceded exposure to candidate scores.

## Leakage

The log records forward mode and September 27 activity, before the September 29 disposition. Local reads and general-authority lookups are consistent with the disclosed analysis; no query targets this application's eventual outcome. Capture coverage is 31/34. The three unobserved web rows concern older Yeshiva precedent: their missing results do not verify the candidate's claim that the searches supplied nothing, but the queries themselves do not indicate target-outcome retrieval. Nothing suggests the case had already been decided when predicted. Retrieved outcome material is false, influence is not_applicable, and leakage_suspected is false.
