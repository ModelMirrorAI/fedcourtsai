# Evaluation: gemini-baseline

## Cell
Interim stage: *Akerman v. MSPB*, No. 26A612. The application was for an injunction pending certiorari, submitted to the Chief Justice on Oct 20, 2026, docketed Oct 30, and denied by the Chief Justice on Nov 3, 2026. `outcome.json`: `interim_reading` denied, `interim_granted` 0. There was no response request, no referral and no amicus. Scoring uses the finer interim reading: `correct` is 1 for a prediction on the ungranted side, and `brier_score` = p². The interim baseline (`segment_base_rate`) and `brier_skill_score` are the harness's to stamp from the statpack's pooled finer counts. I quote no rate of my own. The prediction carries no cert band (`context.band` null), so no band flag applies. Interim cells declare no semantic set, so this file has no `semantic_grades` block, and `vote_accuracy` is omitted (interim stage).

## Score
P(grant) = 0.01 and the prediction was **denied**, which is correct. Brier 0.0001.

## Reasoning quality: 0.55
Strengths: substantial, accurate research into the lower-court record. It covered DDC 1:23-cv-02574, the April 18, 2026 omnibus denial at ECF 98, the D.C. Circuit interlocutory appeal 26-5131, the parallel mandamus, and the applicant's prior SCOTUS applications (24A730/24A731, both denied after referral). The application text, later OCR'd, confirms the ECF 98 framing. Its conclusion that a pro se interlocutory dispute presents no basis for emergency relief is sound.

Weaknesses: it **misstated the provisioned docket entry**. It quoted it as "Application for immediate administrative stay and stay pending appeal, submitted to Justice Gorsuch". The snapshot entry reads "Application (26A612) for an injunction, submitted to The Chief Justice." That error carried into the analysis in two ways:
- It applied the Nken/Hollingsworth stay standard rather than the stricter injunction standard. The direction is the same, so this costs little on its own.
- It built its 35% referral estimate on the non-circuit-Justice premise, which the record contradicts.

It also asserted an unsourced "<1%" empirical grant rate for this sub-population. The headline probability is good; the record handling behind it was not reliable.

## Leakage
Forward cell. The retrieval was lower-court and prior-docket material dated before the Nov 3 resolution, which is legitimate forward signal. The log is outcome_only, so calls are graded on their queries, and none sought 26A612's disposition. Clean: `not_applicable`.

## Predicted reasoning: 0.60
Central claims: (1) denial in full (borne out); (2) the application was addressed to Justice Gorsuch, making referral a substantial path (not borne out: it was submitted to and denied by the Chief Justice, with no referral); (3) no response request (borne out); (4) in-chambers denial within about 1-10 days of docketing (borne out: docketed Oct 30, denied Nov 3); (5) no separate writing (borne out).

The disposition and timing calls were specific and correct. The procedural-path claim the document gives most weight to rested on a misread of the record and failed. Mixed, so above 0.5 only because of the accurate timing call.

## Big case
My read is 0.03.
