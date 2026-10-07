# Evaluation: codex-baseline

## Outcome and quantitative scores

The supplied cert-stage outcome records denial on October 5, 2026, with `actual_granted = 0`, consistent with the October 5 snapshot's denial entry. codex-baseline predicted `denied` and P(any grant) = 0.005. Thus **correct = 1**, and **Brier = (0.005 - 0)^2 = 0.000025**. The bare denial does not reveal the Court's reasons or endorse an immunity holding.

The scored prediction freezes `baseline` under `sal-v4`, Term 2025. The committed statpack's matching table supplies the bracketed reached rates and denominators. Pooling all rendered prior Terms 2017–2024 gives, in ascending Term order: 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. The weighted denominator is 11,580; **segment_base_rate = 0.05120250431778929**, with `base_rate_basis = risk_set`. This is an approximate denial-reweighted rate reconstructed from rounded displayed cells. Skill = 1 - 0.000025 / baseline^2 = **0.9904641896985705**.

The table renders 10 of 10 available Terms, so there is no hidden-window divergence. The case's own Term 2025 and later Term 2026 are excluded. I use the prediction's frozen band and Term, never the evaluator's terminal context. The figures describe the supplied committed statpack, not a live corpus refresh; no corpus-blob vintage is asserted. The skill figure is descriptive of this one resolved event, not a performance claim across cases.

## Reasoning quality: 0.93

The rationale distinguishes what is observed from what is inferred. It treats a June distribution for the September conference as one distribution, not as a summer relist; separates an ordinary response deadline from a Court-requested response; and uses the correct versioned prior-Term reached-band baseline with an explicit rounding caveat. It avoids turning terminal relist and CVSG buckets into forward transition probabilities.

The case-specific analysis is particularly careful about the record's limitations. It distinguishes the proposed connection between recusal and immunity from an established exception, identifies a lack of demonstrated conflicting holdings, and explains why preservation and available remedies can obstruct review independently of the abstract question's importance. Most importantly, it recognizes the actual conflict between the petition's solely-immunity account and the opposition's alternative-ground account. The supplied petition, pages 7–8, and opposition, pages 5–10, support that characterization. It treats the opposition's position as an adversarial submission rather than claiming to have independently verified the lower decisions. The alleged misconduct is not taken as proven, and a possible argument for review is acknowledged before the downward probability adjustment.

The score is not perfect: the reduction from roughly 5.12% to 0.5% remains a judgmental adjustment rather than a fitted estimate, and missing underlying opinions and pleadings limit certainty about preservation and alternative grounds. The candidate makes those limitations explicit. Its smaller Brier loss does not itself earn a higher reasoning grade; the score rests on analytic specificity, proper conditioning, and evidentiary restraint in `reasoning.md`.

The forecast document was read only for context. No quantitative claim scores, semantic grades, or cert-vote accuracy are assigned here. The optional independent significance assessment is omitted.

## Leakage assessment

The prediction and forward log predate the October 5 denial. Of 29 calls, 27 have captured results; two web calls are unobserved, giving capture coverage 0.9310344827586207. The latter queries concern historical immunity authority and a historical United States Reports PDF, not this litigation. Although the candidate says they returned no usable content, that absence is not independently observable and is not credited as an empty result. Their benign query scope is what supports the assessment.

Other external calls concern Mireles v. Waco, not this petition's subsequent history. Local reads are provisioned case materials, the statpack, instructions, schemas, and validation-related code. The file-discovery query that names the forbidden labeling path does so to exclude it; this is not a read of labeling contents. Neutral `other` tool classes do not count as suspicious merely because the harness collapsed their names.

Nothing in the logged queries, recorded dates, or rationale reveals this petition's outcome before prediction. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This assessment uses the predictor's chronology and information-set account, not the evaluator's later snapshot as a reconstruction of its baseline.
