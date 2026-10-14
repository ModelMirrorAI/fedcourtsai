# Evaluation: claude-baseline

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
0.94 and actual grant 1, Brier = (0.94 - 1)^2 = **0.0036**.

**Reasoning quality: 0.86.** The rationale connects the label-based verdict,
intervening decision, rejected design-defect claims, and explicit respondent
nonopposition to a strong case for GVR rather than plenary review. It records
an attempt to inspect the companion decision and related GVR examples and
acknowledges the incomplete trial-record review. It distinguishes a
redistribution from a substantive relist and gives concrete denial and
settlement scenarios for its remaining probability. These are meaningful
analytical strengths apart from the realized success.

Some claims outrun the supporting evidence. A response request and the later
nonopposition strongly support the chosen forecast, but the record does not
establish the categorical assertion that a response request is a signal the
Court does not send on a petition it intends to deny. The related-case sample
was selected with a GVR filter: useful for analogies, not a denominator that
establishes the probability of success among all similar requests. The broad
settlement assertion and precise 3% settlement allowance are not sourced in
the supplied rationale. The description of the anchor population as petitions
seeking plenary review also sits uneasily with the same discussion's explicit
inclusion of GVRs. These analytical limitations modestly reduce the score.
I do not separately grade its auxiliary claim probabilities or its forecast
document, and no eventual remand result is inferred from the GVR.

## Leakage assessment

The log identifies a forward September 27 run with all 37 results captured.
Queries include GVR corpus priors, two broad Monsanto docket searches, and
Durnell opinion searches plus a document read. The visible retrieved dates
are April 22, 2025 and June 25, 2026, both before this petition's October 13
resolution. The dated result is not a blanket guarantee about every row:
the assessment also considers query scope and the candidate's rationale.
The retrieval note describes June 30 companion GVRs and the June 25 opinion,
not an order disposing of Dennis. Broad party-name searches were permitted
in a genuinely open forward case; their breadth is not itself leakage.

No call or reasoning discloses this petition already resolved. In particular,
the forecast's accurate October 13 timing is a prediction tied to the stated
conference calendar, not evidence that the order was retrieved.
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
and `leakage_suspected = false`. The evaluator's October 13 snapshot is used
as ground truth, not assumed to have been available to this predictor.
