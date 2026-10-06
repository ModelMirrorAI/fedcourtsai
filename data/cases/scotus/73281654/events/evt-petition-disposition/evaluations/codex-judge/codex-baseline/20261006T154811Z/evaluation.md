# Evaluation: codex-baseline

## Outcome and scores

This is a cert-stage petition-disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. codex-baseline's September 18 prediction called denial with P(any grant) = 0.06. Thus exact-label correctness is 1 and Brier loss is `(0.06 - 0)^2 = 0.0036`.

The candidate's frozen context, not the evaluator's terminal context, supplies elevated band, sal-v4, and docket Term 2025. The committed statpack's sal-v4 table matches. I pool the bracketed reached rates for every displayed strictly prior Term, 2017–2024: `(17.5%,400), (15.9%,347), (13.8%,334), (16.1%,397), (20.5%,342), (19.0%,300), (17.5%,354), (17.9%,336)`. Their resolved-weighted numerator is 484.386 and denominator 2,810, giving a risk-set baseline of 0.17237935943060498. The numerator is reconstructed from rounded percentages, not an exact count of grants. The table renders all ten of its ten Terms; 2025 and 2026 are excluded. Brier skill is `1 - 0.0036 / baseline^2 = 0.8788476128610186`. This is comparison with the committed denial-reweighted slice, not a current whole-corpus estimate or an aggregate performance claim. No live corpus freshness is asserted.

## Reasoning quality: 0.92

The rationale gives a disciplined, record-specific explanation for moving below the matched anchor. It distinguishes a response-request redistribution from demonstrated repeated consideration of a fully briefed petition, recognizes the positive signal in the response request, and treats the parties' assertions as advocacy. It addresses the petition's strongest distinction between safeguarding existing water and obtaining additional water rather than treating the cited precedent as a complete answer by assertion.

Its treatment of alternative grounds is particularly careful. The provisioned opposition, printed pages 9–11 and 21–24, identifies the CFC's independent grounds and explains that the Federal Circuit did not reach section 1500 for the water claim. codex-baseline preserves that distinction while explaining the vehicle risk. It also identifies the absent reply as a limitation and labels the quantitative downward adjustment judgmental rather than fitted.

The remaining limitation is calibration: the exact reduction from about 17.24% to 6% is not empirically established, and the substantive assessment relies substantially on the parties' presentations rather than the complete lower-court record. Denial is consistent with the analysis but does not establish that the Court adopted any of its reasons. The score evaluates the soundness of `reasoning.md`, not success of the forecast document or the structured claims.

## Leakage and scope

The harness log says forward. All 35 calls were inspected; 33 carry captured results and two precedent-directed web calls are unobserved. The candidate reports those two calls unsuccessful, but uncaptured results do not independently establish failure or absence of content. Their queries target a 2023 precedent, and the remaining logged retrieval and prose show no acquisition of this petition's October 5 disposition. A command excluding the topic-labeling path from an instruction-file search is not a read of its artifacts. No forward mis-provisioning is indicated: retrieved outcome material is false, influence is not applicable, and leakage suspected is false.

The evaluator's October 5 snapshot was used only as resolved-event context; it was not substituted for the candidate's September 17 information set. The forecast document was read for context and remains unscored. Cert votes are not scored, no semantic set is declared, and mechanical claim scores are left to the harness. Optional independent stakes grading is omitted because the candidate's stakes score had already been seen.
