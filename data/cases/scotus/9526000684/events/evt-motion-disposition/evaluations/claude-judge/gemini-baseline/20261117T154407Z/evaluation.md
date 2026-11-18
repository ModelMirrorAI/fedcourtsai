# Evaluation: gemini-baseline, scotus/9526000684, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: a pro se application for a stay (26A684) submitted to the Chief Justice on November 10, 2026. The outcome records the finer reading: `interim_reading` is `denied` and `interim_granted` is 0. The Chief Justice denied the application on November 16, 2026, with no response requested, no referral and no amicus filing.

- Predicted disposition `denied` at probability 0.002: on the ungranted side, so `correct` = 1.
- `brier_score` = (0.002 - 0)^2 = 4e-06.
- `vote_accuracy` is omitted: votes are not scored on an interim cell.
- The segment base rate, the skill score and `base_rate_basis` are the harness's on an interim cell and are left null here. If the stamped rate comes back null, the stamp's own record says why; I pooled no rate of my own.
- No semantic set is declared on an interim cell, so there is no `semantic_grades` block.

## Reasoning quality: 0.85

Thorough and sound. It anchors on the statpack's interim pool and the private/unmarked cut, then moves far below on case-specific grounds that are the right ones: an unpublished mandamus denial on recusal, rehearing still pending below (Rule 23.3), relief against a separate creditor's foreclosure reaching beyond the order under review, and the same applicant's two sibling applications denied in chambers days earlier with no response or referral. It checked OCR artifacts and the BOFK/BOKF caption transposition rather than relying on them. The 0.002 headline is very aggressive, but the sibling denials and posture support a figure well under 1%, and the outcome matched on every procedural dimension. Small deductions: length and verification detail beyond what the forecast needed, and increments (1.5% response, 1.2% referral) stated with more precision than the evidence gives.

## Predicted reasoning: 0.9

Central claims: solo chambers denial by the Chief Justice in a one-line entry; no response; no referral; no amicus or separate writing; timing of three to seven days from docketing. Every one is specific and borne out, down to the wording of the docket entry. The doctrinal paragraph is conditional on reasons being given, which they were not, so it earns neither credit nor penalty. Held short of 1.0 because a routine chambers denial of a pro se application is the modal path, so the discriminating content is modest even though the document committed to it flatly.

## Leakage

Forward cell: prediction created 2026-11-14, event resolved 2026-11-16. Log (70 calls, capture coverage 0.0, so graded on queries) shows no query for this application's disposition and no retrieved_doc_date; no qp-topics read. Corpus rows for the applicant's sibling applications 26A657/26A658 (denied Nov 10-11) are other dockets predating resolution: legitimate forward signal, disclosed in the prose. Graded `not_applicable`; `leakage_suspected` is false.

## Big case: 0.03

Pro se debtor's stay application to the Chief Justice arising from an unpublished Fourth Circuit mandamus denial in a recusal/bankruptcy dispute, aimed at one residential foreclosure. Denied in chambers in a one-line entry with no response, referral or amicus. Stakes are personal to one litigant; no doctrinal or public significance.
