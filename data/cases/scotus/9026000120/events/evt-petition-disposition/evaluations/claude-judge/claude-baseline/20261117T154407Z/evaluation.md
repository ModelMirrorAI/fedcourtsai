# Evaluation: claude-baseline

Cert-stage cell (`stage: cert`, moment `distribution`). Outcome: petition **denied** on 2026-11-16, no CVSG, two distributions in total, no noted dissent.

## Scores

- Predicted `denied` at P(grant) = 0.12. `correct` = 1; `brier_score` = (0.12 - 0)^2 = 0.0144.
- The segment base rate, its basis and the skill score are the harness's to stamp; I wrote none of them. `vote_accuracy` is omitted (cert cell). No `semantic_grades` (no semantic set on a cert cell).

## Reasoning (`reasoning_quality` 0.72)

Short, but it found the points that mattered. It saw that the elevated band rested on a reschedule before the first conference, not on a true relist, and discounted the anchor for that reason. It identified *Consumers Union* as a direct obstacle to QP1, credited the opposition's argument that the split is thin while noting the reply's best answer, flagged the unanimous judgment below, and was the only candidate to use the district court's alternative mootness holding as a vehicle problem (confirmed in the opposition and petition text). Halving the anchor to 0.12 was a proportionate response to that evidence, and it stated plainly that the size of the reschedule adjustment was its own judgment with no table behind it.

Two weaknesses. First, it read the reschedule as a sign that a Justice was looking closely and so put 0.30 on a dissent or statement from denial; the denial came without any writing, and a reschedule is at least as often administrative. That inference sits uneasily with using the same reschedule to discount the band. Second, the doctrinal treatment is thin: it asserts that the split is shallow without working through the state-versus-municipal distinction that explains why.

Base-rate figures match the committed statpack to within the drift a later refresh would produce; none marked wrong.

## Predicted reasoning (`predicted_reasoning_quality` 0.72)

Central claims: denial; denial on the November 16 order list unless relisted (about one in three); no CVSG; a roughly 30% chance of a writing from Thomas or Alito. The first three were borne out, and naming the order-list date is a specific, checkable commitment that held. The writing lean was not borne out: the denial carried no dissent or statement. Because the document's modal call was still no writing, I treat that as a secondary miss and not a failed central call. The conditional QP2 forecast is unresolved. The document's stated grounds for denial (*Consumers Union*, shallow split, mootness) cannot be checked against an unexplained denial order.

## Leakage

Forward cell, predicted 2026-11-09. Every call's result is captured: provisioned-record reads, statpack greps and corpus queries for unrelated granted cases. No CourtListener or web calls. Nothing surfaced this case's disposition. `influenced_prediction` = `not_applicable`.

## Stakes

My own read is 0.4: real doctrinal questions on a salient speech subject with four advocacy-group amici, but confined to state legislative committee procedure, a unanimous judgment below, and a denial without any writing.
