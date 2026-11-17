# Evaluation: codex-baseline, scotus/9526000684, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: a pro se application for a stay (26A684) submitted to the Chief Justice on November 10, 2026. The outcome records the finer reading: `interim_reading` is `denied` and `interim_granted` is 0. The Chief Justice denied the application on November 16, 2026, with no response requested, no referral and no amicus filing.

- Predicted disposition `denied` at probability 0.02: on the ungranted side, so `correct` = 1.
- `brier_score` = (0.02 - 0)^2 = 0.0004.
- `vote_accuracy` is omitted: votes are not scored on an interim cell.
- The segment base rate, the skill score and `base_rate_basis` are the harness's on an interim cell and are left null here. If the stamped rate comes back null, the stamp's own record says why; I pooled no rate of my own.
- No semantic set is declared on an interim cell, so there is no `semantic_grades` block.

## Reasoning quality: 0.75

Sound and carefully bounded. It computes the scored interim pool from the statpack's finer counts, leans on the private/unmarked cut, and explains the further move to 2% by the weak link between the alleged pattern and any prospect of review and reversal, the pending lower-court processes, and the month of lead time before the sale. It is candid that the appendix orders were not in the record and treats the applicant's account as such. Weaker than the other two on evidence: its corpus query returned only unrelated cert denials, so it missed the same applicant's sibling applications denied days earlier, which were the single most informative comparables; that left its referral figure (18%) and its 2% headline higher than the record supported. Direction and analysis were right.

## Predicted reasoning: 0.7

Central claims: an unexplained short denial with no writing; resolution by the Chief Justice alone; no response and no amicus; a one-to-three-week timeline. The disposition and procedural path were borne out, but the document stated them as most-likely outcomes beside explicit alternatives (an 18% referral path) rather than flat commitments, and its timing window missed on the slow side: the denial came two days after the forecast. The reasons-if-given and relief-if-granted passages are conditional on events that did not occur and earn nothing either way. Right in direction and reasonably specific, with one secondary claim failed and more hedging than the other candidates.

## Leakage

Forward cell: prediction created 2026-11-14, event resolved 2026-11-16. Log (31 calls; 4 web-search rows unobserved, graded on query) shows only general-law queries (Hollingsworth, Nken, Liteky); none names this application, applicant or docket. Sole retrieved_doc_date is 2026-06-03, before the event opened. No qp-topics read. The candidate states it deliberately avoided the live docket. Graded `not_applicable`; `leakage_suspected` is false.

## Big case: 0.03

Pro se debtor's stay application to the Chief Justice arising from an unpublished Fourth Circuit mandamus denial in a recusal/bankruptcy dispute, aimed at one residential foreclosure. Denied in chambers in a one-line entry with no response, referral or amicus. Stakes are personal to one litigant; no doctrinal or public significance.
