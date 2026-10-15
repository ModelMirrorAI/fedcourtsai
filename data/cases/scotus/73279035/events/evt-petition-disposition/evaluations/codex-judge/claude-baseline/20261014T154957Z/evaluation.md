# Evaluation: claude-baseline

## Outcome and numerical score

The cert-stage outcome is `denied` on October 13, 2026, with
`actual_granted = 0`. claude-baseline predicted `denied` with grant probability
0.30. Exact-label correctness is **1**; the Brier score is
**(0.30 - 0)^2 = 0.09**.

The prediction freezes `high`, `sal-v4`, and Term 2025. The stamped segment
base rate and Brier skill are the harness's; no evaluator-pooled baseline is
supplied. Cert votes are not scored. Mechanical claims remain harness-owned,
the forecast document is contextual only, and no semantic grades apply.

## Reasoning quality: 0.88

The rationale distinguishes the strength of an underlying issue from the
suitability of the petition presenting it. Its decisive evidence is accurately
described: the United States recommends denial while disagreeing with the
Sixth Circuit's categorical surcharge analysis. The staged government brief,
printed pages 8-9 and 15-18, supports the top-hat-plan and unresolved
fiduciary-status concerns, the distinction between a general conflict and
this vehicle, and the vacatur of the Fifth Circuit panel decision for en
banc rehearing. The discussion of preemption also tracks the government's
separate objection to review of question two.

The candidate considers the petitioners' contrary vehicle arguments instead
of treating the government as dispositive. It explains why the categorical
holding might still merit review while acknowledging the possibility of a
cleaner future case. It also avoids equating three distributions with three
substantive relists. These are material analytical strengths independently
of the eventual denial.

Its stated statistical method selects a matching frozen band and prior Terms,
rather than a general petition population. I assess that methodology without
reconstructing its historical statpack calculation or asserting that its
displayed-window calculation equals the harness's stamped anchor.

The principal limitation is the numerical intermediate: the proposed
20-25% starting point after an SG denial recommendation rests on general
recollection, not a documented conditional sample. The candidate discloses
this, but it still leaves the exact adjustment to 30% judgmental. Assertions
that the Court plainly wants the question and that this is the weakest kind
of denial recommendation overstate what the CVSG and briefing establish.
The strength and timing of a future alternative vehicle also remain uncertain.
These reservations limit the score despite the well-supported central analysis.

The grade assesses only the soundness of `reasoning.md`, not the additional
claims or forecast. The unexplained denial is consistent with the candidate's
case-selection account; it does not prove the Court adopted that account or
decide the ERISA merits.

## Leakage and significance

The log records 31 captured calls on September 18, before the October 13
resolution. It includes searches and live case-page checks, one of which
explicitly asks whether a disposition is reported. That request is not itself
leakage in a genuinely open forward cell. The retrieval note reports no
disposition; the rationale relies on predecision filings and treats denial
as a forecast. No dated result or admission contradicts that chronology.
The assessment is `not_applicable`, with `leakage_suspected = false`; null
document-date extraction alone is not evidence of absence.

The independent significance assessment is 0.55, based on the QP's national
remedial implications and the government's vehicle limitations, not the
candidate's stakes score. The denial itself creates no merits precedent.
