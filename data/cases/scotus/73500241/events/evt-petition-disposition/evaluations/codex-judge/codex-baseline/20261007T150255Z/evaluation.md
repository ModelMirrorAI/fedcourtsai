# Evaluation: codex-baseline

Prediction run: 20260917T181231Z. Evaluation run: 20261007T150255Z.

The candidate predicted `denied` with P(any grant) = 0.015.
The realized disposition is `denied`: **correct = 1**.
**Brier = (0.015 - 0)^2 = 0.000225**.
**Brier skill = 0.914177707287135**, against the baseline documented below.

## Reasoning quality: 0.92

The rationale carefully separates P(any grant) from a merits result and builds
its anchor from the candidate's frozen band, version, and strictly prior Terms.
It explains why terminal-state frequencies are not forward probabilities and
why the state respondent does not make these private petitioners a state-caption
risk set. The waived response is treated as posture rather than proof of lack
of merit, and the stale last proceeding is distinguished from the snapshot date.

The substantive analysis engages rather than ignores the asserted split. It
explains why a Fourth Amendment retention disagreement does not by itself
establish the Fifth Amendment proposition presented here. It then identifies
additional defendant- and pleading-specific barriers, citing particular pages
of the filed lower-court appendix, and explains why a new abstract rule might
not change the judgment. The staged retrieval record is consistent with
attempts to obtain the previously filed appendix and a cited 2024 precedent.
Its discussion of the illegal-exaction authorities is also consistent with
the citations appearing in the provisioned petition. The candidate expressly
distinguishes a description of the lower court's reasoning from endorsement
and recognizes that damages remain at issue despite return of the property.

The remaining limitation is the precision of the downward adjustment to 1.5%:
it is explicitly judgmental, not derived from a fitted model or a demonstrated
set of comparable vehicles. Further, the blinded log exposes query slices and
digests rather than the full fetched appendix/precedent passages, so I cannot
independently audit every quoted lower-opinion proposition from the evaluator's
provisioned text. I credit the coherent, specific and qualified analysis,
not an independent verification of those passages. The unexplained denial
supports the outcome forecast but does not establish its stated legal reasons.

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

The log records forward mode, 30 calls, and result_capture_coverage 0.8666666666666667. The September 17 prediction predates the October 5 denial. Four unobserved browser rows target the exact already-filed May 28 appendix, not a later docket or disposition; their unseen results are not treated as proven failures. Captured query slices also show an in-memory request for that appendix and searches concerning cited pre-prediction opinions. The rationale expressly disclaims reading later Supreme Court history. An instruction-file search excludes the forbidden labeling path rather than consulting it. No logged query or reasoning shows this petition already decided; no outcome leakage or forward mis-provisioning is evidenced.

Accordingly, `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, and `leakage_suspected = false`.
This is an evidence-based forward assessment, not proof that unseen material
was absent. The evaluator's October 5 snapshot includes the denial; it is not
the candidate's September 17 snapshot and does not show what the candidate saw.
