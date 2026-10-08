# Evaluation: codex-baseline

## Outcome and arithmetic

This cert petition was denied on October 5, 2026; actual_granted = 0. The candidate correctly chose denied. P(grant) = 0.16 produces Brier = 0.0256. The denial does not identify the Court's reasoning or decide the underlying constitutional questions.

The candidate froze baseline, sal-v4, Term 2025. The matching statpack table supplies the risk_set basis through its bracketed reached figures. Pooling all rendered Terms strictly before 2025, namely 2017–2024, gives 592.925 weighted grant equivalents / 11,580 weighted resolutions = 0.05120250431778929. This is computed from the displayed rounded percentages, not exact numerator counts; the candidate's 593 / 11,580 calculation from its JSON pack is consistent to display precision. The table renders all 10 available Terms. Own-Term and later rows are excluded, and there is no rendered-window omission. Skill = 1 - 0.0256 / 0.05120250431778929^2 = -8.7646697486638. That negative single-event skill does not contradict the correct modal label or independently establish miscalibration. The rate is from the committed denial-reweighted live/historical slice, not a newly refreshed corpus; no live freshness claim is made.

## Reasoning quality: 0.91

The rationale carefully separates petition advocacy, the lower court's holdings, and probabilistic judgment. It identifies the unresolved equal-protection issue while recognizing that party status, permissive intervention, and alternative causation grounds obstruct reaching it. Its treatment of Appendix A, pages 31a–35a, matches the provisioned text: the court assumed the asserted protection for analysis but rejected retaliatory animus and decisive causation. This supplies a meaningful check against the petition's framing rather than simply repeating it.

Other strengths are the frozen-band baseline, distinction between a response request and CVSG, correct handling of two notices for one conference, and candid statement that the missing opposition/reply limited the adversarial record. The transcript supports targeted readings of the appendix and historical precedent. The score is not higher because tripling the baseline to 16% remains a subjective adjustment with no estimated likelihood ratio, and the identified threshold obstacles leave that uplift only loosely constrained. The eventual denial neither proves those obstacles motivated the Court nor makes an uncertain 16% grant forecast inherently unsound.

## Leakage and scope

The log records forward mode, with 27 of 30 calls captured and three web calls unobserved. The unobserved queries concern the Brackeen precedent and the exact August 26 opposition PDF. The reported failure to obtain content is the candidate's disclosure, not a fact established by the absent captures. None of those queries seeks this petition's outcome, and the remaining visible activity and reasoning contain no October 5 disposition. The prediction was made September 16. Accordingly, retrieved_outcome_material is false on the available evidence and influence is not_applicable.

Only reasoning.md is graded qualitatively. The forecast document was read for context; quantitative claims remain harness-scored. No cert vote accuracy or semantic grade is entered. The optional stakes assessment is omitted because no independent assessment was fixed before candidate stakes values became visible.
