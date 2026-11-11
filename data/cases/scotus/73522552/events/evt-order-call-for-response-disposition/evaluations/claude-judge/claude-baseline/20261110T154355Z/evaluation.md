# Evaluation — claude-baseline

**Cell:** scotus/73522552 (*Isaacson v. Moses*, No. 25-1411), `evt-order-call-for-response-disposition`, cert stage, moment `response-requested`, forward mode. **Outcome:** petition denied 2026-11-09 (`actual_granted` 0), two distributions in total, no CVSG, no noted dissent or statement. Both respondents filed BIOs on Sep 18, the Chamber of Commerce filed an amicus brief the same day, the petitioner replied Oct 2, and the case was distributed Oct 7 for the Nov 6 conference.

The segment base rate, brier skill score and basis are the harness's to stamp (cert cell, frozen band `baseline` under sal-v4 → risk-set pool). Here I refer only to "the stamped segment base rate" and do not give a figure of my own. Votes are not scored on a cert cell. No semantic set is declared on a cert event, so there is no `semantic_grades` block.

## Score
- Predicted `denied` at P(grant) = 0.06 → `correct` 1, `brier_score` 0.0036.

## Reasoning quality: 0.75
Concise, accurate and well calibrated:
- The record facts are right: Aug 5 distribution, the waivers, the Feb 10, 2026 summary order, and the split as the petition states it (the Eleventh Circuit against five circuits, including *NVLSP*, Fed. Cir. 2026).
- The anchor (baseline `reached` 2017–2024, rows 4.7–5.9%, ≈5.3%) matches the table in the build the candidate was placed against.
- It weighed the CFR upward against the issue's history of denials and a weak vehicle ($5,000 award, unpublished summary order, pro se objector, waiving respondents). It added a sensible reading that a CFR on a waived petition often just makes the record adversarial before a denial.
- It flagged that the prior-denials point came from unverified recall rather than presenting it as a record fact. That was honest.
- It also noticed the Chamber of Commerce in the party block, and the Chamber did file an amicus brief on Sep 18.

The main limit is that the decisive downward factor rested on unverified memory.

## Predicted reasoning: 0.70
I treated four claims as central: denial at the first post-response conference, one redistribution and no real relist, no CVSG, and most likely no separate writing. All were borne out (Oct 7 distribution for the 11/6 conference, denied Nov 9, no statement). The document commits specifically against a relist and against a writing, which a CFR could plausibly have produced. Denial itself is the modal outcome, so the grade stops short of the top.

## Leakage
Forward cell, `not_applicable`. Retrieval was local record and statpack reads plus one corpus query for 2020s grants. None of it concerned this petition's disposition.

## Big case
My own read is 0.35. See the JSON notes.
