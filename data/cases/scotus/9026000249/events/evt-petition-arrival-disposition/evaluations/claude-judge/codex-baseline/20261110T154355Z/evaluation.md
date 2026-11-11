# Evaluation — codex-baseline — scotus/9026000249 (Quaid v. Granet, No. 26-249), arrival disposition

**Stage:** cert (arrival moment, forward). **Outcome:** denied 2026-11-09 after a single distribution; no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.0025 → `correct` = 1, Brier = 0.00000625. The segment base rate and skill score are the harness's to stamp ("the stamped segment base rate").

## Reasoning (reasoning_quality 0.75)
A disciplined analysis. The candidate anchors on the arrival-population rate and cross-checks it against the rate for Ninth Circuit petitions. It then moves down on case-specific facts it found by forward retrieval of the lower-court docket: claims dismissed with prejudice, a vexatious-litigant finding with a prefiling order, an award of fees, and a pro se appeal. Those facts point strongly toward a vehicle that would never be granted. It correctly treats `relist-increment` as the chance of the first distribution, not a true relist. It is candid that it had neither the question presented nor the Ninth Circuit memorandum. Like claude-baseline, it never named the actual ground (California's litigation privilege), so the substantive read is inferred from posture. I score it slightly below claude-baseline because it engages less with the specifics of the petition itself.

## Predicted reasoning (predicted_reasoning_quality 0.6)
I treated these as central: denial, one initial distribution with no relist, no CVSG, and no separate writing. All four held. The document is correct but mostly generic. Apart from the one-distribution call, it commits to little beyond what the base rate already implies for a pro se paid petition. It makes no call on timing or on whether respondents would respond. The paragraph on what a grant would look like is conditional on an event that did not happen, so it is neutral. The grade lands a little above the 0.5 anchor for "right but generic".

## Leakage
Forward cell, predicted 2026-08-27. CourtListener lookups targeted the CA9 and district-court dockets; the latest captured document date is 2026-07-02, before docketing. Many rows are `outcome_only` or `unobserved`. I graded those on their queries, and none aims at this petition's disposition. `influenced_prediction` = not_applicable.

## Semantic grades
None. This is a cert cell.
