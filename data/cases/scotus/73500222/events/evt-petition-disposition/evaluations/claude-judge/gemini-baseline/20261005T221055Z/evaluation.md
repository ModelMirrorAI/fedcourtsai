# Evaluation of gemini-baseline — Karsjens v. Gandhi, No. 25-1321 (scotus/73500222), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on
2026-10-05 after a single distribution (conference of 9/28/2026), with no noted
dissent from denial. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = 0.0064.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction's frozen context
  carries `band: baseline` and `salience_version: sal-v4`, and the statpack's
  "Segment base rate by salience band (sal-v4)" heading names the same version,
  so the bracketed `reached` figures apply. Pooled resolved-weighted over the
  rendered Terms strictly before OT2025 (OT2017–OT2024; the caption renders 10 of
  10 Terms, so the rendered window is the pack's whole and there is no window
  divergence to flag): 592.9 / 11,580 ≈ 5.12%. Printed percentages are rounded,
  so the figure is approximate at the third decimal.
- `brier_skill_score` = 1 − 0.0064 / 0.0512² ≈ **−1.44**. The forecast named the
  right label but sat at 8%, above the 5.1% a naive base-rate forecast would
  have put, and so scores worse than the baseline on a denial.
- `judgment_correct` null, no `vote_accuracy`: non-merits cell. No
  `semantic_grades`: cert cell declares no semantic set, and `semantic_claims`
  is null on the prediction anyway.

## Reasoning quality: 0.50

What is sound: the band and basis are read correctly ("around 4–6% based on the
statpack risk set"), the circuit disagreement is characterized accurately from
the petition (Ninth Circuit permitting the chilling-effect factor, Sixth and
Eighth rejecting it), and the main negatives are the right ones — the
abuse-of-discretion standard, the idiosyncratic $366,461.96 Rule 706 expert-cost
record, the respondent's waiver, and the second question's fact-bound character.

What drags it down: the rationale is short and its net adjustment runs against
its own balance of factors. It names one upward factor (a real split) and four
downward ones, then lands at 0.08, roughly 60% above the anchor it just cited. It
does not engage the Eighth Circuit's actual ground (the unaddressed 2013 joint
recommendation to split expert fees), which is what makes the vehicle weak, and
treats "messy vehicle" at the level of a label. The 15% dissent-from-denial figure
is asserted from the stakes alone with no base-rate or doctrinal support, and the
outcome recorded no separate writing. The waiver's structural significance (no
grant without a called-for response) is noted only as a sentiment signal. A
correct label and a correct anchor, but the analysis is thin and internally
inconsistent in direction, so middling credit.

## Leakage

`mode` = forward in the harness log; `influenced_prediction` = `not_applicable`,
`retrieved_outcome_material` = false, `leakage_suspected` = false. Checked for
mis-provisioning: the prediction was created 2026-09-17, eleven days before the
conference and eighteen before the denial; the log's 28 calls are all unobserved
(`result_capture_coverage` 0.0, an engine shape, not a defect), so each was graded
on its query — prompt, record, snapshot and statpack reads, one corpus query by
legal-topic text, one CourtListener opinion search for the Rule 54(d)(1) split.
No query names this docket, no `retrieved_doc_date` is set, and the rationale
reads the snapshot (one distribution, waiver) rather than any disposition. The
retrieval note's claim that the search "surfaced" Stanley cannot be checked
against an unobserved result; nothing turns on it.

## Big case (independent read): 0.15

A Rule 54(d)(1) costs-discretion question with a thin, decades-old
disagreement framed as a discretionary factor, a record-specific second
question, no amicus, a waiver, one distribution, and a bare denial. Low-visibility
stakes outside civil-procedure specialists, with sympathetic facts. The predictor's
`big_case_score` was visible in the staged `prediction.json` when it was read, so
this read is independent in basis but not strictly in sequence.
