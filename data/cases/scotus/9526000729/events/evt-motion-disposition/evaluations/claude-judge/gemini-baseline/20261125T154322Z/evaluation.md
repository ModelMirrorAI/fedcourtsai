# Evaluation - gemini-baseline, scotus/9526000729, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: a stay application (26A729), filed with a motion for leave to file under seal, from the Supreme Judicial Court of Maine. Justice Jackson denied both on 2026-11-23, six days after submission, with no response requested, no referral to the Court and no amicus filings. The outcome records the finer reading (`interim_reading: denied`, `interim_granted: 0`).

- Predicted `denied` at probability 0.005: `correct` = 1, `brier_score` = 2.5e-05.
- `vote_accuracy` is omitted, as on every interim cell.
- The segment base rate, the skill score and `claim_scores` are the harness's to stamp and are left unset here. The prediction froze no band, so no flag is needed.
- No semantic set is declared on an interim cell, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.85)

The strongest rationale of the three. It anchors on the pack's interim pool and the private/unmarked applicant cell, then moves far below it for reasons it actually went and found: the dispute is a Maine divorce and custody matter, the applicant is self-represented, the same Circuit Justice denied his earlier stay application between the same parties alone and without a response, and a recent sealed-application analogue was handled in chambers. Each of those is forward-legitimate context from other dockets, and each points the way the order went. The per-signal adjustments (response, referral, amicus) are argued individually rather than asserted, and the referral figure is tied to two concrete pathways (referral alongside the pending cert petition, or a quick renewal to a second Justice).

Marked down slightly: the factual background rests on web and docket lookups whose results the captured log does not carry, so I cannot verify it from the staged record; and 0.5% is an aggressive number for a cell whose application text was never read, although the document says so and explains the residual.

## Predicted reasoning (`predicted_reasoning_quality` = 0.9)

I treated as central: denial by Justice Jackson alone; no response and no referral; the sealing motion disposed of in the same chambers order with no writing; no amicus and a summary order in one to two weeks; and the stated ground. The first four are borne out by the Nov 23 docket entry and the outcome's interim signals. The single-Justice route was a real call - a competent reader could have forecast referral to the Court - and the document committed to it flatly. It hedged on whether the sealing motion would be granted or denied (it was denied), committing only to the route, and the six-day turnaround sits at the short edge of its window. The ground is unresolved because the order gives no reasons. Specific and borne out on everything the record can settle.

## Leakage

Forward cell (cutoff 2026-11-18, arrival-position; prediction written 2026-11-21, event resolved 2026-11-23), so no disposition existed when it ran. Every call in the log is outcome_only, so graded on queries: the web searches explicitly excluded 26A729, the two supremecourt.gov fetches were of other dockets between the same parties (25A572, 26-5639), and CourtListener lookups targeted lower-court dockets. No query reaches this application's own disposition and the reasoning does not presuppose it. Related-docket history is legitimate forward signal. Graded `not_applicable`; `leakage_suspected` is false.

## Big case

My own read is 0.02: a private family-type dispute between two individuals, resolved by a one-line chambers denial.
