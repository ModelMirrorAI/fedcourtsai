# Evaluation: codex-baseline

Case: scotus/73281345; event: evt-petition-disposition.
Scored prediction run: 20260917T214606Z.

## Outcome and numerical scores

The supplied outcome records denial on October 5, 2026, with
`actual_granted = 0`. The candidate predicted `denied`, an exact match:
`correct = 1`. Its grant probability is 0.07, hence
`brier_score = (0.07 - 0)^2 = 0.0049`. Against the baseline
detailed below, `brier_skill_score = 1 - 0.0049 / 0.17237935943060498^2 = 0.835098139727`. This is a single-event
comparison, not evidence of cohort-level calibration or forecasting skill.

## Reasoning quality: 0.92

The rationale carefully distinguishes the asserted motor-vehicle conflict from
the telephone-specific question, attributes alternative jurisdictional facts
to the opposition, and addresses the petition's competing argument about the
categorical instructions covering phones, internet, and email. It explains why
a response request before the first scheduled conference weakens the inference
from two distributions, without changing the frozen band. It balances that
against the response request, amicus support, preservation, and stakes, and
explicitly acknowledges the unavailable reply and trial-record uncertainty.
The supplied petition (pp. 16–17) and opposition (pp. 7–9) support this balanced
account of the parties' positions. The cited comparator check is documented
in the captured log, though I did not independently retrieve that opinion.

The main limitation is that the reduction from roughly 17% to 7% remains
judgmental rather than empirically estimated; the document acknowledges this.
A correct denial does not establish the proposed causal explanation. The high
score rewards source discipline, competing-argument analysis, and calibrated
uncertainty, not hindsight or accuracy of the separate forecast document.

## Baseline and scoring scope

This is a cert-stage event. The scored prediction freezes Term 2025, band
`elevated`, and `sal-v4`; that version matches the committed statpack heading.
I use `risk_set`, not the evaluator's terminal context or a terminal-band rate.
The bracketed reached-elevated rows for OT2017–OT2024 supply these
(rate percent, weighted resolved n) pairs: 2017 (17.5, 400), 2018 (15.9, 347),
2019 (13.8, 334), 2020 (16.1, 397), 2021 (20.5, 342), 2022 (19.0, 300),
2023 (17.5, 354), and 2024 (17.9, 336). Pooling the displayed rounded rates
with their denominators gives 484.386 / 2810 = 0.17237935943060498.
The numerator is an implied weighted total from rounded percentages, not an
integer count of grants. OT2025 and OT2026 are excluded. The caption renders
10 of 10 Terms, so there is no truncated-window discrepancy to flag.
This is the committed pack's denial-reweighted historical/live-slice estimate,
not a newly refreshed corpus measurement; no build timestamp or current
corpus freshness is asserted. Small differences from candidates' cited
484 / 2810 reflect their use of unrounded companion data, not a scoring error.

Votes are unscored on cert cells. There is no semantic grading on this stage.
I read the pointer-named forecast for context but did not grade it or the
structured quantitative claims; the harness supplies claim scores. The
reasoning score concerns only `reasoning.md`. The recorded denial establishes
the result, not the Court's reasons for denying or approval of either party's
Commerce Clause position. I omit the optional independent stakes assessment.

## Leakage assessment

The harness log records forward mode and 30 calls on September 17, 2026,
before the October 5 resolution. Twenty-eight results are captured; the two
unobserved web calls concern the preexisting Chavarria comparator, not this
petition's disposition. Their missing results are not treated as failed or
empty searches. Other logged activity covers provisioned filings, aggregate
base rates, comparator opinion excerpts, and output/validation work. Neither
the queries nor the rationale shows this petition's disposition already known.
The rationale expressly treats the petition as pending. On this evidence,
retrieved_outcome_material is false, influenced_prediction is not_applicable,
and leakage_suspected is false. This is not an assertion that all result bytes
were visible, and the unavailable predictor flags are not evidence of cleanliness.
