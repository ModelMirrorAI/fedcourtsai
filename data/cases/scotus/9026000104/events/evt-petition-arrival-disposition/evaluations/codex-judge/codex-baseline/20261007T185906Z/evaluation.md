# Evaluation: codex-baseline

## Outcome and quantitative score

The cert-stage outcome records a standard plenary grant on October 1, 2026, with `actual_disposition = granted` and `actual_granted = 1`. The October 4 snapshot contains the corresponding grant entry. codex-baseline predicted `granted` on August 16, giving exact-label correctness **1**. The Brier score is **(0.71 - 1)^2 = 0.0841**. Neither this score nor the grant establishes the outcome of the underlying merits dispute.

## Reasoning quality: 0.86

The rationale's strength is disciplined use of limited information. It selects the prediction-time federal-band risk set rather than treating a zero-distribution arrival state as a terminal failure-to-relist signal. It explicitly separates the grant-family probability from the most likely exact disposition. It refuses to invent a question presented, circuit conflict, vehicle defect, or lower-court holding when substantive documents are unavailable, and describes its forecast as class-conditional rather than case-specific. Its modest confidence and near-zero adjustment from the reported prior follow that limitation coherently.

The score is not higher because the analysis cannot assess the case-specific legal grounds or alternative vehicles, and the staged material does not independently establish the exact historical count reconstruction it quotes. Its reported prior is useful as an explanation of its choice, not a substitute for a compatible baseline at evaluation. A correct outcome does not erase the substantive information gap; conversely, missing documents alone do not make a candid prior-based forecast unsound.

This quality judgment concerns `reasoning.md` only. The forecast document was read for context and not scored. The quantitative claims are left to the harness. No vote accuracy or semantic grades are written on this cert event.

## Baseline refusal

codex-baseline's frozen context records `federal`, `sal-v3`, and Term 2026. The evaluation-time statpack's segment-table heading is **sal-v4**, rendering 10 of 10 Terms. The version mismatch requires omission of `segment_base_rate` and `brier_skill_score` and a null `base_rate_basis`. I do not use the evaluator's terminal band or rename the frozen-band comparison as terminal. The cell-level flag records the incompatibility. It is not evidence that the candidate used the wrong version when it predicted.

## Leakage assessment

The harness log identifies forward mode and contains 29 captured calls, dated August 16. It includes reads of the candidate's then-provisioned snapshot, the statpack, code/schema material, and prediction examples for other cases. These are not evidence that this petition's later disposition was known. The prose reports a lower-court search returning HTTP 429; no corresponding MCP search row appears in this staged transcript, so I do not independently certify either its result or the completeness of that part of the self-report. Captured coverage of listed calls does not establish coverage of every described action.

No visible query, dated document, or reasoning passage reveals this case's October 1 grant in advance. The rationale affirmatively acknowledges that the holding and vehicle facts are unknown rather than presupposing an outcome. Accordingly `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, limited to the evidence available. The present October 4 snapshot is not used as a proxy for the August baseline. No external retrieval was undertaken.
