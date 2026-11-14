# Evaluation: gemini-baseline

**Outcome.** Cert-stage cell (CVSG moment). The petition was granted on November 13, 2026, limited to the first question presented as the Solicitor General reformulated it; route plenary.

**Scores.** Predicted `granted` at 0.55: `correct` = 1, Brier = (0.55 - 1)^2 = 0.2025, the best of the three. The segment base rate, basis and skill are the harness's to stamp and are left null. No vote accuracy on a cert cell.

## Reasoning (`reasoning_quality` 0.5)

Right in direction and the best-calibrated number, on a thin rationale. Two short paragraphs: a CVSG-cut base rate of about 35%, then an upward adjustment for the alleged splits, the Macquarie conflict, business amicus support and the divided panel. It names the respondents' half-truth counter-argument and the possibility that it persuades the SG, then predicts the SG "will likely recommend grant or, at minimum" that the Court grants anyway, without giving a reason for the SG's position beyond the importance of the issue. That call was correct, but it is asserted rather than argued, and the rationale largely restates the petition's framing ("strong vehicle factors") without engaging the interlocutory posture or the dispute over what the Ninth Circuit held. It does not use the frozen band's anchor, only the CVSG cut, and does not explain how the adjustment was sized. It treats the two questions as a unit, where the outcome separated them.

## Predicted reasoning (`predicted_reasoning_quality` 0.35)

Short and mostly conditional. The document does not itself state a disposition; its content is that the petition will be distributed again (near-entailed by a pending CVSG), that a grant would take both questions, that plenary is likelier than summary, and that a dissent from denial is possible. The one specific, discriminating commitment - both questions - failed: the Court granted limited to the first. Plenary over summary held. The denial-conditional content is moot. One central claim failed with the rest generic, placed slightly above that anchor because the route call was right and the document's framing was consistent with a grant.

## Leakage

Forward cell, run before resolution. Every call in the log is unobserved, which is a capture fact and not a finding; graded on queries, the calls are local shell and file operations with no web or CourtListener retrieval, and the prose relies only on the baseline record and the statpack. `not_applicable`.
