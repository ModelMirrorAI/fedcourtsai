# Evaluation: gemini-baseline

Prediction run: 20260917T181231Z. Evaluation run: 20261007T150255Z.

## Scores

The prediction names `denied`, matching `denied`: **correct = 1**.
P(grant) = 0.01; Brier = (0.01 - 0)^2 = **0.0001**.
With the baseline described below, Brier skill = **0.961856758794**.

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

## Reasoning quality: 0.52

The rationale gives a coherent low-grant direction: the government waived its
response, no request for a response is identified, and the petition is at its
first distribution. It distinguishes the defendant's notoriety from the
likelihood of certiorari and identifies both questions presented. The 1% grant
forecast receives the best realized Brier of these candidates, but that does
not make its analysis the strongest.

The numerical anchor is weaker than the contract requires. It selects the
current docket Term's 2025 reached rate, about 3.9%, instead of pooling the
strictly-prior Terms. It also cites a zero-relist terminal rate as a baseline
without explaining that a currently unrelisted petition can later advance.
That conditional population is not interchangeable with the frozen-band risk
set. The evaluator therefore uses the common strictly-prior baseline, not the
candidate's selected rate. Because this was a forward prediction made before
resolution, the current-Term aggregate use is a baseline-method issue, not
evidence that the candidate knew this case's future result.

The assertion that the Ninth Circuit applied settled law, and that there is
no sufficiently clear split, receives little supporting analysis. The rationale
does not examine the distinction between exploiting false testimony and failing
to correct it, how preservation affects the alleged conflict, or whether the
Rule 702 question accurately describes the appellate rationale. Its conclusion
may be reasonable, but the reasoning document does not demonstrate it. The
waiver-to-1% adjustment is likewise unmeasured. Neither the terse style itself
nor the absence of external retrieval is penalized; the deduction reflects
these missing analytical links and the baseline mismatch. Forecast prose and
structured claims are not separately scored.

## Leakage

The harness log records forward mode and 22 calls, all unobserved, with capture
coverage 0.0. Their queries concern provisioned files, the committed statpack,
output creation, and validation; one searches the provisioned record for the
caption. No query seeks a post-decision source or the target outcome. No result
absence or null document date is treated as evidence that a call returned
nothing. The rationale describes an unresolved petition, and the September 17
prediction precedes the October 5 denial. On the observable queries and prose,
there is no affirmative outcome exposure; the zero capture coverage limits
verification but is not itself suspicious. Assessment:
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
`leakage_suspected = false`.
