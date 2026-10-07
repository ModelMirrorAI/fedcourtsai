# Evaluation: gemini-baseline

## Outcome and arithmetic

This is a cert-stage event. The supplied outcome records denied on October 5, 2026, with actual_granted = 0. The prediction names granted and assigns a grant probability of 0.55: correct = 0 and Brier = (0.55 - 0)^2 = 0.3025. A failed forecast is not itself proof of unsound reasoning, and the denial gives no explanation of the Court's grounds.

The prediction froze elevated under sal-v4 in Term 2025. The matching sal-v4 table in committed metrics/statpack.md renders all 10 of 10 Terms; the admissible strictly prior rows are 2017–2024. Pooling the displayed bracketed reached rate/weighted n pairs gives (0.179*336 + 0.175*354 + 0.190*300 + 0.205*342 + 0.161*397 + 0.138*334 + 0.159*347 + 0.175*400)/2810 = 0.17237935943060498. The basis is risk_set, not terminal. This is a denial-reweighted live/historical-slice estimate from the committed pack, not a fresh corpus reading. Display rounding makes the numerator 484.386 an approximation rather than an integer grant count. Skill is 1 - 0.3025/(0.17237935943060498)^2 = -9.180165863761632. Its magnitude reflects division by the small baseline loss on a denial, not a bounded percentage accuracy measure.

## Reasoning quality: 0.35

The rationale identifies relevant positive indicators: a response request after waiver, supporting amici, and experienced counsel. It uses an approximately appropriate 17% reached-band anchor and acknowledges that two distributions need not mean a genuine post-briefing relist. These are substantive strengths.

The key weakness is the unsupported jump from that anchor to 55%. The rationale calls the circuit split clear and clean without addressing the supplied opposition's concrete distinctions. Printed pages 16–19 argue that Rush concerned home daycare inspections, that Taylor II declined to apply the closely regulated industry exception to municipal parking, and that recognition of a search differs from assessing reasonableness. Printed pages 12–14 discuss the conceded status of lobstering and the particular maritime setting. The candidate does not explain why those distinctions fail, nor meaningfully assess preservation or vehicle objections. General assertions about the Court's ideological appetite and counsel's track record do not demonstrate that these correlated attention signals justify tripling the baseline probability.

The score reflects that underdeveloped analysis, not brevity alone and not merely the wrong outcome. The candidate could reasonably see the petition as important, but significance and attention are not substitutes for a demonstrated conflict and a suitable vehicle. No inference is made that the eventual denial adopted the opposition's account.

## Leakage and scoring boundaries

The harness records forward mode. All logged calls are dated September 17, before this petition's October 5 resolution. Result-capture coverage is 0.0: no result body was observed by the telemetry, so null dates and digests cannot establish empty searches. The candidate reports unsuccessful corpus queries, but that report is not independently verified by a captured result. I assess the queries themselves: provisioned files, a prior-case query bounded before September 17, and a Johnson v. Wilson lookup. None seeks this petition's subsequent disposition, and the rationale treats it as pending. There is no affirmative sign of a decided-forward mis-provision. Thus retrieved_outcome_material = false on the available evidence, influenced_prediction = not_applicable, and leakage_suspected = false, with the capture limitation expressly retained.

The named predicted_reasoning.md was read only for context. Its proposed relist, plenary review, and possible writings are not independently scored or folded into reasoning_quality. Quantitative claim_scores is left to the harness. Cert votes are unscored, and no semantic set is declared; vote_accuracy and semantic_grades are omitted. No independent big-case score is supplied.
