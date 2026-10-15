# Evaluation: gemini-baseline

## Scope and ground truth

This is a cert-stage evaluation. The provisioned outcome records `gvr`,
`actual_granted = 1`, resolved October 13, 2026. The October 13 snapshot
independently contains the order granting the petition, vacating the judgment,
and remanding in light of Durnell. This is not a plenary grant or a merits
judgment. The outcome establishes that disposition, not a new merits holding.

All candidates froze an elevated band under sal-v4. The stamped segment base
rate and its derived skill are the harness's; I leave `segment_base_rate`,
`brier_skill_score`, and `base_rate_basis` null and do not compute a competing
anchor. No terminal fallback applies. I did not independently audit the
historical statpack figures quoted in the candidates' rationales.

Only `reasoning.md` contributes to reasoning quality. The separate forecast
was read for context, not graded; quantitative claims remain for the harness.
No semantic set is graded on this cert cell, and cert votes are not scored.
The stakes assessment is the same independent case assessment for every
candidate: a substantial individual judgment and broader litigation relevance,
but a requested follow-on remand rather than a new doctrinal decision.

## Outcome and reasoning quality

The predicted label `gvr` exactly matches: `correct = 1`. With P(any grant)
0.95 and actual grant 1, Brier = (0.95 - 1)^2 = **0.0025**.

**Reasoning quality: 0.82.** The concise rationale identifies the decisive
case-specific combination: the petition requests application of the
intervening Durnell decision, and the court-requested response expressly does
not oppose the requested GVR. The response and questions presented support
that explanation. It distinguishes this follow-on request from a vehicle for
new law, and the selected label coherently implements that distinction.

The score is limited by explanation, not brevity itself. The statement that
the base rate was adjusted upward does not identify the relevant band,
prior-Term population, or starting rate, leaving the adjustment unauditable.
The remaining 5% is not linked to identified adverse scenarios or uncertainty
about application of the precedent. Its description of preemption is broader
than the provisioned response's specific label-based claim. It also loosely
places issuance of the order at the October 9 conference; the recorded order
is October 13. That calendar imprecision is minor, not a change to the correct
disposition score and not an independent timing-claim grade.

## Leakage assessment

The log identifies a September 27 forward prediction. All 27 call results
are marked unobserved, so result-capture coverage is 0.0: null document dates
cannot establish that a query returned nothing. I assessed the query slices
and the rationale instead. They name the provisioned September 27 snapshot,
context, response and questions presented, aggregate statpack sections,
schemas, output writes, and validation. No visible query seeks this case's
own disposition or post-resolution materials, and the rationale does not
presuppose a decided petition. The retrieval note's no-extra-retrieval claim
is not used as a substitute for the log; statpack reads are visible there.

`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
and `leakage_suspected = false`. This is an evidence-limited forward assessment,
not a claim to have observed the uncaptured results. The absence of result
capture is not itself a defect or a reasoning-quality penalty.
