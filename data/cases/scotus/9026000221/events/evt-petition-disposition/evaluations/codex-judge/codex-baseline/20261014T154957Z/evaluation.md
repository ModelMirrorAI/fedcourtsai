# Evaluation: codex-baseline

## Outcome and numerical scores

The cert-stage outcome is `denied`, resolved October 13, 2026, with `actual_granted = 0`. The provisioned October 13 snapshot corroborates the denial. codex-baseline's October 5 prediction named `denied`, so **correct = 1**. With P(grant family) = 0.03, **Brier = (0.03 - 0)^2 = 0.0009**. This is the arithmetic score for one event, not evidence of general calibration.

Because the prediction froze `baseline`, `sal-v4`, and Term 2026, the stamped segment base rate and derived skill are the harness's. The rate, skill and basis remain null pending that stamp; no independent comparison rate is quoted here. Cert votes are unscored. There is no semantic grading on this stage, and mechanical claim scores are left to the harness. The court-forecast document was read but did not contribute to reasoning quality.

## Reasoning quality: 0.93

The rationale connects its low grant probability to specific obstacles visible in the petition's reproduced decision rather than merely invoking a low general grant frequency. It identifies state collateral ineffective-assistance review, distinguishes deficiency from prejudice, and explains the alternative prejudice analysis in Appendix A, pages 16a–20a. It also identifies the statement-provenance dispute at pages 13a–15a: the QP's characterization does not resolve whether the challenged testimony concerned private statements to a grandfather or stationhouse statements. The candidate fairly records the petitioner's responses instead of treating those obstacles as uncontested jurisdictional bars.

The positive and negative considerations are balanced. The document explains why the asserted investigative-background problem could matter while distinguishing an analogy to an earlier decision from a holding already resolving this precise petition. It discounts an asserted circuit conflict for differences in review posture and explicitly declines to claim independent verification of every cited circuit decision. The response waiver receives modest rather than conclusive weight, and the absence of a BIO is not called a concession. It clearly separates a historical artifact from live corpus freshness and describes a strictly prior-Term, frozen-band anchor without confusing terminal trajectory buckets with forward hazards.

These strengths support a high grade for the reasoning document itself. The adjustment to precisely 0.03 remains judgmental, the full trial record and adversarial response were unavailable, and some conflict authorities were not independently checked. Those limitations prevent treating the numerical adjustment as empirically demonstrated. The ultimate denial is consistent with the forecast but supplies no explanation validating a particular doctrinal or vehicle rationale.

## Leakage assessment

The log and prediction context establish forward mode, with the prediction and all 30 calls dated October 5, before the October 13 denial. The logged external queries concern prior general precedents, not this petition's disposition. Local reads concern the provisioned inputs, schemas, and historical aggregate material. The instruction-file discovery command excludes labeling files before any read; merely naming an excluded path is not leakage.

Twenty-eight calls have captured results; two web calls are `unobserved`. The candidate describes those attempts as returning no usable content, but their capture markers cannot independently establish that. Their recorded targets nevertheless concern earlier precedents, and neither the log nor the reasoning presupposes this petition's result. Outcome-material retrieval is assessed false, influence `not_applicable`, and leakage suspicion false. The evaluator's decided snapshot is corroboration of the outcome only, not evidence of what the predictor originally saw.
