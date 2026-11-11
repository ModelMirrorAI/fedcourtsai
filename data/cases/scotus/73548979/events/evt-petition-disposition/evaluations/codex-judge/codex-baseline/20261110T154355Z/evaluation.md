# Evaluation: codex-baseline

## Outcome and scores

This is a cert-stage evaluation. The petition was denied on November 9, 2026. The record adds exactly one distribution beyond the candidate's two-distribution baseline: November 2 for the November 6 conference. The outcome reports three distributions, no CVSG and no noted dissent from denial.

The predicted denied label is correct: **correct = 1**. P(grant) = 0.32 against actual_granted = 0 gives **Brier = 0.1024**. That probability scores worse than a lower grant forecast on this realized denial, without determining the quality of either prose document. Baseline, skill and basis fields are left for harness stamping using the frozen elevated/sal-v4 context, not today's terminal high/sal-v8 context. Cert votes are unscored; semantic grading does not apply; quantitative claim_scores is deliberately absent.

## Rationale quality

**reasoning_quality = 0.93**, grading reasoning.md alone. The rationale uses a well-defined information set, identifies the truncated appendix and does not claim access to a complete appellate opinion. It reconstructs the proper reached-risk-set anchor from strictly-prior docket-number Terms and explicitly avoids double-counting the existing relist. It distinguishes terminal-state statistics from prospective transition probabilities and party-reported USPTO interest from a government recommendation.

I independently reconstructed the candidate-era pack with statpack-at: build **886549a3ac32bdba039691b6d2ca7dc57bb72561**, digest **sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde**, with no alternative build. The prior 2017–2024 elevated reached counts reproduce **484/2,810 = 17.2242%**. The candidate's anchor is therefore assessed against its historical build, not rejected for disagreeing with the refreshed current pack. This contextual check is separate from the baseline that the harness will stamp.

The legal analysis fairly engages both sides: the distinction between excluding intangible property and finding no appropriation, categorical versus Penn Central theories, weaknesses in the asserted split, the Commonwealth's presence as a possible answer to the earlier vehicle problem, and the opposition's preservation/clear-statement obstacles. It recognizes that one Justice's prior interest does not show four votes to grant. The staged reply contests some vehicle objections, so the candidate appropriately does not accept the BIO wholesale. The main limitation is that the large uplift to 0.32 remains judgmental; institutional interest and doctrinal importance do not establish its magnitude. This is a calibration uncertainty rather than a demonstrated legal error. The unexplained denial does not decide which side's constitutional account is correct, and neither the successful forecast document nor the worse Brier value is folded into this rationale grade.

## Predicted reasoning

**predicted_reasoning_quality = 0.90.** The central path was unusually concrete: denial after exactly one additional distribution, in late October or November, without a CVSG or separate writing as the modal outcome. The staged record matches the sequence and window: redistribution November 2, denial November 9 and no CVSG. These were discriminating procedural commitments, not just restatements of the questions presented. The outcome establishes no noted dissent, but the broader no-separate-writing claim remains unresolved: a bare docket denial does not independently rule out every statement respecting denial, and no order text or writing is staged. That ordinary absence is not a provisioning fault and is neither a miss nor a source of additional credit.

The conditional narrowed QP1 grant, plenary merits route and possible Thomas participation were never tested, and earn neither credit nor penalty. The 30% CVSG alternative did not occur, but the document expressly made no CVSG its modal forecast; its separate quantitative claim is not rescored here. This grade measures the forecast's realized thrust and specificity, not whether every low-probability alternative happened. Its high score rests on the specific procedural path and timing, not on inferred substantive reasons or unverified writing details; the forecast contains less verified discriminating content than a fully borne-out specific account would.

## Leakage

The harness log records forward mode and October 14 calls, before the November 9 denial. Capture coverage is 37/39 (approximately 94.87%). The two unobserved web queries concern the exact September 21 supplemental PDF and the 2023 Financial Oversight precedent; they are assessed on query scope, not accepted as empty merely because the candidate says no content appeared. Captured calls include retrieval of the dated supplemental brief and consultation of opinion 9393811, a prior precedent, rather than this petition's outcome. The staged supplemental text confirms its subject and pre-decision timing. The log's excluded-path name search does not open labeling artifacts. No post-resolution material about this petition or prior knowledge of its result appears. **influenced_prediction = not_applicable; leakage_suspected = false.**

## Significance

My independent stakes assessment is **0.60**: potentially wide-ranging intangible-property and territorial-immunity questions, limited by the particular trademark dispute and procedural complications. The denial itself creates no merits precedent. No agreement score is calculated.
