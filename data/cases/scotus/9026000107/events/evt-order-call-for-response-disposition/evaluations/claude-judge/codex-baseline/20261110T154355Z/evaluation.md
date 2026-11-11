# Evaluation: codex-baseline

**P(grant) 0.24, predicted denied. Correct = 1, Brier = 0.0576.**

## Cell
Cert stage, `response-requested` moment, forward mode. Outcome: **denied** on 2026-11-09 (`actual_granted` 0), no noted dissent, no CVSG. The docket shows the BIO filed Oct 1, the reply Oct 9, distribution on Oct 21 for the 11/6/2026 conference, and denial at that first post-response conference with no relist. `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are the harness's to stamp (against the stamped segment base rate for the frozen `baseline` band, sal-v4). Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so I wrote no `semantic_grades`. Base-rate use is graded against the build `statpack-at` resolved for this candidate (sha 7bcde3b105cb, landed 2026-10-28), not the committed pack.

## Leakage
Forward. The prediction ran 2026-10-29, before the 2026-11-09 resolution, so it could not have retrieved the outcome. Neither the log nor the reasoning shows this case's disposition. `influenced_prediction`: not_applicable.

## Big case
My read is 0.3: a recurring takings-ripeness issue with organized amicus support, on a single-lot dispute from an unpublished opinion. The Court denied it quietly.

## Reasoning quality: 0.74
Strengths:
- The anchor is correct and transparently derived. The baseline reached rate pooled over 2017–2025 from statpack.json comes to 660/12,913 = 5.11%, consistent with the resolved build's per-Term rows (4.0–5.9%).
- It handles the cross-cuts carefully: amicus 2+, CVSG, and relist buckets are read as terminal associations, and it explicitly avoids treating the CFR-induced redistribution as a substantive relist.
- Its legal analysis is the most precise of the three. It identifies the QP 2 preservation obstacle in App. 2a n.1, correctly notes that Burford was the district court's conditional remark and not the appellate holding, and reads the Fourth Circuit's distinction of Pakdel as a fact-specific dispute over which local decisionmaker must act.

Weakness: the move from about 5% to 24% is large and admittedly unmeasured. That is roughly 4.7x the anchor on a CFR plus amici signal, against a vehicle the candidate itself judged weak. It is the main reason this candidate's Brier is the worst of the three. The direction was sound; the magnitude was generous.

## Predicted reasoning: 0.66
Central claims: denial after the response; a modal path of one redistribution then denial within the first few conferences; no CVSG; no noted dissent conditional on denial; a QP 1 focus if granted. The first four were borne out; the QP 1 claim is conditional and unresolved. The document is specific on the procedural path, but it keeps the alternatives open ("one genuine post-response relist is a plausible alternative") and carries the most grant-leaning headline, so it scores slightly below the others.
