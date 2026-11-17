# Evaluation — gemini-baseline

**Cell.** `scotus/9026000427`, `evt-petition-disposition`, stage `cert`, forward. Outcome: petition **denied** on 2026-11-16 after a single distribution, no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.003 → `correct` = 1, Brier = 0.003² = 0.000009. Base rate, basis and skill are the harness's to stamp; I wrote none.

## Reasoning (`reasoning_quality` 0.88)

The rationale anchors on the frozen `baseline` band's pooled reached rate and then cuts hard for the right reasons: a pro se petitioner, a Solicitor General waiver with no call for a response, a nonprecedential per curiam Federal Circuit affirmance, no asserted circuit split, and fact-bound questions. It is the most record-grounded of the three on the decision below. I spot-checked its appendix facts against the provisioned petition and they hold: the Lourie/Schall/Taranto panel, the January 23, 2015 pay-discontinuation notice preceding the first February 2, 2015 disclosure, and the administrative judge's alternative no-protected-disclosure finding. The vehicle analysis (alternative ground; the reassignment theory tied to later-dated disclosures) is exactly the kind of reason this petition drew no response request.

Its base-rate figures differ from the statpack committed today because the pack has since been refreshed. I rebuilt the build the candidate was placed against with `statpack-at` (build `7bcde3b105cb`, landed 2026-10-28) and graded against that: the cafc row (n=900, 3.0% granted / 1.6% GVR), the zero-relist row (n=10,203) and the sal-v4 baseline reached figures (2025: 4.0%, n=1314; 2024: 5.9%, n=1274) all match.

What holds it short of the top: the adjustment from roughly 5% to 0.3% is asserted rather than tied to any measured pro se or waiver rate, and the summary-route reasoning is slightly at odds with itself (it says no pending case could support a GVR, yet reads the Federal Circuit GVR share as support for 0.25).

## Predicted reasoning (`predicted_reasoning_quality` 0.8)

Central claims: denial on the first order list after the November 13 conference with no relist; no CVSG, because the SG already represents the respondent; no separate writing. All three were borne out by the docket and outcome. The document was specific about route and timing rather than merely naming the disposition. It stops short of 1.0 because, on this record, those calls were ones few competent readers would have made otherwise. The QP 2 narrowing, the predicted affirmance ground and the summary-route split are conditional on a grant that never happened and earn neither credit nor penalty.

## Leakage

Forward; `not_applicable`. The log is `outcome_only` on every call, so I graded the queries themselves: provisioned record, statpack, prompt and schema reads, and one generic corpus query. Nothing targeted this petition's disposition, and the prediction predates resolution by seventeen days.

## Big case

My read: 0.04. An individual pro se federal employee's pay and position-description dispute, dismissed on jurisdictional pleading grounds in a nonprecedential decision, with no amicus interest and a denial without comment.
