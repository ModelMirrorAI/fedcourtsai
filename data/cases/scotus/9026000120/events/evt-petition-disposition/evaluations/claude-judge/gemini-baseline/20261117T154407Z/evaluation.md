# Evaluation: gemini-baseline

Cert-stage cell (`stage: cert`, moment `distribution`). Outcome: petition **denied** on 2026-11-16, no CVSG, two distributions in total, no noted dissent.

## Scores

- Predicted `denied` at P(grant) = 0.10. `correct` = 1; `brier_score` = (0.10 - 0)^2 = 0.01.
- The segment base rate, its basis and the skill score are the harness's to stamp; I wrote none of them. `vote_accuracy` is omitted (cert cell). No `semantic_grades` (no semantic set on a cert cell).

## Reasoning (`reasoning_quality` 0.80)

The strongest analysis of the three. It started from the stamped anchor, then set it against the one-relist bucket and noted, correctly, that the second distribution came from a pre-conference reschedule and so belongs to the weaker end of that bucket. Its doctrinal work explains why the split is weaker than the petition claims: the contrary cases involve municipal or local bodies, while every circuit addressing state legislators applies immunity to prospective relief, and *Consumers Union* already does so. On QP2 it identified a concrete vehicle problem that the other candidates missed, namely that petitioners sued only the legislators and no non-legislator enforcer (confirmed in the opposition's footnote on the sergeant-at-arms), alongside the unanimous judgment and the en banc denial without a poll. It also gave a fair account of why the probability stayed well above the general rate. The move from about 0.25 to 0.10 follows from the evidence it laid out.

Limits: much of section 3A tracks the brief in opposition closely and adopts its framing ("illusory" conflict) with little independent testing of the reply's response, and it did not use the district court's alternative mootness ground. The originating-circuit grant-family figure it quotes (4.2%) is a little above the committed statpack's current row; that is within what a later refresh would move, and I did not mark it wrong. It cites `decision-below.txt` and `lower-court-docket.txt`, which are not in my own record; my record is provisioned separately, so that is no mark against it, and the facts it drew from them match the petition appendix and opposition.

## Predicted reasoning (`predicted_reasoning_quality` 0.78)

Central claims: denial; disposal directly off the November 13 conference without a further relist (75%); no CVSG; a routine denial with no separate writing (88% conditional on denial). All four were borne out by the docket and the outcome record. The conditional content (both questions taken, plenary review, remand of the merits) is unresolved and earns neither credit nor penalty.

The document committed on every dimension the outcome resolved and got each right, with probabilities that leaned the right way on relist and writing. It stays short of the top anchor because a quiet denial is the most common path for a petition in this posture, so the discriminating content is modest.

## Leakage

Forward cell, predicted 2026-11-10. Capture coverage is 0.0: every row records only how the call ended, so I graded each on its query and credited none as having returned nothing. The queries are provisioned-record reads, statpack and schema reads, and one corpus query for unrelated granted cases. Nothing in them reaches for this docket's disposition, and the reasoning does not presuppose it. `influenced_prediction` = `not_applicable`.

## Stakes

My own read is 0.4: real doctrinal questions on a salient speech subject with four advocacy-group amici, but confined to state legislative committee procedure, a unanimous judgment below, and a denial without any writing.
