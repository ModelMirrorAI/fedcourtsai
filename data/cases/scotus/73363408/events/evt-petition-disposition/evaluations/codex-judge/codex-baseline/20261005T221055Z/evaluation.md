# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition cell, not a merits judgment. The provisioned outcome records **denied**, actual_granted **0**, resolved **October 5, 2026**. codex-baseline's September 16, 2026 prediction names **denied** with P(any grant) **0.005**: correct **1** and Brier **(0.005 - 0)^2 = 0.000025**. The current provisioned snapshot is dated October 5; it is not the predictor's September 16 snapshot and was not used to reconstruct the predictor's information boundary.

The prediction freezes **baseline / sal-v4 / Term 2025**, matching the committed statpack's sal-v4 table. I use the bracketed reached rates, not terminal rates or the evaluator's current band. Prior-Term inputs, written as Term: rate, weighted resolved n, are 2024: 5.7%, 1271; 2023: 5.9%, 1312; 2022: 5.8%, 1192; 2021: 5.6%, 1500; 2020: 4.5%, 1739; 2019: 4.6%, 1399; 2018: 4.6%, 1524; 2017: 4.7%, 1643. Their weighted numerator is **592.925**, denominator **11,580**, and pooled baseline **0.05120250431778929**. These are denial-reweighted live/historical-slice estimates reconstructed from rounded displayed percentages, not integer grant counts. Terms 2025 and 2026 are excluded. The caption renders 10 of 10 Terms, so there is no hidden-window divergence. No fresh corpus query or pull vintage was obtained; this describes the committed table only.

The basis is **risk_set**, and single-cell Brier skill is **1 - 0.000025 / 0.05120250431778929^2 = 0.9904641896985705**. This is performance on one denial, not evidence of cohort calibration.

## Reasoning quality: 0.92

The rationale is well grounded in the supplied record. It uses the proper strictly-prior risk-set anchor, distinguishes any grant from plenary review, and explains the downward adjustment through the lack of a demonstrated conflict, the state finality/timeliness problem, and the absence of observed escalation. It correctly limits the waiver to the insurer and adjuster rather than every respondent. Its distinction between petition allegations and verified facts is particularly useful: it treats preservation and state-ground obstacles as uncertainties, not established bars, and identifies the petition's internally inconsistent reconsideration dates.

The provisioned petition supports those cautious characterizations. In particular, its pages 12–14 describe constitutional objections during the appellate motion practice, while pages 22–24 describe the disputed finality rules. The denial is consistent with the low-grant forecast but does not establish which of these concerns motivated the Court. The outcome supplies no judicial explanation to verify that causal account.

The remaining limitations are calibration and evidentiary scope: the reduction from about 5.12% to 0.5% is reasoned but not estimated from matched historical cases, the earlier snapshot is not independently available here, and there is no opposing brief or separately ingested lower-court order to resolve the factual disputes. General web lookups did not provide independently usable legal material. These limitations prevent a perfect score without undermining the core reasoning.

## Leakage and scope

The harness log says **forward**, and all logged prediction activity is on September 16, before the October 5 resolution. The visible queries concern supplied materials, the statpack, and general legal context. Capture coverage is **0.875**. The web results are **unobserved**, not verified failures or verified empty results, notwithstanding the candidate's self-report that nothing usable returned. Their queries do not seek this petition's disposition, and the prose does not presuppose it. I therefore record retrieved_outcome_material **false**, influenced_prediction **not_applicable**, and leakage_suspected **false** on the available evidence.

The independent stakes assessment is **0.12**, formed from the questions presented and outcome before inspecting candidate stakes scores: possible general implications of civil-appeal notice, but a narrow procedural vehicle and no substantive ruling here. It is not a grade of the candidate's stakes number.

Only reasoning.md determines reasoning_quality. The forecast document was read for context, not scored. No quantitative claim scores, semantic grades, cert-vote accuracy, process version, or harness provenance stamps are supplied.
