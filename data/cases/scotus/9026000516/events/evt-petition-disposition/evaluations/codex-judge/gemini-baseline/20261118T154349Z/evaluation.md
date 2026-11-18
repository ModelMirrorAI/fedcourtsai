# Evaluation: gemini-baseline

The event is cert-stage. The staged outcome records `denied`, `actual_granted: 0`, resolved November 16, 2026, with one total distribution, no CVSG, and no noted dissent from denial. The decided snapshot shows October 28 distribution for the November 13 conference followed directly by November 16 denial. No majority opinion, separate-writing files, or complete writing inventory is staged. The bare denial establishes neither agreement with the Fourth Circuit nor a reason for declining review.

The candidate predicted `denied`, so `correct = 1`. With a 3% grant-family probability, the Brier score is `(0.03 - 0)^2 = 0.0009`. The grant axis includes GVRs even though the exact disposition label here is denial.

Reasoning quality: **0.84**. The rationale closely engages the Fourth Circuit's conduct-element analysis and the factual account of procuring information, advising clients, and sending draft returns into North Carolina (petition appendix pp. 15–17). It identifies the count-specific Simmons issue, rehearing opportunity, government waiver, and preservation concession, and gives a coherent explanation for adjusting below the frozen risk-set anchor.

There are two limits. First, it overstates the effect of rehearing when it says that this removes the primary premise of a Lawrence GVR. An opportunity to present the decision weakens a remand request, but a summary rehearing denial does not establish substantive reconsideration; the rationale's own qualification that rehearing does not preclude a GVR partly corrects this. Second, it repeatedly dates the government waiver October 26, while the staged docket records October 21. The waiver and absence of a response request are real, so this date error does not overturn the analysis. Broad practice assertions about the waiver's precise probabilistic force are not estimated by the cited marginal tables. The superior realized Brier score is separate from this qualitative grade.

Base-rate use was checked against historical statpack build `dedb32b153e67d254af10083c3ee247cecd56116` (sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa), reconstructed with `fedcourts statpack-at` from codex-baseline's frozen anchor. All three candidates record that same digest. This is the sal-v6 build in force for their November 1 runs, rather than the current sal-v8 pack; its quoted supporting counts and percentages support the candidate's numerical references. The segment baseline, its basis, and Brier skill are left for the harness; any performance comparison is against the stamped segment base rate. Quantitative claims are not graded here. Cert votes are not scored, and no semantic grades apply.

## Predicted reasoning

Forecast quality: **0.88**. The specific forecast of denial immediately following the first scheduled conference, without another distribution or CVSG, matches the November 16 disposition and final signals. The conditional GVR and plenary-question discussion was never tested and receives neither credit nor penalty. The October 26 waiver date is a minor factual miss: the docket says October 21, while the procedural inference is unchanged. No noted dissent is recorded, but the broader no-separate-writing claim remains unresolved for lack of a complete writing inventory.

## Leakage assessment

The harness records forward mode and November 1 calls, before November 16 resolution. All 61 calls are outcome_only, so null dates/digests do not mean empty results. Queries include this open petition's corpus row, Chollet lower-court dockets, and Abouammo-related authorities. Those were legitimate forward inquiries. Neither query wording nor reasoning shows this petition's November 16 disposition or a decided case provisioned forward.

The prediction froze `mode: forward`, `cutoff: null`, and the November 1 snapshot; the evaluator's November 16 snapshot is the decided record, not evidence of what the predictor was provisioned. No own-case disposition is apparent in the candidate's reasoning. Set `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. Result-capture limitations do not by themselves establish leakage.

My independent stakes assessment is **0.20**: serious individual consequences and a constitutional venue issue, with a limited remand request applying existing precedent. This assessment is the same across candidates and is separate from grant probability.
