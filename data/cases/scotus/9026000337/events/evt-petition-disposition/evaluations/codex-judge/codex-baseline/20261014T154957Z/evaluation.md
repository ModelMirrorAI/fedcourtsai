# Evaluation of codex-baseline

## Outcome and mechanical scores

The supplied cert-stage outcome is denied on October 13, 2026, with actual_granted = 0. codex-baseline predicted denied with P(any grant) = 0.015. Correct = 1 and Brier = (0.015 - 0)^2 = 0.000225. The disposition label matches exactly.

The prediction froze the baseline band, sal-v4, and Term 2026. Baseline and skill therefore belong to the harness; this evaluation refers only to the stamped segment base rate and leaves segment_base_rate, base_rate_basis, and brier_skill_score unwritten. Cert votes are unscored, semantic grades do not apply, and claim_scores remains harness-owned.

## Reasoning quality: 0.91

The rationale closely separates the petitioner's strongest argument from the reasons this vehicle might not attract review. It recognizes the substantive concern about guaranteed issuance followed by claim-time exclusion, while distinguishing novelty and model-law similarity from conflicting appellate holdings. It tests the petition's methodological characterization against Appendix A's contract and statutory reasoning rather than treating the petition as neutral fact. Importantly, it frames that assessment as a vehicle concern, not proof that the panel correctly interpreted Iowa law.

The certification discussion addresses an actual alternative request in the petition, pages 26-28, and notes its presentation on rehearing without asserting forfeiture. The staged log supports the reported retrieval of the historical Mckesson opinion; I did not independently retrieve that authority. The rationale's qualified analogy is more discriminating than simply asserting that state-law questions cannot warrant review. Its treatment of response waiver and absent recorded amicus activity as modest signals is appropriately cautious. It also distinguishes terminal statistical cuts from a forward risk-set anchor and explicitly describes its numerical adjustments as judgmental rather than measured hazards.

Remaining limitations are the absence of a quantified case-adjustment method and incomplete independent substantiation of the broader regulatory and comparative-law picture. The exact 1.5% value is plausible within the analysis but is not established by a single successful prediction. I have not independently recalculated the historical pack or verified every cited precedent. These limits prevent a perfect grade without outweighing the document's careful evidence handling.

The October denial corroborates the disposition call, not the Court's unstated reasons. reasoning_quality grades reasoning.md alone; the forecast document and quantitative claim predictions receive no separate qualitative score and do not contribute to it.

## Leakage assessment

The log records forward mode and 31 September 27 calls, before the October 13 disposition. Twenty-nine calls have captured results; two general rules-related web calls are unobserved. The latter are assessed by their visible query and URL, not credited as returning nothing merely because the candidate says they were unusable. The other external retrieval concerns a historical case, while local reads concern the provisioned record and aggregate context. There is no visible evidence that this petition's own disposition surfaced as already decided. Thus retrieved_outcome_material is false, influence is not_applicable, and leakage_suspected is false, with the stated result-visibility limitation.

## Stakes

My independent case-level significance assessment is 0.22, applied uniformly to all candidates. The provisioned question presents real insurance-coverage stakes and possible effects in analogous state regimes, but the record does not demonstrate a nationwide split or a broad merits holding. This assessment is not a calculation of agreement with the candidate's own score.
