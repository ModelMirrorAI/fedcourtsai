# Evaluation: codex-baseline

## Outcome and quantitative score

This is a **cert** cell. On November 13, 2026 the Court granted plenary review limited to a reformulated first question under Section 11(a)'s misleading-omissions prong. The outcome records `actual_granted: 1`. The predicted `denied` label is wrong: **correct = 0**. P(grant) = 0.44 yields **Brier = (0.44 - 1)^2 = 0.3136**. Cert votes are not scored, and neither merits judgment accuracy nor semantic grades applies.

## Rationale quality: 0.90

`reasoning.md` carefully separates the historical baseline from forward retrieval, the attention-band prior from a CVSG cross-check, and an actual legal conflict from the petition's contested account of the holding. It addresses the majority's treatment of specific statements, the interlocutory remand, and the distinct misleading-omissions and required-disclosure theories. Its treatment of Macquarie is appropriately limited rather than asserting that a Rule 10b-5 holding automatically decides this Section 11 case. It neither invents the SG's recommendation nor hides the unresolved government input.

The denial call ultimately underestimated willingness to take a narrowed legal question notwithstanding vehicle concerns. That is a forecasting limitation, not a reason to discard otherwise strong legal analysis. The nine-point adjustment remains judgmental rather than empirically estimated, and the rationale supplies no calibrated mapping from its counterweights to that precise probability; these limitations prevent a perfect quality score. The forecast document and structured quantitative claims do not contribute to this rationale grade.

The recovered historical statpack is build `73762050f49cd68912e89c864e25a792e498b45a`, landed September 14, 2026, with no alternative build. Its exact prior-Term sal-v4 reached-band rows and CVSG table support the candidate's historical computations. The document properly treats the pooled CVSG cut as descriptive, not a replacement for its prior-Term anchor. The current evaluation defers to **the stamped segment base rate**; baseline, basis, and skill are left to the harness, not recomputed or quoted as a competing anchor.

## Predicted reasoning

**Quality: 0.40.** The opening and highest-weight claim was denial; it failed and materially constrains the grade. Nevertheless, the grant-conditioned content was specific and testable once a grant occurred: the document identified Question 1, anticipated reformulation to avoid assuming a contested holding, and preferred plenary treatment. The actual order follows that path. Its one-or-two additional distributions also matches the October 21 and November 9 entries after the October 7 SG brief. Those successes distinguish it from a wholly wrong or generic forecast, but do not cancel the failed central disposition call. The eventual merits ground remains unresolved, and the denial-conditioned separate-writing forecast earns neither credit nor penalty.

## Leakage and record limitations

This is forward mode, with a September 18 prediction preceding the November 13 disposition. There are 33 logged calls, of which 28 have captured results. Five web calls are unobserved; their null dates do not prove empty results. Their queries seek the April 2024 Macquarie precedent and official opinion, not the present petition's outcome. The candidate discloses an incidental search-index snippet describing only the June 1 CVSG already in its baseline. No own-case disposition or later SG recommendation appears in the reasoning. Outcome retrieval is assessed false on the available evidence, influence `not_applicable`, and leakage suspected false, with the web-capture limit expressly retained.

The corrected QP extract in the evaluator record does not disprove the historical mis-cut reported by this candidate. No majority opinion is staged, an ordinary cert-stage condition; future substantive holdings cannot be graded from the grant. The independent stakes assessment is 0.62 for significant nationwide but technically bounded securities-disclosure litigation.
