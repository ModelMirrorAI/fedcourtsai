# Evaluation: codex-baseline

## Result and scoring

This is a cert-stage petition-disposition cell. The provisioned outcome records denial on October 19, 2026, with `actual_granted = 0`. The candidate predicted `denied`, so `correct = 1`. Its grant-family probability was 0.16; the Brier score is `(0.16 - 0)^2 = 0.0256`.

The scored prediction froze an elevated band under sal-v4 in Term 2026. The segment base rate, its basis, and Brier skill are therefore left to the harness; comparison belongs against the stamped segment base rate, not a separately computed evaluator anchor. Votes are unscored on cert cells. No mechanical claim scores or semantic grades are supplied.

## Reasoning quality: 0.90

The rationale distinguishes a procedural right to notice from an entitlement to custody, addresses the opposition's specific preservation objection, and treats the competing accounts of kinship and fraud as disputed rather than established. The opposition's discussion of App.48a n.27 supports identifying waiver as a serious vehicle concern. The candidate also explains the petition appendix's truncation and why the opposition's quotation cannot substitute for independently reading the complete underlying passage.

The analysis appropriately separates two docket distributions from two substantive conference considerations and avoids treating attention signals as independent multipliers of an already elevated anchor. Its small final adjustment is transparent, though judgmental rather than empirically estimated. The unresolved preservation dispute and limited independent verification of the underlying authorities prevent a perfect grade.

The denial is consistent with the forecast, but supplies no explanation establishing that the Court adopted the waiver objection or any party's merits position. This grade concerns the soundness of `reasoning.md`, not the accuracy of the separate forecast document or structured claims.

## Leakage and significance

The prediction and its log are forward-mode, dated September 30, before the October 19 resolution. I reviewed all 31 logged calls. Twenty-eight have captured results; the three unobserved web calls concern general authorities or procedural rules, not this petition's outcome. The candidate's statement that searches returned nothing is not independently established by those uncaptured rows. The visible query targets and prose nevertheless show no retrieval of this petition's disposition and no mis-provisioned decided case: `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`.

My independent significance assessment is 0.65: the caregiver-notice question has potentially broad implications, and the individual and international stakes are substantial, but the recorded denial makes no nationwide merits holding. This same case-level assessment is used for every candidate.
