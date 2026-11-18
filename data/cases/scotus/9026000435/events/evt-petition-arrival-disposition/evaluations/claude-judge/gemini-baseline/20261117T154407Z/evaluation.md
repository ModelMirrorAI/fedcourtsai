# Evaluation: gemini-baseline

Cert-stage arrival cell, forward mode. Outcome: petition denied on 2026-11-16 after a government waiver and a single conference, with no CVSG and no noted dissent.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.12 - 0)^2 = 0.0144.
- The segment base rate, its basis and the skill score are the harness's to stamp and are left null. No vote accuracy on a cert cell; no semantic grades on a cert cell.

## Reasoning quality: 0.40

The anchor is right: the private-class baseline reached rate, pooled to roughly 5.0% over the prior Terms. Everything after that is thin. The move to 12% rests on what the questions presented allege (defiance of Loper Bright and a split with the Eighth Circuit), taken at face value. The log shows the candidate read the questions presented and the document manifest but not the petition text or the attached summary order, so it never tested either allegation. It names the key risk itself, that the ruling may rest on factual rather than legal deference, but treats it as something only the government's response could reveal, when the appendix would have answered it. The split claim is accepted conditionally ("if the split is genuine") without examination. The reasoning on CVSG is correct. The result is a denial call with a probability more than double the anchor for a petition that drew a waiver and a one-conference denial. I did not rebuild the candidate's statpack with `statpack-at`; I mark no base-rate figure wrong.

## Predicted reasoning: 0.30

Central claims: one relist before decision; denial as the more likely result; no CVSG because the government will file a brief; a reasonable prospect of a dissent from denial. Only the bare disposition held. The relist is the document's lead procedural commitment and it failed: the petition was distributed once, for the 11/13/2026 conference, and denied on the next order list. The document also sits oddly beside the candidate's own 28% relist probability, though I grade only what the document committed to. The no-CVSG call held in result, but it is close to entailed by the government being a party, and its stated mechanism (a government brief) failed, since the respondent waived. The dissent-from-denial prospect did not materialise. A correct but generic disposition with two specific path claims failed sits a little above the 0.25 anchor. Content about the question taken and the summary route is conditional on a grant and earns neither credit nor penalty.

## Leakage

Forward mode; the cell ran on 2026-10-01. Every call in the log is result-unobserved, so I graded the queries: reads of the prompt, the provisioned record, the statpack and the schema, then writes of its own outputs. No web or CourtListener retrieval. Nothing reaches this petition's later docket. `influenced_prediction` = `not_applicable`.

## Big case

My read is 0.12: a one-station bargaining dispute decided by an unpublished summary order, denied without a response or comment.
