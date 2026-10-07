# Evaluation: codex-baseline

## Outcome and numerical scores

This cert petition was denied on October 5, 2026; the supplied outcome records `actual_granted = 0`. codex-baseline predicted denial on September 16 with P(grant) = 0.36. Thus **correct = 1**, and **Brier = 0.1296 = (0.36 - 0)^2**.

The prediction's frozen Term 2025, elevated band, and sal-v4 version select the matching statpack table's bracketed reached rates. The eligible rendered Terms are 2017–2024: 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336 (rate/weighted resolved denominator). Pooling gives 484.386/2,810 = **0.172379359430605**, with `base_rate_basis = risk_set`. This is an approximation from rounded committed-pack, denial-reweighted live/historical-slice rates, not an exact grant count or a claim of current corpus freshness. The caption renders all 10 of its 10 Terms; excluding the scored Term and 2026 leaves eight eligible rows and no unrendered-Term discrepancy.

**Brier skill = 1 - 0.1296 / baseline² = -3.3614859370033293**. Despite the correct categorical call, its upward probability adjustment loses to the lower baseline on this denial. That realized loss does not by itself resolve whether the adjustment was reasonable ex ante or establish a cross-case calibration finding.

## Reasoning quality: 0.92

The analysis is careful about the information set and the distinction between substantive significance and certiorari suitability. It correctly anchors to the frozen risk set, excludes the case's own Term, discloses rounding, and treats pooled terminal relist/CVSG cuts as descriptive rather than forward transition probabilities. It recognizes that the response cycle explains the two distributions without assuming repeated merits deliberation.

The strongest feature is balanced treatment of the vehicle dispute. The rationale identifies the BIO's documentary waiver support and nonfinality objection while describing the reply's amended-pleading answer as a reason to reduce, not erase, the discount. It distinguishes an unexplained order and discretionary appellate review from a developed appellate merits holding. It also explicitly refuses to transfer the earlier due-process votes mechanically to a different constitutional question. The provisioned petition and BIO confirm the competing vehicle arguments; the candidate's discussion of separately fetched appendix and reply material is supported as retrieval activity by its log, although those full fetched bodies are not staged for this evaluator.

The principal limitation is the magnitude of the discretionary uplift from approximately 17% to 36%. The case-specific reasons are articulated, but no measured likelihood ratios or comparable-case model quantify them. Consequently the precision of the point estimate should not be mistaken for empirical calibration. The correct label is not the basis for the high qualitative score, and the silent denial does not establish that preservation or finality was the Court's actual reason.

## Leakage and scope

The log records forward mode and 31 captured calls among 35 marked calls. Four web rows are unobserved: I do not accept null dates or the prose's unsuccessful-search claim as proof that these calls returned nothing. Their recorded targets concern general cert rules and a fixed pre-resolution reply PDF. Captured shell-style queries fetch that reply and the petition appendix, both before this event's disposition; the appendix's state decisions and the separate Lynn/BNSF denial are legitimate antecedent context, not this petition's outcome. Nothing indicates an already-decided case was provisioned forward. Influence is `not_applicable`, and leakage is not suspected with the capture limits disclosed.

The forecast document remains unscored; structured quantitative claims belong to the harness. No cert votes or semantic claims are graded, and no independent big-case assessment is supplied.
