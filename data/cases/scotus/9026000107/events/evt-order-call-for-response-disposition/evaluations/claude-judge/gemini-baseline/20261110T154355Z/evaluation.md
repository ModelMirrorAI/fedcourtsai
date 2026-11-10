# Evaluation: gemini-baseline

**P(grant) 0.06, predicted denied. Correct = 1, Brier = 0.0036.**

## Cell
Cert stage, `response-requested` moment, forward mode. Outcome: **denied** on 2026-11-09 (`actual_granted` 0), no noted dissent, no CVSG. The docket shows the BIO filed Oct 1, the reply Oct 9, distribution on Oct 21 for the 11/6/2026 conference, and denial at that first post-response conference with no relist. `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are the harness's to stamp (against the stamped segment base rate for the frozen `baseline` band, sal-v4). Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so I wrote no `semantic_grades`. Base-rate use is graded against the build `statpack-at` resolved for this candidate (sha 7bcde3b105cb, landed 2026-10-28), not the committed pack.

## Leakage
Forward. The prediction ran 2026-10-29, before the 2026-11-09 resolution, so it could not have retrieved the outcome. Neither the log nor the reasoning shows this case's disposition. `influenced_prediction`: not_applicable.

## Big case
My read is 0.3: a recurring takings-ripeness issue with organized amicus support, on a single-lot dispute from an unpublished opinion. The Court denied it quietly.

## Reasoning quality: 0.60
Strengths: the vehicle analysis is grounded in the appendix and specific. It cites the district court's account of the unretained, unnotarized waiver application, counsel's concession that the February 2022 DPIE letter was not a final decision, the unpublished per curiam, and the Burford warning, each with page cites. It weighs those against the CFR, the six amici and experienced counsel, and lands on a low number that turned out well calibrated.

Weaknesses:
- **The base-rate figures it quotes do not match the build it ran against.** It reports baseline reached rates of 5.3%/6.9%/6.9% for OT2023–2025 (n = 513/1,277/1,452). The resolved build (7bcde3b105cb) shows 5.9%/5.9%/4.0% (n = 1,312/1,274/1,314). The anchor is misstated, though the final number is not far off.
- It pools only three of the nine prior Terms the table offers, without saying why.
- It asserts that post-Pakdel circuit decisions "generally" treat plan amendments as part of the ordinary finality inquiry, with no retrieval behind the claim (its CourtListener access was rate-limited).
- It treats the district court's Burford remark as a "looming alternative ground" when it was not the appellate holding.
- It ignores the QP 2 preservation problem (App. 2a n.1).

## Predicted reasoning: 0.70
Central claims: denial at or shortly after the post-response conference; one more distribution with a modest relist chance; no CVSG; no dissent from denial likely; denial driven by vehicle defects. The first four were borne out by the docket and the outcome. The vehicle rationale is unresolved, because an unexplained denial does not say why. The QP 1 restriction and the summary-route content were conditional on a grant and earn nothing. The document commits specifically and was right, but on the modal path for a weak-vehicle CFR petition, so it sits between 0.5 and 0.75.
