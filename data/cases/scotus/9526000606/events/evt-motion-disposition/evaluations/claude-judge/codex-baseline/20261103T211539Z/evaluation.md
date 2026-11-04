# Evaluation — codex-baseline

**Cell.** scotus/9526000606, `evt-motion-disposition` — No. 26A606, *Silva v. Blanche*, a self-represented application for a stay of removal (Third Circuit No. 25-2933), submitted to Justice Alito Oct 16, 2026. **Stage: interim.** Outcome: `denied` (`interim_reading: denied`, `interim_granted: 0`), resolved Nov 2, 2026 by Justice Alito in chambers. No response was requested, no referral, no amicus. Because the outcome carries the finer interim reading, the cell is scored on `interim_granted`. `correct` is the granted/ungranted side, and `brier_score = (p − 0)²`. The segment base rate and skill score come from the harness: `stamp-cell` pools the statpack's substantive application slice over application-Terms strictly before OT2026. I quote no rate of my own and refer only to "the stamped segment base rate". No semantic set is declared on an interim cell, so there is no `semantic_grades` block. Votes are not scored.

## Scores
- Predicted `denied` at p = 0.07 → `correct` = 1, `brier_score` = 0.0049.

## Reasoning quality: 0.55
The method is careful. It anchors correctly on the interim slice (160/1,366), gives a thorough account of the caveats, and declines to infer facts the record does not hold. The legal frame (*Nken* factors) is correct. The weakness is the adjustment. The rationale itself notes features that strongly predict denial: a self-represented applicant, a single applicant's removal, no exceptional issue, and the respondent being the government. Even so, it moves only from ~11.7% to 7%. It treats missing application text as a reason against a near-zero probability, but the unconditioned pool is dominated by government and institutional applicants, and the docket identifies this one as an individual pro se applicant. That uncertainty argument is overweighted. The 35% referral and 18% response-request figures are likewise high for this shape. The direction was right, but the analysis left most of the available discrimination unused. Its disclosure of the data-quality issue (the later docketing header) and its retrieval discipline are good.

## Predicted reasoning: 0.55
Central claims:
1. Denied by a short order without a separate opinion — borne out.
2. Within one to four weeks, not via conference and relist — borne out.
3. The modal path is denial without escalation, at stated odds of 35% referral and 18% response — borne out as the modal path, though the escalation odds were generous.
4. No separate writing and no explanation — borne out.

It is right in direction, but generic. It never commits to in-chambers denial by the Circuit Justice, and it hedges every procedural step. That puts it at the middle anchor.

## Leakage
Forward cell, prediction made Oct 31. Its web calls were `unobserved` and targeted only *Nken v. Holder*. Its CourtListener calls fetched Nken excerpts. Nothing touched this case's disposition. `not_applicable`; not suspected.

