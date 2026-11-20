# Evaluation — `gemini-baseline` — scotus/9526000715, evt-motion-disposition

## Outcome and scores

This is an **interim** cell: an application for a stay (26A715) submitted to Justice Gorsuch on 16 November 2026. The outcome records `interim_reading: denied`, `interim_granted: 0`: Justice Gorsuch denied the stay on 19 November 2026 and granted the motion to file under seal. No response was requested, the application was not referred, and no amicus brief was filed.

- Predicted `denied` at probability 0.02. Same side of the granted/ungranted line as the outcome: `correct` = 1.
- `brier_score` = (0.02 - 0)^2 = 0.0004.
- The baseline and skill score are the harness's on an interim cell; I wrote neither, and `base_rate_basis` stays null. The prediction froze no cert band, so there is nothing to flag there.
- No `vote_accuracy` (not a merits cell), no `semantic_grades` (no semantic set is declared on an interim cell), no `claim_scores` (computed in code).

## Reasoning quality: 0.8

The document anchors correctly on the statpack: the strictly-prior pooled finer rate (156/1337, 11.7%) and the private x unmarked cell (63/906, 7.0%) both match the committed pack, which I checked. It then gives a reasoned discount for an unescalated, individual, state-court stay application and identifies a concrete legal obstacle — non-finality under 28 U.S.C. § 1257(a) with termination proceedings still pending, read through the *Hollingsworth* stay standard — as the decisive factor. That is sound stay-stage analysis and it pointed the right way: the Circuit Justice denied alone in three days.

Costs: the case facts come from web-search summaries after the petition PDF fetch failed, so details such as the state-court dissent and the tribal enrolment rest on unverified summaries (the broad outline is consistent with what another candidate reports from the petition itself). The document's account of the linked docket (no response filed) differs from another candidate's reading of the same docket (a waiver on file); the staged record cannot settle which is right. The ladder numbers for a response request (0.10) and referral (0.15) were on the high side for an application that drew neither, and some narrative about Justice Gorsuch's leanings is speculative. The disclosure of what was and was not consulted is careful and counts for the cell.

## Predicted reasoning: 0.85

Central claims, in the document's own order of weight: a single-Justice denial by Justice Gorsuch; no response request and no referral; timing of three to ten days with the sealing motion acted on at the same time and accommodated; no amicus; no separate writing. Every one is borne out by the two docket entries and the outcome's interim signals. The timing window and the sealing-motion call are specific commitments a reader could have got wrong, and both held (denied on day three; sealing granted in the same entry). The conditional content about what a grant would look like earns nothing either way. I hold it below the top anchor because the core call — a quiet single-Justice denial of an unescalated private application — is the modal result rather than a contested one.

## Leakage

Forward cell (context.mode forward, log mode forward). Prediction was written on 2026-11-19, the day the order issued, so I checked rather than passed by default: no retrieved_doc_date on or after the resolution date, no query for the 26A715 disposition, no qp-topics read, and neither prose document presupposes the denial. Web searches and two fetches of the linked 26-502 docket page are outcome_only rows (results not captured), so graded on their queries, which target the linked cert petition and the lower-court case, not the stay's disposition. The candidate discloses search-grounding metadata that listed a third-party site without fetching it; no forecast content is reported. Graded `not_applicable`; `leakage_suspected` false.

## Big case: 0.12

A sealed stay application by one parent against Oklahoma arising from a state child-deprivation adjudication, denied by the Circuit Justice alone in three days with no response, referral or writing. The linked petition's Fifth Amendment adverse-inference question has some reach beyond the family, but this interim event carried little.
