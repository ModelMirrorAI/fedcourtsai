# Evaluation — `claude-baseline` — scotus/9526000715, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: an application for a stay (26A715) submitted to Justice Gorsuch on 16 November 2026. The outcome records `interim_reading: denied`, `interim_granted: 0`: Justice Gorsuch denied the stay on 19 November 2026 and granted the motion to file under seal. No response was requested, the application was not referred, and no amicus brief was filed.

- Predicted `denied` at probability 0.02. Same side of the granted/ungranted line as the outcome: `correct` = 1.
- `brier_score` = (0.02 - 0)^2 = 0.0004.
- The baseline and skill score are the harness's on an interim cell; I wrote neither, and `base_rate_basis` stays null. The prediction froze no cert band, so there is nothing to flag there.
- No `vote_accuracy` (not a merits cell), no `semantic_grades` (no semantic set is declared on an interim cell), no `claim_scores` (computed in code).

## Reasoning quality: 0.72

A short, honest rationale. The base rates match the committed statpack (156/1337 pooled; 63/906 for private x unmarked), and the discount below 7% is argued from the right features: the cell's grants are dominated by well-resourced election, religious-liberty and regulatory applications, while this is a family-law matter from a state intermediate court with no response, referral or amicus. The observation that the application came months after the state high court declined review and after the cert petition, undercutting urgency, is a good stay-stage point. The ladder numbers (0.04 response, 0.07 referral) were well matched to what happened.

Costs: the candidate never learned what the application or petition actually argued, so the legal analysis is generic — "almost certainly fact-bound due-process claims" is an inference, flagged as such, and it missed the Fifth Amendment question another route would have surfaced. The document is candid about that limit and about where it should be discounted, which I credit, but the analysis is thinner than the result needed to be explained.

## Predicted reasoning: 0.8

Central claims: a one-line single-Justice denial by Justice Gorsuch; no response and no referral; no amicus and no writing; disposal within two weeks and probably within days, with the sealing motion handled alongside. All are borne out by the two docket entries and the outcome's interim signals. The linked-petition forecast is offered as conditional context and the record cannot settle it, so it is unresolved and costs nothing. The document is crisp and commits to each rung, though on the sealing motion it committed only to where it would be handled, not how. Held below the top anchor because the core call is the modal outcome for this kind of application.

## Leakage

Forward cell (context.mode forward, log mode forward). Prediction was written on 2026-11-19, the day the order issued, so I checked rather than passed by default: no retrieved_doc_date on or after the resolution date, no query for the 26A715 disposition, no qp-topics read, and neither prose document presupposes the denial. The one external lookup is a captured curl of the Court's docket JSON for the linked petition, No. 26-502, truncated to 5000 bytes; the candidate reports entries through Nov 16 with no disposition shown, and nothing in the log or prose contradicts that. Graded `not_applicable`; `leakage_suspected` false.

## Big case: 0.12

A sealed stay application by one parent against Oklahoma arising from a state child-deprivation adjudication, denied by the Circuit Justice alone in three days with no response, referral or writing. The linked petition's Fifth Amendment adverse-inference question has some reach beyond the family, but this interim event carried little.
