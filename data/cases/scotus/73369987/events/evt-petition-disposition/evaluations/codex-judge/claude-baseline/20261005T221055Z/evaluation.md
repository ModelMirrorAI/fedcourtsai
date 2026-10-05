# Evaluation: claude-baseline

Prediction run: 20260917T214606Z. Evaluation run: 20261005T221055Z.

P(grant) = 0.004; correct = 1; Brier = 0.000016; Brier skill = 0.993897081407085.

## Reasoning quality: 0.80

The rationale earns substantial credit for using the matching frozen-band,
prior-Term risk-set anchor and identifying concrete selection concerns:
no demonstrated appellate conflict, an unpublished decision, a potential
state-procedure obstacle, no visible response or response request, and a
narrow family-specific vehicle. It reads the petition substantively and
identifies the prior petitions as earlier proceedings rather than the target
outcome. Its limitations section acknowledges that the lower opinion was not
independently read and that its corpus lookup supplied no useful comparators.
These support a low, nonzero grant forecast without relying on hindsight.

The analysis nevertheless overstates some conclusions. It calls the
particularity ruling an adequate and independent state ground, although the
available petition disputes the procedural account and no lower opinion was
examined. The concession at the end helps but does not fully cure that
categorical formulation. Similar statutory language across states does not
itself establish the absence of conflicting judicial interpretations. Claims
that no court has accepted the theory and that a third petition has no better
claim to review exceed the demonstrated evidence. The pro se and prior-denial
discounts are qualitative, not estimated effects. The 0.4% tail probability is
therefore a defensible judgment, not an empirically validated calibration.
The correct denial is not used to validate these stronger assertions.

## Scoring basis

This is a cert-stage evaluation against the supplied outcome: denied on
October 5, 2026, with actual_granted = 0. The predicted disposition is denied,
so correct = 1. The Brier score is the squared grant probability, not a score
of the probability assigned to denial. An unexplained denial does not establish
why the Court declined review or affirm the lower court's constitutional analysis.

All baseline conditioning comes from this candidate's frozen context: Term 2025,
baseline band, sal-v4. The committed metrics/statpack.md heading also names sal-v4.
I use the bracketed reached figures with base_rate_basis = risk_set, not the
leading terminal rates or the evaluator's decided-docket context. Strictly-prior
rendered rows are OT2017 through OT2024. Their (rate, weighted resolved n) pairs,
in descending Term order, are (5.7%,1271), (5.9%,1312), (5.8%,1192), (5.6%,1500),
(4.5%,1739), (4.6%,1399), (4.6%,1524), and (4.7%,1643). Pooling gives
592.925 / 11,580 = 0.05120250431778929. The numerator is a weighted sum of
rounded published rates, not an observed integer grant count. Small differences
from a candidate's 593 / 11,580 anchor reflect display rounding, not a substantive
baseline error. The caption renders 10 of 10 Terms; excluding 2025 and 2026
leaves eight eligible rows, with no hidden-row window divergence to flag.
These are the committed live/historical-slice, denial-reweighted estimates,
not a freshly queried corpus census. No live corpus freshness claim is made.

Skill is 1 - Brier / baseline^2 for this denied outcome. These are single-cell
scores, not evidence of calibration or comparative performance across cases.
Vote accuracy is omitted because cert votes are not scored. There is no merits
judgment or declared semantic set, so judgment_correct and semantic_grades are
omitted. The forecast document was read only for context; neither it nor the
structured claims is graded here. claim_scores, process_version, and other
harness-owned stamps are deliberately absent. No optional big_case assessment
is supplied.

## Leakage assessment

The captured log has 19 calls and result_capture_coverage = 1.0.
A corpus query carries retrieved_doc_date September 17, 2026, before this
resolution. The two docket-number searches concern earlier proceedings;
the broader name search was unrestricted forward retrieval, and the candidate
reports no matching rows. I do not infer the Court's present disposition from
those earlier denials. The shell status/filter command names an excluded data
path only as an output filter, not as a content retrieval. Neither log nor
reasoning shows this petition already decided. This is not the mis-provisioned
forward exception: retrieved_outcome_material = false,
influenced_prediction = not_applicable, leakage_suspected = false.
