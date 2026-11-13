# Evaluation — codex-baseline

**Cell:** `scotus/9526000661`, `evt-motion-disposition`, stage **interim** (application 26A661 for a stay of execution, *Pavatt v. Oklahoma*). The outcome carries the finer interim reading (`interim_reading: denied`, `interim_granted: 0`), so the cell is scored against `interim_granted`. The baseline (`segment_base_rate`) and `brier_skill_score` are the harness's on an interim cell and are left null here, as is `base_rate_basis`; `claim_scores` is likewise computed in code.

## Scores

- Predicted `denied` at P(granted) = 0.06; outcome denied. `correct` = 1, `brier_score` = (0.06 − 0)² = 0.0036.
- `vote_accuracy` omitted (not a merits cell). No `semantic_grades` (none declared off merits).

## Reasoning quality — 0.75

The anchor work is careful and correct: the per-Term finer counts sum to 156/1,337, and the matching private × capital cell (10/288 = 3.47%) matches the committed statpack. The rationale is disciplined about what it does not know (no response, petition or decision below was provisioned) and about the limits of the escalation counts. The doctrinal analysis is sound — *Peña-Rodriguez*'s racial-bias rationale makes the requested extension a material step, no split is identified, and an objective prejudice analysis is available without juror testimony. The weakness is the direction of the final adjustment: from a 3.5% matching rate it moves *up* to 6% on irreparable harm and the seriousness of the allegation, both of which are present in essentially every application in that capital cell and so are already in the rate; its own analysis of the legal obstacles points down, not up. It also does not weigh the eve-of-execution timing or the likelihood of a state procedural bar as negatives beyond a general caveat. The ladder reasoning expects a formal response request at 0.88 on the theory that a short deadline makes "rapid adversarial consideration" likely, without considering that the State ordinarily responds uninvited in execution-week litigation.

## Predicted reasoning — 0.6

Central claims: denial by a brief unexplained order; a response called for promptly (88%); referral to the full Court (95%) and disposition on Nov 11 or the morning of Nov 12; no amicus; no separately authored writing. The disposition, referral, timing, amicus and no-writing calls were all borne out. The response-request call — stated with high confidence and placed first in the procedural narrative — failed: Oklahoma filed its response on Nov 9 with no request entry, and the outcome records `response_requested: false`. The document also forecast nothing about the linked petition (it expressly declined to), where the Court denied certiorari in the same entry. Right on the disposition and the form of the order, with one confident procedural claim wrong and the rest fairly modal: between the 0.5 and 0.75 anchors.

## Leakage

Forward mode; predicted 2026-11-09, resolved 2026-11-12. Captured log shows only provisioned inputs, the statpack, two corpus queries returning unrelated priors, a CourtListener lookup of the 2017 *Peña-Rodriguez* opinion and two unobserved web searches whose queries target that same opinion. No own-case disposition material; `influenced_prediction: not_applicable`.
