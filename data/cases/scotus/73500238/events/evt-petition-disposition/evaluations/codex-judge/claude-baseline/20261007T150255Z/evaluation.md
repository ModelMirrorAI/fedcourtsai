# Evaluation: claude-baseline

Prediction run: 20260917T181231Z. Evaluation run: 20261007T150255Z.

## Scores

The prediction names `denied`, matching `denied`: **correct = 1**.
P(grant) = 0.02; Brier = (0.02 - 0)^2 = **0.0004**.
With the baseline described below, Brier skill = **0.847427035177**.

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

## Reasoning quality: 0.82

The rationale selects the correct strictly-prior, reached-band anchor and
explicitly rejects terminal zero-relist and terminal-baseline populations as
its main yardstick. Its approximately 593 grants over 11580 is consistent with
the rounded Markdown reconstruction used here. It connects the downward
adjustment to the waiver and lack of a response request, then examines the
preservation problem, the assumed rather than found correction duty, and the
Rule 702 harmlessness rationale. The staged log records checks of the amended
lower-court opinion and relevant passages. These distinctions address the
petition's actual vehicle rather than merely restating low overall grant odds.

The rationale also discloses that corpus queries did not estimate the
waiver-to-grant transition, that the companion-petition search was inconclusive,
and that its 8% response-request and 20% conditional-grant assumptions are
judgmental. The decomposition makes the 2% estimate intelligible without
pretending those assumptions are measured frequencies.

Several assertions exceed their support. The claim that the Theranos name
'guarantees' attention and the numerical premium over an anonymous petitioner
are not grounded in the presented evidence. The absence of a keyword such as
'gatekeep' cannot by itself settle whether an opinion performed the relevant
analysis. The strong interpretation of summer inactivity, and categorical
response/redistribution language, are more confident than the disclosed data
justify. The score credits the substantive vehicle analysis but discounts these
unsupported inferential steps. It does not infer the Court's reasons from the
denial, score the separate forecast, or grade the auxiliary claim values.

## Leakage

The harness log records forward mode and 36 captured calls (coverage 1.0).
It includes searches for the target and possible companion captions, but these
were made before this event resolved. Recorded lower-court document dates
include February 24 and December 22, 2025; the latter is the amended opinion,
not the Supreme Court's October 5, 2026 denial. The broad prior-case queries
and the described lower-court review do not show this petition's future result.
One logged command looks for a sample prediction under another case's output
path; the staged query does not establish outcome exposure, and no candidate
identity is inferred from it. The rationale treats the target petition as open.
Assessment: `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, `leakage_suspected = false`.
