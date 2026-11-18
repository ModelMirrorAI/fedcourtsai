# Evaluation: claude-baseline, scotus/9526000684, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: a pro se application for a stay (26A684) submitted to the Chief Justice on November 10, 2026. The outcome records the finer reading: `interim_reading` is `denied` and `interim_granted` is 0. The Chief Justice denied the application on November 16, 2026, with no response requested, no referral and no amicus filing.

- Predicted disposition `denied` at probability 0.01: on the ungranted side, so `correct` = 1.
- `brier_score` = (0.01 - 0)^2 = 0.0001.
- `vote_accuracy` is omitted: votes are not scored on an interim cell.
- The segment base rate, the skill score and `base_rate_basis` are the harness's on an interim cell and are left null here. If the stamped rate comes back null, the stamp's own record says why; I pooled no rate of my own.
- No semantic set is declared on an interim cell, so there is no `semantic_grades` block.

## Reasoning quality: 0.85

Concise and sound. It uses the correct scored pool and the private/unmarked cut, explains why that cut overstates this application's chances (it pools counseled institutional applications with pro se filings), and identifies the decisive posture defects: discretionary mandamus denial in an unpublished per curiam, no cert-worthy question, rehearing pending below. Its best move was looking up the same applicant's two sibling applications and using their fast chambers denials, with no response or referral, to set both the headline and the response claim, while being explicit that these are other dockets. Its account of how a referral would arise (renewal under Rule 22.4) is accurate and shows real understanding of the process. Minor deduction: the pro se denial rate is asserted from experience rather than measured, and 12% on referral is a guess it acknowledges as its least certain number.

## Predicted reasoning: 0.9

Central claims: the Chief Justice denies it himself in a one-line entry with no administrative stay; no response; no referral absent a renewed application; no amicus or writing; denial within about a week of submission. All are flatly stated and borne out. The date range (Nov 17-20) was a day late against a Nov 16 denial, but the governing statement, within about a week of submission, held. The renewed-application branch and the conditional standard paragraph were not tested and earn nothing either way. Held short of 1.0 because the modal chambers denial of a pro se application leaves limited room to have been wrong.

## Leakage

Forward cell: prediction created 2026-11-14, event resolved 2026-11-16. Log (11 calls, all captured) shows corpus queries for denied applications and for sibling dockets 26A657 and 26A658 only; no query for 26A684, no web search, no retrieved_doc_date, no qp-topics read. The sibling denials (Nov 10-11) are other dockets predating resolution and were disclosed: legitimate forward signal. Graded `not_applicable`; `leakage_suspected` is false.

## Big case: 0.03

Pro se debtor's stay application to the Chief Justice arising from an unpublished Fourth Circuit mandamus denial in a recusal/bankruptcy dispute, aimed at one residential foreclosure. Denied in chambers in a one-line entry with no response, referral or amicus. Stakes are personal to one litigant; no doctrinal or public significance.
