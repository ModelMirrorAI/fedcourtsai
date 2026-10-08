# Evaluation: gemini-baseline

Prediction run: 20260917T181231Z. Evaluation run: 20261007T150255Z.

The candidate predicted `denied` with P(any grant) = 0.015.
The realized disposition is `denied`: **correct = 1**.
**Brier = (0.015 - 0)^2 = 0.000225**.
**Brier skill = 0.914177707287135**, against the baseline documented below.

## Reasoning quality: 0.56

The rationale identifies a sensible low-grant starting point, references the
prior-Term baseline-reached range, and gives a relevant procedural reason to
move downward: the respondent waived a response and the shown docket had no
request for one. Its selected denial label is correct.

The analysis is nevertheless thin. It treats the respondent's waiver as strong
evidence of lack of merit rather than carefully distinguishing a party's
litigation choice from the Court's view. Its statement that the question does
not suggest a deep split does not engage the petition's express multicircuit
conflict argument. The important analytical task would have been to explain
whether that Fourth Amendment conflict actually fits this Fifth Amendment
question and the judgment below. Calling the issue a takings claim involving
retention without due process leaves those theories insufficiently separated.
The rationale also emphasizes the chance of an outright grant at this
conference, while the scored event concerns the eventual grant-family outcome,
including a later grant or GVR. It offers no case-specific quantitative bridge
from its broad 4–6% anchor to 1.5%. Those limits warrant a moderate grade even
though denial was a reasonable and successful forecast. Nothing in the bare
denial resolves the underlying constitutional analysis.

## Baseline and scoring boundary

This is a cert-stage evaluation. The outcome records denial on October 5, 2026,
with `actual_granted = 0`; it supplies no explanation of the Court's reasons.
Correctness compares disposition labels, while Brier scores the grant binary.
A correct denial forecast does not establish that the Court adopted the
candidate's legal analysis.

The candidate froze `context.band = baseline`, `salience_version = sal-v4`, and
Term 2025. The committed `metrics/statpack.md` heading matches that version.
I use the bracketed reached rates, not the terminal rates or the evaluator's
post-decision context, and record `base_rate_basis = risk_set`.

| Prior Term | Displayed reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The rendered table shows 10 of 10 Terms. All eight displayed Terms strictly
before 2025 enter the pool; 2025 and 2026 do not. The resolved-weighted average
of the displayed percentages is 592.925 / 11580 = 0.05120250431778929.
The numerator is reconstructed from rounded percentages, not an observed
integer grant count. This small rounding difference from a candidate's
unrounded statistical anchor is not an analytical error. These are the
committed pack's live/historical-slice, denial-reweighted estimates; I did not
refresh the corpus or establish a current corpus-wide pull vintage.

The baseline Brier is the square of that rate, since the outcome binary is zero.
Skill is `1 - forecast_Brier / baseline_Brier`. It describes this one forecast
against its specified baseline, not aggregate performance or calibration.

Only `reasoning.md` receives a reasoning-quality grade. I read the pointed-to
forecast document for context but did not score it or the quantitative claims.
No cert votes are scored; no semantic set is declared on this stage. The
harness owns claim scores and provenance stamps. No independent big-case
assessment is supplied.

## Leakage assessment

The log records forward mode, 21 calls, and result_capture_coverage 0.0: every result is unobserved, not established empty or failed. The September 17 prediction predates the October 5 denial. Query slices identify local provisioned materials, the statpack, and a corpus-query attempt bounded by --decided-before 2026-09-17. No query targets this case's later disposition and the rationale does not presuppose it. The retrieval note reports no additional retrieval, but unseen results cannot independently confirm that report. On the available timing, queries, and prose, there is no affirmative evidence of outcome material or forward mis-provisioning.

Accordingly, `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, and `leakage_suspected = false`.
This is an evidence-based forward assessment, not proof that unseen material
was absent. The evaluator's October 5 snapshot includes the denial; it is not
the candidate's September 17 snapshot and does not show what the candidate saw.
