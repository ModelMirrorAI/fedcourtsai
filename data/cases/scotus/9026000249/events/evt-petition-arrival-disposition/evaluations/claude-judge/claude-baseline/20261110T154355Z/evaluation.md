# Evaluation — claude-baseline — scotus/9026000249 (Quaid v. Granet, No. 26-249), arrival disposition

**Stage:** cert (arrival moment, forward). **Outcome:** denied 2026-11-09 after a single distribution (conference of 11/6/2026); no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.003 → `correct` = 1, Brier = 0.000009. The segment base rate and skill score are the harness's to stamp; I refer only to "the stamped segment base rate".

## Reasoning (reasoning_quality 0.8)
Sound and well-built. The candidate anchors on the baseline band's arrival-population rate from the statpack, then moves sharply down for three reasons that are all real: the petitioners are pro se, the dispute is private and fact-bound with no visible split, and the petition comes out of a run of repeat suits that were dismissed early and affirmed. It looked up the lower-court dockets before the cutoff to identify the parties and posture, which was useful. It is also candid about its main blind spot: it never saw the question presented, since no petition text was in its snapshot. That means it never named the actual legal ground (California's litigation privilege applied to block amendment of privacy claims). It held back from false precision on the conditional-route claim. The point lost is the missing view of the question presented. The candidate was right to say so, but its read of the substance rests on inference.

## Predicted reasoning (predicted_reasoning_quality 0.8)
I treated these as central: (1) denial within OT2026 by a bare order, (2) exactly one distribution, with a conference in late October or November and no relist, (3) the respondents would waive, (4) no CVSG, and (5) no separate writing. Items 1, 2, 4 and 5 held, and item 2 was specific and correct on timing (the 11/6 conference, denied Nov 9). Item 3 held only in part. Two respondent groups waived, but Fidelity National Title et al. filed a brief in opposition and the petitioners replied. That is a secondary claim that failed, so the grade sits at the 0.75 anchor, nudged up because the timing call was specific. The counterfactual section on what a grant would take is conditional on an event that did not happen, so it earns no credit and no penalty.

## Leakage
Forward cell. The prediction was made 2026-08-27, while the petition was open. Retrieval covered the statpack, the cell's own snapshot, and CourtListener lookups of the lower-court dockets. The latest captured document date is 2025-02-24. Nothing touches this petition's disposition. `influenced_prediction` = not_applicable.

## Semantic grades
None. This is a cert cell, and no semantic set is declared.
