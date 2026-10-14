# Evaluation — gemini-baseline

**Cell:** cert stage, forward. **Outcome:** denied 2026-10-13 at the first conference (one distribution, no CVSG, no noted dissent). **Prediction:** denied, P(grant) = 0.001.

- `correct` = 1; `brier_score` = 0.000001.
- The prediction froze `context.band` = `baseline` under `sal-v4`, so the segment base rate, its basis, and the skill score are the harness's (the stamped segment base rate); I leave them null.
- The claims block is scored in code; not graded here. Cert cell, so no vote accuracy and no semantic grades.

## Reasoning quality: 0.55

The call is right and well calibrated in direction. It names the decisive features: no response filed, error-correction questions outside Rule 10, no split, and a pro se, fact-bound grievance. It also names the one plausible upside, a summary correction of the show-cause procedure. But the analysis is thin:
- It is one paragraph.
- Its anchor ("3.9% grant rate over the prior term" for the baseline band) matches neither the band's leading figure nor its pooled reached-rate figure, and it is not traced to a table row.
- It does not engage the petition's actual content beyond the questions presented. Its log shows no read of `petition.txt`, and it tried to read a non-existent `record/documents.json`.
- It says the respondent "let the deadline lapse," which is a fair reading but is stated as fact.
- The move from roughly 4% to 0.1% is asserted, not argued.
A correct conclusion with a lightly supported path.

## Leakage

The cell is forward. It predicted on 2026-10-04, before the 2026-10-13 resolution. Every logged call is `unobserved` (capture coverage 0.0), so I graded the calls on their queries. None of them sought this petition's disposition, and none could have found it. Grade: `not_applicable`, not suspected.

## Big case

My own read is 0.02: a private, unpublished, pro se procedural dispute.
