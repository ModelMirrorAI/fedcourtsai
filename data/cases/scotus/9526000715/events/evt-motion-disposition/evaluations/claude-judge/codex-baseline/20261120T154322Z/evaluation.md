# Evaluation — `codex-baseline` — scotus/9526000715, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: an application for a stay (26A715) submitted to Justice Gorsuch on 16 November 2026. The outcome records `interim_reading: denied`, `interim_granted: 0`: Justice Gorsuch denied the stay on 19 November 2026 and granted the motion to file under seal. No response was requested, the application was not referred, and no amicus brief was filed.

- Predicted `denied` at probability 0.04. Same side of the granted/ungranted line as the outcome: `correct` = 1.
- `brier_score` = (0.04 - 0)^2 = 0.0016.
- The baseline and skill score are the harness's on an interim cell; I wrote neither, and `base_rate_basis` stays null. The prediction froze no cert band, so there is nothing to flag there.
- No `vote_accuracy` (not a merits cell), no `semantic_grades` (no semantic set is declared on an interim cell), no `claim_scores` (computed in code).

## Reasoning quality: 0.68

The base-rate work is correct against the committed statpack (156/1337 pooled; 63/906 private x unmarked; 126/1021 unmarked margin) and the candidate notes the pack's selection and parsing limits. It is the one rationale that rests on the linked petition's own text: it identifies the adverse-inference and notice questions, the pending termination motion as the irreparable-harm argument, and the *Baxter* obstacle plus the fact-bound state findings as the reason reversal is unlikely. That is a real likelihood-of-success analysis under the stay standard and it pointed the right way.

Costs: the reasoning for the ladder is weak. It says the Circuit Justice "could also send the papers to the full Court for a short order (42%)" with no stated basis for a figure that high on an unescalated private application, and it sits awkwardly beside the candidate's own expectation that he would act alone; the application was in fact denied in chambers with no referral. The 0.17 response figure is similarly generous. The headline 4% is defensible but the move from 7% to 4% is asserted more than derived, and the document does not address finality or the federalism reluctance to stay state juvenile proceedings.

## Predicted reasoning: 0.75

Central claims: a short-order denial by Justice Gorsuch within about two weeks; no response and no referral; no further amicus and no separate writing. All three are borne out by the docket entries and the outcome's interim signals. The document is brief and commits to the ladder rungs, but says nothing about the sealing motion and gives only a loose timing window, so it is right and reasonably specific rather than sharply so.

## Leakage

Forward cell (context.mode forward, log mode forward). Prediction was written on 2026-11-19, the day the order issued, so I checked rather than passed by default: no retrieved_doc_date on or after the resolution date, no query for the 26A715 disposition, no qp-topics read, and neither prose document presupposes the denial. External lookups were the Court's docket JSON for the linked petition No. 26-502 (the scripted read filters to entries before Nov 16) and the public cert petition PDF dated 2026-10-15; several inner rows are unobserved and are graded on their queries, none of which seeks the 26A715 disposition. Graded `not_applicable`; `leakage_suspected` false.

## Big case: 0.12

A sealed stay application by one parent against Oklahoma arising from a state child-deprivation adjudication, denied by the Circuit Justice alone in three days with no response, referral or writing. The linked petition's Fifth Amendment adverse-inference question has some reach beyond the family, but this interim event carried little.
