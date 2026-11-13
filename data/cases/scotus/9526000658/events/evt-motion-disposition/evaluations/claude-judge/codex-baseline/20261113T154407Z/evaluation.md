# Evaluation: codex-baseline, scotus/9526000658, evt-motion-disposition

**Outcome.** The application for a stay (26A658) was denied by the Chief Justice on November 11, 2026, with no response requested, no referral to the full Court and no amicus filings. `outcome.json` records `interim_reading: denied` and `interim_granted: 0`.

**Scores.** Predicted `denied` at P(granted) = 0.06. `correct` = 1 (same side of the granted/ungranted line as `interim_granted`); `brier_score` = 0.0036.

This is an interim cell. The segment base rate and the skill score are the harness's to stamp, so I wrote neither and left `base_rate_basis` null; I cannot see from here whether the stamped rate will come back null. No votes are scored at this stage, and no semantic set is declared, so there is no `semantic_grades` block.

## Reasoning

The 6% call was right in direction and cost a Brier of 0.0036. The rationale is careful and honest about its limits: it reads the application as content-unavailable (the text it was given was empty), rebuilds the ten-Term finer-reading pool from the statpack counts, moves to the private/unmarked applicant cell, and stops there with one further point of judgment. What it did not do is the work that was available without the application text: it took the snapshot's "Bankruptcy Appellate Panel for the 10th Circuit" label as provisioned metadata and never noticed that an application to the Chief Justice from a Virginia applicant cannot come from the Tenth Circuit, and it did not weigh the self-represented posture, which was legible from the snapshot. The result is a number that sits at the applicant-class rate for a case that had strong visible reasons to sit well below it. The 25% referral hazard is also high for an unescalated application to a single Justice and is given no support. Sound method, thin case-specific analysis: 0.60.

One fact about the information sets: the application text this candidate was given was empty, while the copy staged for me has OCR text. I used that text only to check what the case was about, and did not mark the candidate down for not knowing what it could not read.

## Predicted reasoning

Central claims: denial by the Chief Justice in a short unexplained order; no response and no referral; resolution by about Nov 16; no writing or amicus. All four held against the docket and `outcome.json`. The document is specific on timing and on the acting Justice, but it hedges the route (a 25% referral, a 10% response request) and commits to nothing about the case itself, because it had not identified the posture below. The conditional rationale for an explained denial never came into play. Right and moderately specific, with little discriminating content: 0.60.

## Leakage

Forward cell (run 2026-11-09; event resolved 2026-11-11). Log shows only prompt/schema/record reads, the statpack, one corpus query for denied cert petitions (doc date 2026-04-29), two unobserved web searches whose queries target Hollingsworth v. Perry, and CourtListener lookups of that 2010 opinion. No query reached this application's docket or disposition; reasoning states the disposition is unknown. Nothing shows the case provisioned as already decided. Graded `not_applicable`; `leakage_suspected` is false.

## Big case

My read is 0.02: a one-party emergency request in a personal bankruptcy, disposed of by a single Justice in one line.
