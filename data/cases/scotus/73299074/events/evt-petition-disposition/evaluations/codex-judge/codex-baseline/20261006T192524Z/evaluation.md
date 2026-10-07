# Evaluation: codex-baseline

## Outcome and quantitative scores

The provisioned event is cert-stage, although the underlying filing is an original mandamus petition. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`; the October 5 snapshot independently contains "Petition DENIED." The predicted label, `denied`, matches exactly: **correct = 1**. With P(grant) = 0.07, **Brier = (0.07 - 0)^2 = 0.0049**.

The prediction freezes Term 2025, `baseline`, and `sal-v4`. These, not the evaluator's terminal context, select the bracketed reached-baseline figures in the committed `metrics/statpack.md` sal-v4 table. Strictly prior displayed Terms contribute: 2024, 5.7%/1,271; 2023, 5.9%/1,312; 2022, 5.8%/1,192; 2021, 5.6%/1,500; 2020, 4.5%/1,739; 2019, 4.6%/1,399; 2018, 4.6%/1,524; 2017, 4.7%/1,643. Weighting these displayed rates by their weighted resolved denominators yields **0.05120250431778929**, denominator **11,580**, basis **risk_set**. This is an approximation from rounded published percentages, not reconstructed exact grant counts. Terms 2025 and 2026 are excluded. The caption renders 10 of 10 available Terms; there is no hidden-window divergence to flag.

**Brier skill = 1 - 0.0049 / 0.05120250431778929^2 = -0.8690188190801803**. The correct modal call nevertheless assigns more grant probability than the prescribed baseline, costing probability-score performance on this denial. This single resolved event does not establish calibration or general performance. The prescribed baseline describes a denial-reweighted cert population, not an established mandamus rate; the shared scope flag preserves that limitation. These numbers use the committed pack as supplied, not a freshly queried corpus.

## Reasoning quality: 0.90

The rationale directly identifies the procedural mismatch, distinguishes petitioners' advocacy from findings, and weighs the asserted mandate violation against the possibility that preserving a Texas cause of action did not guarantee a federal forum. It addresses the strongest intervention argument instead of substituting a generic low-grant prior. The provisioned question presented confirms that this mandate/forum distinction is central to the petition. Its explicit treatment of absent response entries as limited evidence, rather than proof of no response anywhere, is appropriately cautious.

The reasoning also distinguishes the reached-band anchor from terminal signal buckets, discloses rounding and the limits of transporting cert rates to original mandamus, and acknowledges the lack of an independently retrieved opposition. The remaining weakness is numerical: the move from an approximately 5.12% cert anchor to 7% is judgmental, with no measured mandamus comparison set supporting its size. The denial does not reveal the Court's rationale or establish that it adopted the jurisdictional analysis discussed by the candidate. The score rewards the analytical distinction and uncertainty handling, not a supposed confirmation of that analysis by a bare denial.

Only `reasoning.md` receives this qualitative grade. The forecast document was read for context but not scored; quantitative claims remain the harness's. No vote accuracy or semantic grades are recorded on this cert-stage event. No independent big-case score is supplied.

## Leakage

The harness log identifies a **forward** prediction; the prediction and every captured call are dated September 16, before the October 5 resolution. The petition-URL retrievals concern the pre-decision filing and earlier appendix materials, including the separate 2024 judgment. Those are not the disposition being evaluated. The log contains 28 calls, 26 with captured results. Two petition-URL calls are unobserved: the candidate reports unsuccessful opens, but uncaptured telemetry itself proves neither failure nor an empty result. The queries still target a pre-decision petition rather than later outcome material.

The instruction-file search explicitly excludes the labeling-artifact path; its appearance in an exclusion expression is not evidence of reading that data. There is no observed retrieval of this petition's denial and no reasoning that presupposes it. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. Capture limits qualify the evidence, not the temporal fact that the petition was still pending.
