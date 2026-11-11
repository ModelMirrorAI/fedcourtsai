# Evaluation — codex-baseline

**Cell:** scotus/73522552 (*Isaacson v. Moses*, No. 25-1411), `evt-order-call-for-response-disposition`, cert stage, moment `response-requested`, forward mode. **Outcome:** petition denied 2026-11-09 (`actual_granted` 0), two distributions in total, no CVSG, no noted dissent or statement. Both respondents filed BIOs on Sep 18, the Chamber of Commerce filed an amicus brief the same day, the petitioner replied Oct 2, and the case was distributed Oct 7 for the Nov 6 conference.

The segment base rate, brier skill score and basis are the harness's to stamp (cert cell, frozen band `baseline` under sal-v4 → risk-set pool). Here I refer only to "the stamped segment base rate" and do not give a figure of my own. Votes are not scored on a cert cell. No semantic set is declared on a cert event, so there is no `semantic_grades` block.

## Score
- Predicted `denied` at P(grant) = 0.22 → `correct` 1, `brier_score` 0.0484.

## Reasoning quality: 0.60
Careful and accurate on the record:
- Distribution date (Aug 5), waivers, the Feb 10, 2026 summary order and the CFR date are all correct.
- It pooled the baseline-band `reached` rates over 2017–2024 from the sal-v4 table. Those rows (4.5–5.9%, n≈1,200–1,750) match the build the candidate was placed against (verified with `statpack-at`), and the ~5.2% figure is consistent with them.
- It correctly declined to read the Chamber counsel listing as a filed brief.
- It checked the prior *Johnson* petitions (Nos. 22-389, 22-517) on official dockets rather than from memory.

The weakness is the size of the adjustment. A four-fold lift, from ~5% to 22%, is weakly supported given what the candidate itself found: this exact split, with a CFR, had already been denied. Its own vehicle concerns (an unpublished summary order resting on an older published opinion, a $5,000 award) cut further down. The document admits the lift is "my judgment … not a measured call-for-response multiplier". It is honest about that, but it does not justify the size. Its denial call was right, but the probability was overconfident toward a grant relative to the evidence it laid out.

## Predicted reasoning: 0.65
I treated four claims as central: denial without a separate writing, one redistribution after the response followed by disposition with no true relist on the modal path, no CVSG, and an unsigned denial (8% writing). All were borne out. The document is specific on the path and on the absence of writings. It hedges more than the others ("modal path", "A grant path is more likely to include…"), and the 22% grant figure sits beside the denial call. That puts it a little below the most committed versions.

## Leakage
Forward cell, `not_applicable`. The web searches and fetches hit the Eleventh Circuit *Johnson* opinion and the Supreme Court dockets for older, different petitions. One corpus query was bounded `--decided-before 2025`. Nothing about this petition's disposition (Nov 9) was retrieved, and none existed when the candidate ran on Oct 29.

## Big case
My own read is 0.35. See the JSON notes.
