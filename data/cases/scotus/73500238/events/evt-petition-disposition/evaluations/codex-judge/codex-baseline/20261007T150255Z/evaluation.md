# Evaluation: codex-baseline

Prediction run: 20260917T181231Z. Evaluation run: 20261007T150255Z.

## Scores

The prediction names `denied`, matching `denied`: **correct = 1**.
P(grant) = 0.04; Brier = (0.04 - 0)^2 = **0.0016**.
With the baseline described below, Brier skill = **0.389708140709**.

## Ground truth and scoring scope

This is a cert-stage event. The supplied outcome records denial on October 5,
2026, with `actual_granted = 0`, one distribution, no CVSG, and no noted dissent
from denial. The staged October 5 snapshot also records Justice Thomas's
nonparticipation. None of this identifies the other Justices' individual cert
votes or the Court's reasons for declining review. Denial does not establish
that the lower court's legal analysis was correct.

The exact disposition comparison and binary Brier are scored separately.
`reasoning_quality` assesses only `reasoning.md`; the forecast document was read
for context, not graded. Structured mechanical claims are left to the harness.
No vote accuracy, judgment accuracy, or semantic grades are supplied on this
cert cell. No independent big-case assessment is supplied.

## Baseline

The prediction froze `baseline`, `sal-v4`, and docket-number Term 2025. The
matching sal-v4 heading in committed `metrics/statpack.md` supports `risk_set`,
not the terminal band or this evaluator's decided-docket context. Pooling the
bracketed reached figures for every rendered Term strictly before 2025 gives:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The published rounded rates yield sum(rate * n) = 592.925 and total n = 11580,
so the scoring baseline is approximately 0.05120250431778929. The fractional
numerator is a reconstruction from rounded, denial-reweighted estimates, not
an exact count of grants. Terms 2025 and 2026 are excluded. The caption reports
10 of 10 Terms rendered, so there is no hidden-window truncation to flag.
These are the committed pack's estimates, not a newly refreshed corpus claim;
no corpus-wide vintage or live per-case freshness was inferred. The evaluated
prediction's input snapshot is dated September 17, 2026; the evaluator's staged
snapshot is dated October 5, 2026.

Skill is `1 - brier_score / baseline**2` for this denial. It is a single-event
comparison, not evidence of calibration or general predictive performance.

## Reasoning quality: 0.90

The rationale connects the low grant probability to the actual information
available at prediction: a government waiver, one distribution, no recorded
response request, and no CVSG. It correctly separates a long summer wait from
multiple relists and uses a strictly-prior, reached-band anchor. Its stated
5.1209% anchor uses unrounded aggregate inputs; the tiny difference from this
evaluation's 5.12025% reconstructed Markdown rate is rounding, not a different
population or an error.

The analysis distinguishes the prosecution's correction duty from preservation
and appellate review, rather than accepting the petition's conflict framing
wholesale. It identifies that the Rule 702 question's credentials-only premise
may not describe the appellate harmlessness rationale. The staged log supports
the described targeted authority checks. The rationale expressly separates
petition-supplied allegations from independently checked material and recognizes
the missing appendix and opposition. Those are substantive analytical strengths,
not credit for using more tools or for getting denial right.

The remaining limitation is quantification: the reduction from roughly 5.1%
to 4% is judgmental rather than measured against matched waiver cases, and the
underlying vehicle assessment remains partly dependent on one-sided briefing.
The score does not treat the eventual denial as confirmation of either legal
argument and does not reward the unscored forecast or claim probabilities.

## Leakage

The harness log records forward mode: 33 calls, 32 captured and one unobserved
(coverage 0.9696969697). The unobserved web query concerns Glossip, not this
petition's result. The candidate's statement that no visible results returned
is not independently established by that marker; unobserved is not an empty
result. The other described external checks concern pre-decision authorities.
The log and rationale show no retrieval of this petition's October 5 disposition
and no reasoning that presupposes it. The September 17 prediction precedes
resolution. Assessment: `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, `leakage_suspected = false`.
