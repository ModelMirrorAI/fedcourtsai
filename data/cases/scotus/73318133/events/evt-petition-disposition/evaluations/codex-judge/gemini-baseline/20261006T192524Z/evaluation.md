# Evaluation: gemini-baseline

## Outcome and scores

This cert-stage event resolved in denial on October 5, 2026, with `actual_granted = 0`. The September 16 prediction names `denied`, giving **correct = 1**. Its 0.001 grant probability gives **Brier = 0.000001**. The exceptionally small realized loss on this denial is not, by itself, evidence of calibrated near-certainty.

The prediction's frozen `baseline` band, `sal-v4` version, and Term 2025 govern the baseline. The statpack heading matches. The bracketed reached rates for every displayed prior Term, 2017–2024, give 592.925/11,580 = **0.05120250431778929**, with `base_rate_basis = risk_set`. Rate-percent/denominator pairs are 5.7/1271, 5.9/1312, 5.8/1192, 5.6/1500, 4.5/1739, 4.6/1399, 4.6/1524, and 4.7/1643. This calculation uses rounded displayed rates, not exact underlying grant counts. Skill = 1 - 0.000001 / baseline² = **0.9996185675879429**. The displayed table covers 10 of 10 pack Terms; this calculation excludes 2025 and 2026, and no displayed-window discrepancy is apparent.

These figures describe the committed pack used for scoring, not a current corpus census. Corpus-wide freshness was not obtained. The petition manifest records a July 17, 2026 fetch; the candidate freezes a September 16, 2026 snapshot. Ground truth is the supplied October 5 outcome.

## Reasoning quality: 0.60

The short rationale identifies a genuine problem visible in the petition's nine questions: several disparate requests concerning drugs, corporate penalties, patents, financing, and whistleblower allegations are not developed into a coherent challenge to the judgment below. Its roughly 5% prior-Term reference is broadly consistent with the appropriate reached-band baseline. Those observations support a substantially below-baseline grant forecast, and the categorical outcome was right.

The analysis is nevertheless substantially underdeveloped. Calling the claims frivolous and the vehicle wholly deficient substitutes characterization for an account of the lower decision, the preserved issue, and the missing review-worthy conflict. It does not explain the Term window, weighting, or distinction between the reached population and the terminal zero-relist comparison it invokes. The move to 0.1% is asserted rather than supported by a relevant comparison set. Its claim that uncertainty is purely administrative is stronger than warranted when the rationale does not independently examine the lower opinions or acknowledge substantive information gaps. These shortcomings concern evidentiary support and calibration, not brevity or failure to predict denial.

The score applies only to `reasoning.md`; the forecast document and quantitative claims are not independently graded. No semantic set applies at cert, and cert votes are not scored. No optional big-case assessment is supplied.

## Leakage

The harness log records forward mode and 23 calls on September 16, before the October 5 denial. All results are unobserved, yielding capture coverage 0.0. Null dates therefore cannot establish that retrieval was empty or harmless. Assessment rests on the query slices and prose: reads target the provisioned snapshot, petition opening, instructions, and statpack, followed by output operations. No outcome-directed or external case lookup appears, and the reasoning does not presuppose this petition's disposition. The available record shows no affirmative outcome exposure or mis-provisioned decided case. Outcome-material retrieval is false on that evidence, influence is `not_applicable`, and leakage suspicion is false; limited result visibility remains a qualification, not a finding of leakage.
