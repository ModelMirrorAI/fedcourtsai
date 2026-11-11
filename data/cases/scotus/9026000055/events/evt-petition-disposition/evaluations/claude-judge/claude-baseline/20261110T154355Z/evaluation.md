# claude-baseline — evaluation

**Cell.** scotus/9026000055 (Momin v. Blanche, No. 26-55), `evt-petition-disposition`, stage **cert**, forward distribution moment (`cutoff: null`). Outcome: **denied** on 2026-11-09 off the first distribution (11/6/2026 conference), no CVSG, no noted dissent. `actual_granted` = 0. The segment base rate, its basis and the skill score are left to the harness stamp; refer to "the stamped segment base rate" for the comparison. Claims are scored in code and are not graded here. No `semantic_grades` block (cert cell).

**Leakage.** Forward cell; prediction made 2026-10-17, three weeks before resolution. Nothing in the log or prose reads this petition's disposition as decided. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Big case (own read): 0.05.** The SG's brief in opposition (now in the record) frames the question as whether the Fifth Circuit, in an unpublished per curiam, correctly upheld the BIA's denial of an untimely motion to reopen; it is fact-bound, and the SG denies any conflict with the Ninth Circuit. Stakes are confined to the petitioner.

## Score
Predicted **denied**, P(grant) = 0.03 → correct = 1, Brier = 0.0009.

## Reasoning quality: 0.72
This was the strongest of the three analyses. It anchors on the same prior-Term sal-v4 baseline reached rate (~5.0%), then makes reasoned case-specific adjustments from the docket alone. From the 25-60xxx lower-court number it infers a petition for review of a BIA order, likely decided by unpublished per curiam. The BIO later in the record confirms both: a motion-to-reopen denial affirmed in an unpublished per curiam. It also discounts for non-specialist counsel and the first-distribution posture. One upward adjustment is weak: it reads the SG's BIO as "voluntary" and mildly signalling merit. The SG routinely files oppositions in immigration cases it defends, so that inference carries little weight. The candidate keeps it small, though. It states its main uncertainty (an unseen circuit split) honestly. The SG's BIO does respond to an asserted Ninth Circuit conflict, so the candidate's caution was well placed.

## Predicted reasoning (0.55)
Central claims: denial at or shortly after the November 6 conference, no further distribution, no CVSG, no separate writing. All were borne out. The guess about what a grant would take (a BIA petition-for-review question) depends on a grant that did not happen, so it is neither credited nor penalized. Like the others, the document makes no non-modal call that it got right, so it sits slightly above the midpoint for specificity.
