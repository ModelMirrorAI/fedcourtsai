# Evaluation: claude-baseline

## Cell
Interim stage: *Akerman v. MSPB*, No. 26A612. The application was for an injunction pending certiorari, submitted to the Chief Justice on Oct 20, 2026, docketed Oct 30, and denied by the Chief Justice on Nov 3, 2026. `outcome.json`: `interim_reading` denied, `interim_granted` 0. There was no response request, no referral and no amicus. Scoring uses the finer interim reading: `correct` is 1 for a prediction on the ungranted side, and `brier_score` = p². The interim baseline (`segment_base_rate`) and `brier_skill_score` are the harness's to stamp from the statpack's pooled finer counts. I quote no rate of my own. The prediction carries no cert band (`context.band` null), so no band flag applies. Interim cells declare no semantic set, so this file has no `semantic_grades` block, and `vote_accuracy` is omitted (interim stage).

## Score
P(grant) = 0.02 and the prediction was **denied**, which is correct. Brier 0.0004.

## Reasoning quality: 0.80
The candidate read the provisioned record accurately: an injunction application, submitted to the Chief Justice as Circuit Justice, by a pro se applicant against the MSPB with the SG as counsel. It correctly treated the then-empty application text as unavailable rather than absent. It named the right standard for an injunction pending review (All Writs Act, "indisputably clear" rights). It anchored on the interim section of the statpack and then adjusted downward for the pro se posture and the demanding form of relief.

It concluded the pack published no finer-reading baseline. Whatever pack it read at prediction time, it said so and quoted the older reading only "for shape", which is the right discipline. It correctly saw the renew-to-another-Justice path as the main route to a referral, and that reasoning sensibly lifted referral above zero. The analysis is concise and sound. It is not exceptional, because it could not engage the application's contents.

## Leakage
Forward cell. The candidate web-fetched this application's own live Supreme Court docket at 2026-11-03T20:46Z, which is the resolution date. The log shows only a digest of the result. The candidate disclosed that the page showed no disposition, and its own timing forecast (late November/December) is inconsistent with knowing about a Nov 3 denial. Grade: `retrieved_outcome_material` false, `not_applicable`, not suspected. A flag notes the same-day fetch for maintainers.

## Predicted reasoning: 0.85
Central claims, in the document's order: (1) denial; (2) route: the Chief Justice in chambers, with referral only on renewal; (3) no response request; (4) no amicus and no writings; (5) timing. All were borne out. The route claim is specific and discriminating: the docket shows "denied by The Chief Justice" and no referral. The timing ("by late November or December") technically holds but was looser than the actual quick in-chambers denial. The rest of the document is fairly standard for a pro se application, so it falls short of 1.0.

## Big case
My read is 0.03: an individual pro se employment/FOIA dispute.
