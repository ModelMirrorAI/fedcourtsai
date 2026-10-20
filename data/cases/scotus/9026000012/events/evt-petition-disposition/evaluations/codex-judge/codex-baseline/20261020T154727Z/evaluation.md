# Evaluation: codex-baseline

## Outcome and mechanical score

This is a cert-stage cell. The authoritative outcome records a plenary grant on October 19, 2026: `actual_disposition = granted`, `actual_granted = 1`. The provisioned October 19 snapshot records a grant limited to whether the targeted racial group must suffer aggregate disparate impact relative to its applicant-pool share.

codex-baseline predicted denial with P(any grant) = 0.22. The exact disposition match is **0**, and the Brier score is **(0.22 - 1)^2 = 0.6084**. No merits judgment or cert-vote accuracy is scored. No semantic set is declared on this cert event. Structured claims and the separate forecast document are not graded here.

The prediction froze an `elevated`, `sal-v4`, Term 2026 context. Its baseline, basis, and skill are the harness's to stamp; I leave those fields absent and refer only to the stamped segment base rate. The evaluator's terminal `high` band does not replace the prediction's frozen band. No independent baseline was pooled for this evaluation.

## Reasoning quality: 0.86

The grade concerns `reasoning.md` alone. The analysis carefully distinguishes disagreement about aggregate versus individualized discriminatory effect from the broader and potentially misleading claim that intent alone suffices. It compares the petition and opposition, describes a primary-source check of the separate Sargent decision, and identifies the alternative intent ground as a prudential vehicle concern rather than a categorical bar. Its distinction between pre-conference rescheduling and a genuine post-conference relist is a useful guard against overreading the distribution count. It also keeps correlated docket signals and terminal-state base-rate descriptions from becoming independent multipliers.

The weakness is the weight assigned to vehicle problems: after identifying a substantive, newly deepened conflict and explaining how review could lead to remand, the analysis gives only a modest upward probability adjustment. The supplied grant shows that those obstacles did not prevent review in this instance. Its limited question also fits the analysis's distinction between aggregate impact and sequencing. Neither observation establishes the eventual merits rule, and the unexplained grant does not tell us the Justices' motives. The precise probability adjustment remains judgmental rather than empirically supported. A wrong modal outcome therefore earns the mechanical miss without erasing the rationale's substantial analytical strengths.

## Leakage and information boundary

The prediction and captured transcript identify forward mode, using a September 27, 2026 snapshot, before the October 19 resolution. I assessed the candidate's frozen context rather than treating the evaluator's uncensored snapshot as the candidate's information set. The 36-call transcript has 34 captured results and two unobserved general-doctrine web calls. Those unobserved calls cannot establish that their results were empty; their queries nevertheless concern Arlington Heights generally, not this petition's result. The separate Sargent authority predates the forecast. No logged query or reasoning passage reveals this petition's eventual disposition or reads it from an already-decided snapshot. Thus `retrieved_outcome_material = false`, influence is `not_applicable`, and leakage is not suspected.

## Stakes

My case-level significance assessment is **0.80**: the aggregate-impact requirement has national consequences for proof of intentional discrimination in selective public-school admissions, while the specific lottery and pleading posture constrain this vehicle. This is independent of whether denial or grant was more probable and does not infer a merits holding from the grant.
