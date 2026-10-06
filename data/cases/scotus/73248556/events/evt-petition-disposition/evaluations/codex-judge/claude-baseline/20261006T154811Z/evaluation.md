# Evaluation: claude-baseline

## Outcome and numerical scores

The supplied cert-stage outcome records `denied` on October 5, 2026 and `actual_granted = 0`. claude-baseline predicts denial with P(any grant) = 0.07. Exact-label correctness is **1**; Brier loss is **(0.07 - 0)^2 = 0.0049**. The outcome establishes the disposition, not the Court's unstated reasoning.

The prediction's frozen context names federal band, sal-v4, and docket Term 2025. I use the matching committed statpack's bracketed federal `reached` rows, pooled over all displayed Terms strictly before 2025: 2017–2024. In ascending order, rates/weighted denominators are 76.5%/17, 43.5%/23, 88.5%/26, 65.9%/41, 72.7%/11, 89.5%/19, 86.2%/29, and 60.0%/15. The resulting rate is **132.039/181 = 0.7294972375690608**, with `risk_set` basis. Skill is **1 - 0.0049 / 0.7294972375690608^2 = 0.9907923505488742**. The implied numerator uses the table's rounded rates and is not an exact observed grant count.

The table renders 10 of 10 available Terms; its 2025 and 2026 rows are excluded. No frozen-version mismatch or rendered-window truncation applies. The committed statpack header provides no corpus-wide pull vintage; these calculations describe that supplied table, not current remote-corpus state. No live corpus query was made by this evaluator. One successful cell is not evidence of calibration or general performance.

## Reasoning quality: 0.88

The rationale distinguishes the narrow conditional GVR request from plenary review of the broader constitutional question. It correctly uses the approximately 73% strictly-prior federal anchor and makes its substantial downward adjustment explicit. Its treatment of Mitchell as the post-companion comparator, while separately dating Doucet and Cockerham before the companion decision, is more discriminating than treating all three as interchangeable subsequent denials. It also identifies possible alternative vehicles, a later hold-and-remand path, and uncertainty from not reading the full companion opinion. The provisioned petition and opposition support the core account of the requested relief and competing positions.

The main limitation is excess certainty in parts of the adjustment. The absence of an intervening decision favoring the government is treated almost as eliminating any reason for reconsideration, while the petition itself frames the GVR request around possible effects on the lower court's analysis. One comparator denial is persuasive forecasting context, not proof that every such route is foreclosed. The sweeping statement that every as-applied petition has been denied exceeds the finite searches and exemplars described. The residual path probabilities are transparent judgments rather than empirically estimated conditional rates. The rationale acknowledges enough of these uncertainties to remain strong, but not definitive. I have not independently repeated its external searches or verified every reported opinion passage.

The qualitative grade applies only to `reasoning.md`, not to the separate forecast or mechanical claims. Correctness of the headline label does not itself earn a higher reasoning grade. Cert vote scoring and semantic grading are inapplicable; mechanical claim scores remain for the harness.

## Leakage

Both the frozen context and retrieval log say forward. All 45 calls carry captured-result markers and September 16 timestamps, preceding the October 5 resolution. Visible retrieval concerns the companion decision, earlier comparator denials, corpus priors, and pending petitions. An initial CourtListener docket query includes this petition's number; broader litigation searches also could surface its pending status. Neither is prohibited in a genuinely open forward cell.

The dated retrieved-document metadata does not reach the resolution, and the reasoning consistently treats Hembree as unresolved. The log contains result digests rather than full source bodies, so a null document date is not independently proof of an innocuous source. Nevertheless, query scope, timestamps, and staged prose provide no evidence of this petition's eventual denial entering the prediction. Assessment: outcome material not shown, influence `not_applicable`, leakage suspicion false.
