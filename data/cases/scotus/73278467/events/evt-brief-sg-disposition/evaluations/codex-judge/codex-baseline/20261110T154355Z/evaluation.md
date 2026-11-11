# Evaluation: codex-baseline

## Outcome and quantitative accuracy

This **cert-stage** event resolved on November 9, 2026 by GVR. The final entry in `record/snapshots/2026-11-09.json` names B.P.J. and Skrmetti as the grounds for reconsideration, consistent with `outcome.json` (`actual_disposition = gvr`, `actual_granted = 1`). codex-baseline predicts that exact label: `correct = 1`. Its grant-family probability of 0.88 gives `(0.88 - 1)^2 = 0.0144`.

The stamped segment base rate and skill are the harness's, using the prediction's frozen sal-v4 high band and strictly prior Terms; no alternative scoring anchor is authored here. Cert votes are not scored. Semantic grading does not apply, and quantitative claim scores remain entirely with the harness.

## Reasoning quality: 0.94

The rationale is particularly careful about the difference between **any grant**, a GVR, and plenary review. It reads the SG's invited recommendation accurately and identifies a limited intervening-precedent route rather than assuming the Court would decide the underlying correctional-policy dispute. Its account of the panel's cited authorities, the Turner presentation problem, and petitioners' alternative request for vacatur is supported by the staged SG brief and reply.

It also takes the respondent's vehicle objections seriously: the interlocutory posture, contested split, and abusive-search allegations do not automatically disappear with decisions addressing other contexts. The rationale appropriately distinguishes the government's advocacy from adjudicated facts and does not claim that a GVR determines the ultimate winner. It accurately discloses the truncated appendix and its reliance on selected portions of other documents.

The calibration argument distinguishes an all-recommendation CVSG population from a recommendation-conditioned following rate, and explicitly labels the large upward adjustment as judgment rather than a measured statistic. That honesty supports a high reasoning grade. The remaining limitation is empirical: the record provides no recommendation-specific series that validates the precise move to 0.88. The grade reflects the argument's soundness, not a bonus for having the smallest realized Brier error.

I checked the candidate's statistical transcriptions against its reconstructed historical statpack, build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`. Its displayed CVSG figures and prior-Term high-band calculation are consistent with that build. Those contextual figures are not a second evaluator-supplied scoring baseline.

## Predicted reasoning

**Grade: 0.95.** The central forecasts were a summary GVR naming both intervening decisions, one additional distribution and a fall disposition, no second CVSG, and no plenary adoption or definitive resolution of the underlying questions. The docket records exactly one additional distribution, October 14 for the November 6 conference, followed by the November 9 GVR naming both decisions. The forecast was specific about route, timing, and scope, not merely directionally correct.

The short disposing entry cannot independently confirm all proposed judicial motivations; those explanations earn no extra credit as established holdings. The alternative discussion of plenary questions and a writing on denial was conditional on events that did not occur and is not penalized. No separate forecast grade is imported into `reasoning_quality`, and this review does not score the structured quantitative claims.

## Leakage and significance

The log records **forward** mode and an October 23 prediction before the November 9 outcome. I reviewed all 38 calls and the rationale, forecast, and retrieval note. Thirty-five calls have captured results; the three unobserved web rows concern Lawrence v. Chater or its official reporter PDF, not this petition's later history. The candidate says those attempts yielded no usable content, but the log cannot independently confirm that absence; the query targets themselves are benign. The remaining reads concern provisioned inputs, statistical context, or local tooling. Nothing shows an already-decided Roybal disposition reaching the candidate. Assessment: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

My independent significance assessment is **0.62**, balancing national constitutional and correctional stakes against the limited immediate precedential effect of this GVR. No opinion or separate-writing slot is staged, and no substitute was retrieved.
