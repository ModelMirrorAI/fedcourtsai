# Evaluation: claude-baseline

## Outcome and quantitative score

This is a cert-stage event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot also records “Petition DENIED.” The September 17 prediction names `denied`, so exact-label correctness is **1**. Its grant probability is **0.14**, giving Brier **(0.14 - 0)^2 = 0.0196**.

The candidate froze `elevated`, `sal-v4`, and Term **2025**. These match the committed statpack's sal-v4 table. I use the bracketed **reached** population, not the terminal rate and not the evaluator's terminal context. All displayed prior-Term rows are pooled: OT2017–OT2024. In ascending Term order their printed rates and weighted resolved denominators are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336. The weighted numerator is 484.386 and denominator 2,810, yielding **0.17237935943060498**, on a `risk_set` basis. The numerator is an approximation from printed percentages, not an integer grant count. The table renders 10 of 10 Terms; there is no hidden-window divergence. OT2025 and OT2026 are excluded.

Against this baseline, Brier skill is **1 - 0.0196 / 0.17237935943060498^2 = 0.3403925589099902**. This is one cell's comparison against a denial-reweighted committed-pack estimate, not an estimate of general predictive performance or a fresh corpus census. No live corpus refresh was performed.

## Reasoning quality: 0.82

The analysis connects a matched risk-set anchor to concrete cert-stage considerations. It distinguishes a redistribution following a response request from a substantive relist after full briefing. It addresses competing considerations rather than equating an ideologically salient question with a likely grant: amici, dissents below, and the response request favor attention, while an unestablished circuit conflict, the challenged provision's limiting construction, an alternative statutory ground, preservation, and the facial record weigh against this vehicle. The provisioned opposition contains the limiting-construction and preservation arguments the candidate discusses. The candidate identifies the missing reply and discloses where its comparisons are memory-based or second-hand.

The principal limitations are evidentiary and inferential. Assertions about the Court's appetite, typical disclosure grants, and recent comparable denials are not independently substantiated in the material the candidate successfully retrieved. The analysis gives a separate downward adjustment to the respondent's characterization of NRSC despite not obtaining its opinion text. It sometimes states disputed vehicle objections more firmly than their status as opposition arguments warrants, and the numerical adjustment remains judgmental rather than empirically estimated. Those limitations reduce the grade despite the correct label and low Brier loss.

An unexplained denial does not establish that the Court adopted these objections or resolved the underlying constitutional questions. The quality grade concerns only the analysis in `reasoning.md`, not whether particular claims or passages in the forecast proved accurate. The forecast document was read for context but not scored; quantitative claims remain for the harness. Cert votes and semantic propositions are not scored. No independent big-case score is supplied.

## Leakage assessment

The harness log identifies **forward** mode. The prediction and all logged activity occurred September 17, before the October 5 resolution. All 29 logged calls carry `captured` markers. The lower-court search returned a September 9, 2025 opinion; the generic corpus query carries September 17, 2026; the NRSC search carries June 30, 2026. These are not evidence of this petition's eventual denial. The log also contains a lookup of another prediction artifact: I did not follow that path or attempt to identify its author, and the available query/prose does not expose this case's outcome.

Nothing in the staged reasoning or retrieval note reads this petition as already decided. Thus `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is an assessment of the available logged queries, dates, capture markers, and prose, not a claim to have reconstructed result bodies from their digests. No mis-provisioned-forward evidence was found.
