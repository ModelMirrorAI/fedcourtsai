# Evaluation: codex-baseline

The event is cert-stage. The staged outcome records `denied`, `actual_granted: 0`, resolved November 16, 2026, with one total distribution, no CVSG, and no noted dissent from denial. The decided snapshot shows October 28 distribution for the November 13 conference followed directly by November 16 denial. No majority opinion, separate-writing files, or complete writing inventory is staged. The bare denial establishes neither agreement with the Fourth Circuit nor a reason for declining review.

The candidate predicted `denied`, so `correct = 1`. With a 12% grant-family probability, the Brier score is `(0.12 - 0)^2 = 0.0144`. The grant axis includes GVRs even though the exact disposition label here is denial.

Reasoning quality: **0.92**. The rationale gives a balanced, record-specific explanation for denial despite a genuine intervening-precedent argument. It checks the Fourth Circuit's own conduct-element analysis and the defendants' communications into North Carolina (petition appendix pp. 15–17), rather than accepting the petition's effects-only characterization. It also checks the district court's separate treatment of Counts 18–22 (App. 36), the July 8 rehearing denial (App. 60), and the petition's concession that the venue instruction was not challenged on appeal (Pet. 16). These distinctions support treating Abouammo as a possible basis for reconsideration rather than automatic entitlement to a GVR.

The rationale uses the frozen risk-set anchor, distinguishes terminal relist and amicus cuts from a live forecast, and does not treat the United States as a federal petitioner. Its upward adjustment for the two-day judgment/precedent sequence is transparent but remains a discretionary estimate; the procedural GVR examples supply no matched denominator for the 12% choice. The realized denial cannot validate every doctrinal inference or show that 12% was intrinsically miscalibrated.

Base-rate use was checked against historical statpack build `dedb32b153e67d254af10083c3ee247cecd56116` (sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa), reconstructed with `fedcourts statpack-at` from codex-baseline's frozen anchor. All three candidates record that same digest. This is the sal-v6 build in force for their November 1 runs, rather than the current sal-v8 pack; its quoted supporting counts and percentages support the candidate's numerical references. The segment baseline, its basis, and Brier skill are left for the harness; any performance comparison is against the stamped segment base rate. Quantitative claims are not graded here. Cert votes are not scored, and no semantic grades apply.

## Predicted reasoning

Forecast quality: **0.90**. The central commitments were denial, no additional distribution, resolution in the stated November-to-early-December window, and no CVSG. The staged outcome and docket bear out those specific procedural calls; this goes beyond merely restating a generic expectation of denial. The conditional GVR route and proposed scope were never tested and receive neither credit nor penalty. No noted dissent is recorded, but the broader prediction of no separate writing remains unresolved because no complete writing record is staged. That uncertainty is not counted as a miss.

## Leakage assessment

The harness records forward mode and November 1 calls, before November 16 resolution. The 42 calls concern provisioned inputs, historical statistical context, other GVRs, Abouammo, and Lawrence. Three web calls are unobserved and are assessed from their precedent-only queries, not credited as empty. The sole parsed document date is June 9, 2026. No query or reasoning exposes this petition's own disposition.

The prediction froze `mode: forward`, `cutoff: null`, and the November 1 snapshot; the evaluator's November 16 snapshot is the decided record, not evidence of what the predictor was provisioned. No own-case disposition is apparent in the candidate's reasoning. Set `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. Result-capture limitations do not by themselves establish leakage.

My independent stakes assessment is **0.20**: serious individual consequences and a constitutional venue issue, with a limited remand request applying existing precedent. This assessment is the same across candidates and is separate from grant probability.
