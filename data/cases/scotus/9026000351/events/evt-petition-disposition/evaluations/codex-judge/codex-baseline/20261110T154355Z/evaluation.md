# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a **cert-stage distribution** cell. The authoritative outcome is denial on November 9, 2026, with `actual_granted = 0`. codex-baseline predicted `denied` with grant probability 0.002: **correct = 1** and **Brier = (0.002 - 0)^2 = 0.000004**.

The November 9 snapshot records an October 16 response waiver, an October 21 distribution for the November 6 conference, and then denial. The outcome records one distribution, no CVSG, and no noted dissent from denial. Cert votes are not scored. No semantic grading is declared on this stage. Claim scores, the stamped segment base rate, and skill are left to the harness.

## Rationale quality: 0.94

The reasoning identifies the decisive vehicle problem rather than treating the institutional question as a reason to grant. Appendix A, App. 2, expressly states that petitioner acknowledged presenting no money-mandating claim and applies the Tucker Act jurisdictional rule. App. 3 addresses the recusal argument in that limited jurisdictional posture. Appendix D dismisses without prejudice for lack of jurisdiction. Petition page 7 footnote 1 acknowledges that the constitutional issue was not reached below. These inputs substantiate the candidate's separation of the broad constitutional controversy from the judgment actually presented for review.

The response waiver and first distribution appropriately reinforce the vehicle analysis without being treated as conclusive adjudications. The rationale distinguishes reached-band risk sets from terminal-band statistics and incremental events from terminal relist/CVSG selection. It also makes its unsuccessful authority retrieval and the limits of document-completeness verification explicit. The residual limitation is calibration: the particular near-zero probability is a judgmental adjustment, not an empirically demonstrated conditional estimate, and one denial cannot validate its precision.

I checked base-rate use against the reconstructed historical statpack, build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, recovered by `statpack-at`. It is the sal-v4 build in force at the prediction run, not the currently committed sal-v8 pack. The candidate's strictly-prior-Term baseline risk-set calculation reproduces that build. I do not supply a replacement for the stamped segment base rate.

## Predicted reasoning

**Grade: 0.90.** The forecast commits to the first-conference denial route, publication following the November 6 conference, no further distribution, no response request, and no CVSG. Those central procedural predictions are borne out by the November 9 denial and the staged docket, making this more specific than a generic denial forecast.

The outcome explicitly supports no noted dissent. The broader prediction of no separate statement or writing remains unresolved because no order text or complete writing inventory is staged; this is not counted as a miss. The conditional selection of the Tucker Act/recusal questions and preference for plenary review are likewise untested, not credited or penalized. The denial does not establish the Court's substantive reasons. The grade concerns this forecast document alone and does not enter rationale quality or the mechanical scores.

## Leakage

The captured log identifies forward mode, and all 25 calls precede the November 9 resolution. The case reads target the provisioned October 23 snapshot and filings. The authority searches concern Navajo Nation and Tucker Act law rather than this petition's subsequent disposition. The CourtListener citation lookup is captured as throttled. Two web queries have unobserved results; their missing dates are not evidence that nothing returned, and the candidate's no-results description is only a self-report. Their query content and the reasoning nevertheless give no indication of retrieval of this petition's outcome. Result capture coverage is 0.92.

Assessment: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. The current evaluator's decided snapshot is not substituted for the candidate's provisioned baseline.

## Case significance

My independent stakes assessment is **0.28**: the institutional questions matter, but this collateral, nonmonetary vehicle did not produce a merits ruling or alter judicial-discipline doctrine. No blocking or actionable input defect was identified.
