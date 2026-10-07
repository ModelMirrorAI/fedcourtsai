# Evaluation: gemini-baseline

## Outcome and score

This is a cert-stage arrival prediction. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The predicted label is `denied`, so correctness is **1**. Brier loss is `(0.001 - 0)^2 = 0.000001`. A small loss on this denial does not establish calibration across cases.

## Analysis quality: 0.62

The rationale identifies the petition's central vehicle problems: a pro se dissolution dispute, record-dependent procedural complaints, and no developed conflict. Those observations support a substantial downward adjustment from a broad paid-petition prior. The provisioned petition confirms the state-court dissolution posture and complaints about subsection miscitation, notice, and incomplete transcripts.

The reasoning is nevertheless too categorical. Its assertion of no federal interest does not distinguish lack of an institutional federal stake from the expressly presented federal due-process issues. Its adequate-state-ground characterization does not engage the petition's contention that the procedural ground was inadequate. The claim that the Court rarely, if ever, reviews this subject matter is unsupported within the analysis. The drop from approximately 6.5% to 0.1% has little quantitative justification. The denial supports the forecast's label, not those stronger propositions or a particular explanation for the Court's action.

## Baseline and scoring boundaries

The prediction freezes `baseline`, `sal-v3`, Term 2026. The committed statpack's segment heading is `sal-v4`. This version mismatch requires omitting `segment_base_rate` and `brier_skill_score` and leaving `base_rate_basis` null; a terminal fallback is not permitted for a frozen band. The mismatch is recorded in the cell's flags. I do not treat the current table as verification or refutation of the historical 6.5% anchor.

The forecast document was read for context only. Neither it nor the quantitative claims contributes to this quality grade; claim scoring belongs to the harness. No vote accuracy or semantic grades are written on this cert cell.

## Leakage

The logged mode is forward. Prediction and calls date to August 16, before this case's October 5 resolution. The query scopes and prose show no already-decided disposition. All 21 result markers are unobserved, so their null dates and digests do not prove that nothing was returned. With that limitation, the evidence supports no retrieved outcome material and `not_applicable` influence, not a leakage exclusion.
