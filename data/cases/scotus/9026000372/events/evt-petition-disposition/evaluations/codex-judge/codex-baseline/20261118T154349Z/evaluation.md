# Evaluation: codex-baseline

This is a **cert-stage** evaluation of scotus/9026000372, evt-petition-disposition. The realized outcome was **denied** on November 16, 2026, with actual_granted = 0. codex-baseline predicted **denied**, so **correct = 1**. Its grant probability was 0.04; **Brier score = (0.04 - 0)^2 = 0.0016**.

## Rationale quality

The rationale gives a strong, balanced explanation for a modest downward adjustment from the frozen anchor. It separates the new completed-appeal/finality question from Fuld's earlier personal-jurisdiction holding, identifies the absence of a demonstrated square split, and explains the lower court's discretionary recall reasoning rather than simply adopting the petition's characterization. The appendix confirms the distinction between legislative compulsion and judicial discretion, the without-prejudice dismissal, and the still-pending second action (printed 16a–27a). It correctly treats the response waivers as party choices and gives the earlier stay denial limited weight.

The statistical discussion distinguishes reached-band from terminal populations, overlapping marginal cuts from independent signals, and a deliberately denial-selected corpus sample from a usable frequency estimate. It also recognizes that an empty similarity search does not establish the absence of similar issues. The remaining limit is that the move to a precise 4% probability rests on qualitative judgment rather than a validated conditional model. The unexplained denial cannot verify the proposed judicial motivations. Reasoning quality: **0.94**, assessed from reasoning.md alone.

## Statistical provenance and scoring boundaries

All three staged predictions pin the same statpack digest. I reconstructed that build with statpack-at using gemini-baseline's blinded directory: **dedb32b153e67d254af10083c3ee247cecd56116**, digest **sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa**, with no alternative build. Statistical references are assessed against that historical sal-v6 pack, rather than today's sal-v8 pack. The rationale's reported anchor is consistent with its frozen context; I do not calculate or supply another baseline. The **stamped segment base rate**, its basis, and Brier skill are the harness's responsibility.

Quantitative claims are left for code to score; no claim_scores block is written. Cert votes are not scored, so vote_accuracy is omitted. No semantic claim set is declared for this cert event, so semantic_grades is omitted. The absent opinion/writings slots are ordinary record availability, not a staging defect.

## Predicted reasoning

The central forecast was denial following the November 13 conference, no further distribution or response request, no CVSG, and no recorded dissent. Those specific procedural calls match the November 16 docket and the outcome signals. Its narrower-follow-on explanation for the Court's action remains unresolved because no reasons for denial are staged. Likewise, the absence of a separate statement cannot be independently established from the staged record. The question formulation and plenary-versus-summary discussion were conditional on a grant that never occurred and earn neither credit nor penalty. Forecast quality: **0.90**.

This grade assesses predicted_reasoning.md alone and does not change reasoning_quality or the mechanical scores. A denial does not endorse the lower court's reasoning or reveal a merits vote lineup.

## Leakage assessment

Forward prediction made October 31, before the November 16 resolution. Captured calls target provisioned inputs, an earlier-Term denial sample, and the earlier Fuld opinion. The web search is unobserved; its query concerns prior Fuld authorities, so no empty-result credit is given. Capture coverage is 34/35. No call or reasoning cites this petition's disposing order or post-resolution facts; prior stay and Fuld decisions are legitimate pre-resolution context.

Accordingly, mode is **forward**, retrieved_outcome_material is **false**, influenced_prediction is **not_applicable**, and leakage_suspected is **false**. The evaluator's decided snapshot is used only to evaluate the forecast; its later contents are not attributed to the candidate's October 31 snapshot. No capture limitation is treated as proof that a query returned nothing.

## Stakes

My independent significance assessment is **0.65**: a large terrorism judgment and a substantial jurisdiction/finality issue with foreign-relations implications, tempered by the highly unusual statutory history and the denial's absence of a new merits holding.
