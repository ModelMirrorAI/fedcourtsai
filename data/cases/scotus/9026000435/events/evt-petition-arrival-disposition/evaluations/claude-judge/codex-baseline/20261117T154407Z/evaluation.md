# Evaluation: codex-baseline

Cert-stage arrival cell, forward mode. Outcome: petition denied on 2026-11-16 after a government waiver and a single conference, with no CVSG and no noted dissent.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.12 - 0)^2 = 0.0144.
- The segment base rate, its basis and the skill score are the harness's to stamp and are left null. No vote accuracy on a cert cell; no semantic grades on a cert cell.

## Reasoning quality: 0.78

The analysis is careful and well sourced. It anchored on the private-class baseline reached rate from the statpack (about 5.0% pooled over the displayed prior Terms) and was candid that the pool was reconstructed from rounded percentages. It read the appendix closely and identified the real obstacles to review: the order's evidence-specific holdings on assignment and responsible direction, the non-categorical nature of Multimedia KSDK, the Second Circuit's later self-correction as the petition itself reported it, and the weakness of a Loper Bright GVR for a judgment that postdates Loper Bright. It checked both authorities it relied on and labelled the petition's account of Siren Retail and Hospital Menonita as unverified advocacy.

The weakness is the direction of the adjustment. Having listed four substantial restraints, and with an unpublished summary order as the vehicle, it still moved the estimate up from about 5% to 12%, more than doubling the anchor on the strength of one deference sentence that its own analysis showed was not clearly dispositive. The denial after a government waiver and one conference is what its listed restraints pointed to. The number was defensible but leaned the wrong way relative to the document's own evidence. I did not rebuild the candidate's statpack with `statpack-at`; I mark no base-rate figure wrong, and the pooled figure matches what the other candidates read from the same table.

## Predicted reasoning: 0.72

Central claims, in the order the document weights them: denial; an initial conference distribution followed by denial without a repeat conference; no CVSG; an unexplained denial with no separate writing; and the path and timing (distribution after the response period, government views through ordinary opposition briefing, disposition December 2026 to March 2027). The first four held. The docket shows one distribution, for the 11/13/2026 conference, and a plain denial. The document was usefully specific in saying the declared distribution increment meant entry into conference rather than a true relist, and in committing to no repeat conference. The path claim failed: the federal respondent waived on October 23 and the petition was denied on November 16, before the forecast window opened. That is a secondary claim, so the grade sits just under the 0.75 anchor. The content about the summary route and the question the Court would take is conditional on a grant that did not happen and earns neither credit nor penalty.

## Leakage

Forward mode; the cell ran on 2026-10-01, six weeks before the denial. The log shows record and statpack reads, two uncaptured web calls whose queries concern Loper Bright only, and CourtListener lookups of Loper Bright and Multimedia KSDK. Nothing dated on or after resolution and nothing about this petition's disposition. `influenced_prediction` = `not_applicable`.

## Big case

My read is 0.12: a one-station bargaining dispute decided by an unpublished summary order, denied without a response or comment.
