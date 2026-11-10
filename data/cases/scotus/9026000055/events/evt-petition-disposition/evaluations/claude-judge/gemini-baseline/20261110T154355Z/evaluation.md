# gemini-baseline — evaluation

**Cell.** scotus/9026000055 (Momin v. Blanche, No. 26-55), `evt-petition-disposition`, stage **cert**, forward distribution moment (`cutoff: null`). Outcome: **denied** on 2026-11-09 off the first distribution (11/6/2026 conference), no CVSG, no noted dissent. `actual_granted` = 0. The segment base rate, its basis and the skill score are left to the harness stamp; refer to "the stamped segment base rate" for the comparison. Claims are scored in code and are not graded here. No `semantic_grades` block (cert cell).

**Leakage.** Forward cell; prediction made 2026-10-17, three weeks before resolution. Nothing in the log or prose reads this petition's disposition as decided. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Big case (own read): 0.05.** The SG's brief in opposition (now in the record) frames the question as whether the Fifth Circuit, in an unpublished per curiam, correctly upheld the BIA's denial of an untimely motion to reopen; it is fact-bound, and the SG denies any conflict with the Ninth Circuit. Stakes are confined to the petitioner.

## Score
Predicted **denied**, P(grant) = 0.015 → correct = 1, Brier = 0.000225.

## Reasoning quality: 0.50
The call is right, but the analysis is thin. The rationale notes the ~5% baseline reached rate and then anchors on the relist-0 bucket's ~1.2% instead. That conditions on a terminal relist classification that the candidate itself could not observe as final at first distribution. It gives no reason for going about a third below the risk-set anchor beyond "immigration from CA5 is heavily denied". That intuition is directionally correct but goes unexamined. The CVSG reasoning is correct (the SG is the respondent and already filed a BIO). It also states that a BIO was filed while saying the documents were unavailable, which is consistent with the docket. Overall the analysis is sound but generic and states few reasons.

## Predicted reasoning (0.50)
Central claims: denial at first conference with no relists, no CVSG, no separate writing. All were borne out. They are the modal path for a paid petition with an SG opposition, though, and the document commits to nothing a competent reader would likely have called differently. It names no conference date and makes no specific claim about the issue. The GVR content is conditional on a grant that did not happen, so it neither earns nor loses credit. Right but generic, so it sits at the midpoint anchor.
