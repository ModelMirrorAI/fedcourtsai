# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage cell. The committed outcome records a standard, plenary grant on November 13, 2026, with `actual_granted: 1`. The staged docket specifies: "Petition GRANTED limited to Questions 1 and 2 presented by the petition." The grant followed the November 9 redistribution, bringing the distribution count from the candidate's frozen one to two. No CVSG is recorded.

The predicted label `granted` matches exactly: `correct = 1`. With probability 0.86, the Brier score is `(0.86 - 1)^2 = 0.0196`. Cert votes are not scored; no vote-accuracy field is written. Baseline and skill fields are left to the harness; any comparison uses the stamped segment base rate. No quantitative claims are scored here, and this cert cell has no semantic grading block.

## Reasoning quality

Score: **0.92**, grading `reasoning.md` alone. The analysis distinguishes certworthiness from ultimate government success, locates the statutory and remedial issues, and takes the opposition's Chenery, unchallenged-vacatur and class-definition objections seriously. It explains why nationwide importance can justify review without a developed split and explicitly avoids counting government sponsorship twice. Its use of the supplied reply identifies a genuine companion-case hold/GVR alternative without treating that possibility as knowledge of this petition's disposition. Advocacy about migration effects is appropriately labeled as advocacy.

Historical base-rate use was checked against the contemporaneous statpack reconstructed by `statpack-at`: build `a14b36a1e190a86d6a01df2ce410f5f9e54fb98b`, digest `sha256:84a5c25d4bf0a2a70ba5c6e9392e2e21d43ed5b794de0ae59c27cf1973ad0e7e`, not today's pack. The prior-Term federal risk-set rows support the rationale's calculation and exclusion of the case's own Term. No evaluator-computed anchor is substituted for the stamped segment base rate. The remaining limitation is that the size of the upward probability adjustment and companion-route weight is judgmental rather than empirically established; the grant alone cannot validate those choices or the parties' merits theories.

## Predicted reasoning

Score: **0.90**, grading `predicted_reasoning.md` separately. The central claims were a plenary grant, one further distribution, a November-December grant, no CVSG, and review centered on Question 1 with possible narrowing. The November 9 redistribution and November 13 grant specifically substantiate the procedural forecast. Questions 1 and 2 were taken, Question 3 was excluded, which is compatible with the forecast's scope but was not its precise committed selection. That flexibility limits top-of-scale specificity.

The anticipated merits reasoning is unresolved: the staged record contains no merits judgment or opinion. Conditional denial writings and the alternative hold/GVR path did not occur and earn neither credit nor penalty. Unresolved merits reasoning does not reduce the grade. These conclusions do not alter the separate rationale grade.

## Leakage

The harness log records forward mode, with 30 calls and 0.9 result-capture coverage. The October 13 prediction precedes the November 13 disposition. Captured calls concern the supplied record, contracts, schemas, statpack and output work. The three unobserved web calls concern general Court rules, not this petition or its result; the candidate's report that they returned nothing cannot independently establish their contents. The queries themselves supply no outcome-directed evidence. The companion-case material was in the supplied October reply and is legitimate forward information. No retrieval or reasoning shows this petition already resolved: `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`.

## Stakes

Independent evaluator significance: **0.92**. The questions affect nationwide asylum access, executive immigration authority and classwide relief. This assessment rests on the questions and record, not the candidate's stakes number or a predicted merits winner.
