# Evaluation: claude-baseline

## Outcome and numerical score

The cert-stage arrival event resolved as `denied` on October 5, 2026, with
`actual_granted = 0`. claude-baseline's prediction from run `20260816T111104Z`
names `denied` and gives P(grant family) = 0.02. Thus `correct = 1` and
`brier_score = (0.02 - 0)^2 = 0.0004`.

The provisioned outcome reports one distribution, no CVSG date, and no noted
dissent from denial. It contains no substantive explanation of the denial, so
it does not prove the candidate's legal account was the Court's actual reason.
A successful label forecast and a small single-event Brier score are not a
finding of general calibration.

## Reasoning quality: 0.83

This grade uses only `reasoning.md`, not the court-reasoning forecast or the
structured claim probabilities. The candidate gives a clear prior-to-posterior
account: an arrival risk-set anchor, downward adjustments for the absence of
an identified conflict and the case's factual and state-law dependencies, and
a residual allowance for the asserted due-process problem. It distinguishes
the federal theory in the first question from the fee-rule argument in the
second. It also expressly discloses reliance on the petition's advocacy and
the lack of an independently retrieved state high-court opinion. Its account
of the empty corpus lookup appropriately avoids treating missing coverage as
affirmative evidence against the petition.

Two weaknesses keep the grade below an excellent, fully grounded analysis.
First, saying the Maryland courts "evidently resolved" the recall-law predicate
against the petitioner compresses an important distinction: the intermediate
decision quoted in the provisioned petition, printed pages 35–38, finds the
offered evidence insufficient to establish the relevant timing, rather than
conclusively adjudicating all alleged ineligibility. The candidate's caveat
mitigates but does not eliminate that overstatement. Second, the reference to
solo-practitioner counsel and presentation style supplies no demonstrated
case-specific quantitative basis for the reduction. The 2% estimate remains
a plausible judgmental forecast, not an empirically established conditional
rate. These limitations concern the rationale itself; they are not inferred
from the favorable outcome.

## Baseline unavailable: salience-version mismatch

The prediction freezes `baseline` under `sal-v3`, for Term 2026. The currently
committed `metrics/statpack.md` salience table is explicitly `sal-v4`. Although
all 10 of 10 Terms are rendered and OT2017–OT2025 are strictly prior to the
case's Term, those rows cannot supply a version-matched baseline for the frozen
band. `segment_base_rate` and `brier_skill_score` are therefore omitted, and
`base_rate_basis` is null. The approximate 6.5% historical anchor quoted in the
candidate's rationale is not independently reconstructed or adopted as this
evaluation's rate. A terminal fallback and the evaluator's decided-docket
context are not substitutes. The cell-level flag records the mismatch; it is
not a reasoning-quality penalty.

## Leakage and scoring boundaries

The candidate's mode is forward. The log contains 26 calls on August 16, 2026,
with capture coverage 1.0. Reads address local provisioned case material,
instructions, schemas, and the committed statpack. The sole recorded corpus
lookup targets the older Caperton citation, not this petition's disposition;
the candidate's retrieval note says it returned no rows. That result is a
candidate disclosure, while the staged harness log independently establishes
the query and captured-result marker, not the complete returned body. Neither
the visible queries nor the prose shows this case's October 5 denial surfacing
before prediction. The response period and resolution are treated as pending.
The forward default therefore applies: `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, and `leakage_suspected = false`.

No cert votes are scored. There is no declared semantic set on this event, so
no semantic grading block is written. Mechanical claim scoring and provenance
are the harness's. `predicted_reasoning.md` is consulted only for context and
leakage, never included in `reasoning_quality`.
