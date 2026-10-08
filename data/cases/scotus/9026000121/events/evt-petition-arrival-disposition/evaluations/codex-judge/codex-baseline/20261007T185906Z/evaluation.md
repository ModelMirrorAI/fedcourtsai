# Evaluation: codex-baseline

## Outcome and numerical score

This is a cert-stage, arrival-moment prediction for Joseph Basso v. Jose
Rodriguez, et al. The provisioned outcome records denial on October 5, 2026,
with `actual_granted = 0`. The prediction from run `20260816T111104Z` names
`denied` and assigns P(any grant) = 0.006. Therefore `correct = 1` and
`brier_score = (0.006 - 0)^2 = 0.000036`.

The outcome reports one distribution, no CVSG date, and no noted dissent from
denial. These are recorded outcome facts, not evidence that the Court adopted
any particular legal rationale. The bare denial does not establish why the
petition failed. This one resolved forecast also cannot establish calibration.

## Reasoning quality: 0.88

The grade concerns only `reasoning.md`. Its strongest feature is the specific
connection between the grant probability and the uncertainty in the predicate
for the asserted federal claim. The provisioned petition, at printed pages
35–38, quotes the intermediate appellate court's conclusion that the LinkedIn
material did not establish when the judge began practicing law. The petition's
own subsequent account places the challenged order on Thursday and daily county
work on Monday, while also relying on an earlier employment agreement. The
candidate accurately treats this as a disputed premise, rather than proof that
the asserted disqualification had been established. Its recognition of the
state high court's procedural dismissal and the predominantly state-law fee
question supplies additional, case-specific reasons for a low grant forecast.

The rationale distinguishes an arrival risk-set anchor from a terminal-band
rate and openly identifies the missing respondent presentation. Those are
useful uncertainty controls. The residual weakness is that the sharp numerical
reduction to 0.6% remains judgmental rather than supported by a demonstrated
reference class; the account also could address more fully the petition's
argument that the earlier employment agreement warranted an evidentiary
hearing. The denial is consistent with the forecast but does not resolve these
contested legal or factual points. Neither the structured claim probabilities
nor `predicted_reasoning.md` contribute to this qualitative grade.

## Baseline unavailable: salience-version mismatch

The scored prediction freezes `context.band = baseline`,
`context.salience_version = sal-v3`, and `context.term = 2026`. The committed
`metrics/statpack.md` table is headed **Segment base rate by salience band
(sal-v4)**. It renders all 10 of its 10 Terms; the strictly prior rows would be
OT2017–OT2025, but their version does not match this prediction's frozen band.
Accordingly `segment_base_rate` and `brier_skill_score` are omitted and
`base_rate_basis` is null. A terminal fallback is not permitted for a prediction
that already freezes a band. Neither the candidate's historical 6.56% anchor
nor the evaluator's terminal context is substituted. This mismatch is recorded
in the cell-level `flags.json` and does not reduce reasoning quality.

## Leakage and scoring boundaries

The prediction and captured retrieval log both identify forward mode. The 17
logged calls occurred on August 16, 2026, before the October 5 disposition.
Capture coverage is 1.0; visible query slices concern the provisioned petition,
snapshot, context, instructions, schemas, and statpack, without a query for the
petition's result. Some slices are truncated and the staged log carries result
digests rather than full result text. The rationale and unscored forecast
nevertheless describe an unresolved petition, with no concrete evidence of
outcome material having surfaced. Credential/identity redactions do not supply
such evidence. Thus `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, and `leakage_suspected = false`.

No vote accuracy is scored on a cert cell. No semantic set is declared here;
`semantic_grades` is absent. Mechanical claim scores and provenance stamps are
left to the harness. The court-reasoning forecast is read for context and
leakage assessment only, not substantively graded.
