# Evaluation: claude-baseline

**Outcome.** Cert-stage cell (CVSG moment). The petition was granted on November 13, 2026, limited to the first question presented as the Solicitor General reformulated it; route plenary.

**Scores.** Predicted `granted` at 0.52: `correct` = 1, Brier = (0.52 - 1)^2 = 0.2304. The segment base rate, basis and skill are the harness's to stamp and are left null. No vote accuracy on a cert cell.

## Reasoning (`reasoning_quality` 0.82)

The strongest rationale of the three. It anchors on the frozen band's pooled prior-Term rate and cross-checks it against the CVSG cut, then moves off the anchor through an explicit decomposition: P(SG favours grant) times P(grant | SG position). That structure identified the variable that in fact decided the case. Its substantive read of the SG was an inference, labelled as one, from the SEC's never having required intra-quarter reporting, and it was right on the question that mattered: the United States urged a grant on the Section 11(a) question, and the Court followed. The downward factors (interlocutory posture, the factbound-DIG risk, the BIO's argument that the questions mischaracterise the holding) were the real ones and were weighted modestly, which the outcome vindicates.

What holds it short of the top: the final number is a small lift for an analysis whose own conditional figures and qualitative read pointed more firmly to a grant, so the calibration was cautious; and the SG inference treated both questions alike, where the government separated them and opposed review of Item 303. The "where to discount me" section is candid and accurate about what was unknown.

## Predicted reasoning (`predicted_reasoning_quality` 0.75)

Central claims: the disposition and route (grant, plenary), the SG's position and the Court tracking it, which questions a grant would take, and the procedural path. The document was specific on each. Disposition, route, the SG-tracks-Court mechanism and the path (redistribution, then a grant after at most one relist - exactly one occurred) were borne out. The primary call on scope failed: it expected both questions "essentially as written", and the Court took only the first, reformulated. It did name a Question-1-only grant as the likelier narrowing if the SG counselled one, which softens the miss without converting it. The SG-brief timing (late November or December) was off by about two months, a secondary detail. Specific and mostly borne out, with one central claim held only in part.

## Leakage

Forward cell, run eight weeks before resolution. The log is fully captured; the CourtListener docket lookup returned no entries and no post-baseline state, and nothing retrieved is dated on or after the grant. `not_applicable`.
