# Evaluation: claude-baseline

## Outcome and scores

This is a cert-stage petition-disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate's September 16 prediction names `denied`, so exact-label correctness is **1**. Its grant probability is 0.004: Brier = (0.004 - 0)^2 = **0.000016**.

The frozen prediction context, not the evaluator's decided-docket context, supplies `baseline`, `sal-v4`, and Term 2025. The committed statpack heading matches that version. The risk-set baseline pools the bracketed baseline reached rates over every displayed Term strictly before 2025: 2017–2024. Rate-percent/weighted-denominator pairs are 5.7/1271, 5.9/1312, 5.8/1192, 5.6/1500, 4.5/1739, 4.6/1399, 4.6/1524, and 4.7/1643. Their rounded-rate weighted numerator is 592.925 and denominator 11,580, giving **0.05120250431778929**. This is an approximation from published rounded percentages, not an exact recovered grant count. Skill = 1 - 0.000016 / baseline² = **0.9938970814070851**. The table renders 10 of 10 pack Terms; 2025 and 2026 are excluded. No rendered-window discrepancy is evident.

These are calculations from the committed statpack, not a fresh corpus census. No corpus-wide freshness stamp was obtained. Case evidence is the provisioned outcome and petition text whose manifest records a July 17, 2026 fetch; the candidate's frozen snapshot date is September 16, 2026.

## Reasoning quality: 0.84

The rationale connects its low grant estimate to specific petition defects rather than merely assuming denial from the low base rate. Its description of the nine disparate questions and the petitioner's disagreement with the unpublished lower decision is supported by the staged petition, especially printed pages i–iii and 7–9. It correctly distinguishes the frozen reached-band anchor from terminal relist and circuit cuts, and candidly discloses that its lower-court account is second-hand. Those are substantial analytical strengths.

The limitations are overstatement and weak quantitative support for the final adjustment. Statements that no split is plausible, that petitions of this kind are never granted, and that paid pro se petitions occupy a particular bottom decile go beyond the evidence presented. The missing independent lower opinions warrant more reserve. The adjustment from about 5.1% to 0.4% is understandable but not empirically calibrated by the supplied comparison set. The denial supports the directional call; it does not establish the candidate's asserted reasons as the Court's reasons or validate the precise probability.

Only `reasoning.md` determines this quality score. The forecast document was read for context, not graded, and the quantitative claims are left to the harness. No semantic set is declared on this cert cell, and cert votes are not scored. No independent big-case assessment is supplied.

## Leakage

The harness log records forward mode and 25 calls, all dated September 16, before the supplied October 5 resolution. All have captured results, although only digests and extracted dates are staged. The own-docket lookup, lower-opinion search, and generic corpus query do not show this petition's outcome; the rationale explicitly treats it as pending. Case-specific retrieval in a genuinely open forward cell is permitted. There is no evidence of a decided case being provisioned forward. Accordingly, outcome-material retrieval is false, influence is `not_applicable`, and leakage suspicion is false.
