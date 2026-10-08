# Evaluation: claude-baseline

Prediction run: 20260917T181231Z. Evaluation run: 20261007T150255Z.

The candidate predicted `denied` with P(any grant) = 0.01.
The realized disposition is `denied`: **correct = 1**.
**Brier = (0.01 - 0)^2 = 0.0001**.
**Brier skill = 0.961856758794282**, against the baseline documented below.

## Reasoning quality: 0.78

The rationale gives a concrete, intelligible adjustment from the appropriate
prior-Term risk-set anchor. It uses the waived response and single distribution
as procedural signals and distinguishes the petition's Fifth Amendment framing
from the Fourth Amendment retention conflict it invokes. The provisioned
petition supports the concern about constitutional framing and itself labels
the illegal-exaction authorities as lower-court cases. The candidate also
identifies uncertainty arising from its inability to obtain the opinion below
and distinguishes that uncertainty from its strong denial forecast.

The deduction reflects overstatement within the rationale, not the result or
its auxiliary claims. The inference that this Court would not reformulate the
question is categorical relative to the evidence presented. Some supposed
vehicle barriers, especially limitations, are raised without demonstrating
that they controlled the judgment. The observation about counsel's lack of
Supreme Court practice is not substantiated by the supplied analysis and is a
weak substitute for evaluating the petition. The candidate acknowledges that
its description of the lower decision relies on an adversarial petition;
that disclosure helps, but does not independently establish the inferred
barriers. The move from roughly 5.1% to 1% remains judgmental rather than a
validated calibration. The unexplained denial does not confirm these theories.

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

The harness log records forward mode and 25 calls with result_capture_coverage 1.0. The September 17, 2026 prediction precedes the October 5 denial. Calls cover the provisioned record, statpack, a general corpus query, lower-opinion searches, and other retention cases. Neither the logged query slices nor the rationale shows this petition already disposed of. Null document dates and result digests alone do not prove empty results; the candidate separately reports unsuccessful opinion searches. No evidence of outcome material or forward mis-provisioning was found.

Accordingly, `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, and `leakage_suspected = false`.
This is an evidence-based forward assessment, not proof that unseen material
was absent. The evaluator's October 5 snapshot includes the denial; it is not
the candidate's September 17 snapshot and does not show what the candidate saw.
