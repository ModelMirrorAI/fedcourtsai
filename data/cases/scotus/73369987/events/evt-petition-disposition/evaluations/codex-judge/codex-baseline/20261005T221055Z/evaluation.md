# Evaluation: codex-baseline

Prediction run: 20260917T214606Z. Evaluation run: 20261005T221055Z.

P(grant) = 0.005; correct = 1; Brier = 0.000025; Brier skill = 0.990464189698571.

## Reasoning quality: 0.93

This rationale provides a strong, source-conscious basis for its low grant
probability. It identifies the frozen baseline population, prior-Term window,
and correct risk-set denominator, while explicitly distinguishing terminal
relist/CVSG descriptions from forward hazards. The case-specific adjustment
rests on no demonstrated judicial conflict, an unpublished fact-dependent
vehicle, potentially dispositive procedural obstacles, and the gap between the
petition's constitutional analogies and its requested relief. It distinguishes
different state legislative policies from conflicting appellate holdings.

The strongest feature is disciplined uncertainty: lower-court descriptions
remain the petitioner's account; the candidate does not convert a possible
procedural ground into an established jurisdictional bar. It recognizes that
one child aging out does not moot all relief involving the younger child.
Earlier petition denials are separated from the target event. Its authority
check is presented as contextual analogy, not a controlling holding on
parenting-time factors. Those distinctions are supported by the supplied
petition's questions and its discussion of the procedural ruling and children.

The residual limitation is quantitative: reducing approximately 5.12% to 0.5%
remains an unestimated judgment without matched comparable petitions or
independent lower-opinion text. The detailed account supports the direction
of adjustment better than its exact magnitude. The actual denial supplies no
judicial explanation validating the predicted selection rationale. This score
grades reasoning.md alone, not the forecast, claims, or optional stakes score.

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

The log has 34 calls: 29 captured and five unobserved generic web
requests (result_capture_coverage = 0.8529411764705882). The five queries concern
certiorari rules or official rules documents, not this petition's disposition.
Although the candidate reports no usable web results, the unobserved markers
cannot independently verify that statement; I assess the queries themselves.
The precedent queries name 584 U.S. 148 and "deportation," consistent with the
reported check of a preexisting 2018 authority, not the target case. The git
history query is limited to aggregate statpack vintage. Provisioned-record reads
and unrelated historical precedent do not reveal the October 5 disposition.
The September 17 reasoning expressly maintains unresolved posture and separates
prior proceedings from this one. I find no mis-provisioned forward exception:
retrieved_outcome_material = false, influenced_prediction = not_applicable,
and leakage_suspected = false.
