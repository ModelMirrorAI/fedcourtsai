# Evaluation: gemini-baseline

## Outcome and accuracy

This is a cert-stage arrival cell. The November 13, 2026 docket entry grants review limited to Questions 1 and 2. The authoritative outcome nevertheless uses `granted`, not `granted-in-part`, and records the plenary route. The candidate's `granted` label receives **correct = 1**. Its probability 0.98 gives **Brier = (0.98 - 1)^2 = 0.0004**.

No cert votes are scored; judgment accuracy and semantic grading are inapplicable. Structured quantitative claims are reserved to the harness, as are the stamped segment base rate, its basis, and skill score.

## Reasoning quality: 0.70

The rationale identifies the strongest basic considerations: the Solicitor General seeks review of a major presidential immigration policy invalidated below, and the dispute combines executive authority with consequential limits on classwide relief. Its analogy to Trump v. Hawaii is relevant at the level of certworthiness. It recognizes the arrival posture rather than treating a zero-distribution docket as a terminal denial signal.

The evidentiary support is thinner than the near-certainty conclusion. There is no explicit pooled prior or disciplined explanation for the magnitude of the uplift, and little engagement with the statutory arguments against the government, the lack of a circuit conflict, or possible vehicle and mootness concerns. Summary disposition changes the route rather than necessarily defeating a grant-family forecast, so it does not by itself adequately explain uncertainty in the headline probability. Most concretely, the rationale says the weakest historical federal-band reached rate exceeded 50%, but the candidate-era table includes **43.5% in OT2018**. The correctly quoted OT2025 and OT2024 entries do not support that generalization. The correct outcome does not erase these analytical shortcomings. This grade excludes independent impressions of the structured claims and predicted_reasoning.md.

Before finding that error I reconstructed the historical pack using `statpack-at`. It returned build `02dd6a20fccc232651e3e13cdea3da3066e41c5b`, digest `sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, inferred from the run rather than pinned in the prediction, with no alternative build. The OT2018 row is in that historical sal-v3 table, so the issue is not disagreement with today's refreshed pack. I supply no independently pooled scoring anchor.

## Predicted reasoning

**Grade: 0.70.** The document correctly calls a plenary grant after the first or second distribution and no CVSG. The staged docket records two distributions and a grant at the second listed conference, supporting a specific procedural forecast rather than only the ultimate direction.

Its forecast that all three questions would be taken failed: the Court expressly excluded Question 3 and granted only Questions 1 and 2. This is a meaningful scope miss, though the document's dominant prediction of prompt plenary review survived. The grade sits below the mostly-borne-out anchor because the document does not merely miss an incidental detail; it overpredicts the breadth of review. The record cannot confirm that national importance was the Court's actual reason for granting, and the predicted dissent on a hypothetical denial is unresolved, not a miss. The realized grant does not validate the denial-writing counterfactual.

## Leakage

The log identifies **forward** mode, with the forecast on August 25 and disposition on November 13. Its **0.0 result-capture coverage** is an observation limitation, not evidence of empty results, a tooling defect, or wrongdoing. I assessed the queries and prose: they concern the arrival snapshot, petition, statpack, and a lower-court opinion search under the parties' name. The retrieval note identifies an April 24 appellate opinion, not a Supreme Court disposition. No available evidence shows this petition's grant order or later result reaching the prediction. Thus retrieved_outcome_material is false on the available evidence, influence is not_applicable, and leakage_suspected is false, without claiming to have inspected the uncaptured returns.

## Significance

Independent stakes assessment: **0.94**, based on the nationwide asylum/entry policy and remedial issues, not the predictor's own score.
