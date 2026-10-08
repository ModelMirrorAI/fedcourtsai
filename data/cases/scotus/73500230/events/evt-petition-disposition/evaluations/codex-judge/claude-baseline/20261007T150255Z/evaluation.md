# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage distribution event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`; the October 5 snapshot also records “Petition DENIED.” The September 17 prediction named `denied`, so exact-label correctness is **1**. Its grant probability was **0.08**, giving Brier loss `(0.08 - 0)^2 = 0.0064`.

The baseline uses the prediction's frozen `baseline` band, `sal-v4`, and Term **2025**, not the evaluator's terminal context or the Term in which denial occurred. The committed statpack heading matches that version. The bracketed reached rates for all displayed strictly earlier Terms, 2017–2024, give a denominator-weighted rate of **0.05120250431778929**: weighted numerator 592.925 from rounded percentages, denominator 11,580. This is a denial-reweighted paid-segment estimate, not an exact reconstructed grant count. The caption renders 10 of 10 Terms; 2025 and 2026 are excluded, so there is no rendered-window divergence. Basis is `risk_set`; skill is `1 - 0.0064 / 0.05120250431778929^2 = -1.4411674371659498`. The correct denial label does not imply better loss than the lower-probability baseline on this single denial.

These figures use the committed pack, not a newly refreshed corpus. No corpus freshness claim is made; no corpus service was queried.

## Reasoning quality: 0.86

The rationale is substantive and balanced: it starts from the appropriate prior-Term risk set, recognizes the response request and asserted circuit conflict, and weighs those against preservation, independent grounds, unfinished proceedings, and the unpublished disposition. It considers both sides' filings and identifies where an adjustment is judgmental rather than estimated. Its distinction between a response request and a CVSG, and between repeated notices for one conference and a true relist, is careful.

Limitations prevent a higher score. The treatment of prior anti-SLAPP denials is somewhat categorical despite differences among the questions and vehicles; a denial elsewhere does not itself establish how this vehicle should be weighted. The discount for small parties and non-elite counsel lacks a demonstrated empirical basis. The candidate acknowledges relying on advocacy rather than independently reading the lower-court opinions. The bare denial supports the selected label but does not establish that the Court adopted any particular vehicle objection. This grade assesses analytical soundness, not merely the favorable result.

## Leakage and scope

The harness log says `forward`, with 29 of 29 results captured. The reviewed queries, retrieval note, and both prose documents show no target-case outcome retrieval or presupposed denial. The opposition and reply were filed before the prediction, and the cited earlier denials concern other petitions. Captured digests and null document dates do not expose full returned text; the assessment rests on the combined queries and prose, not an inference that null dates mean no retrieval.

The forecast document was read only for context. Its timing, claims, and conditional merits forecast do not enter reasoning quality. Mechanical claim scores remain the harness's. No semantic grades or vote accuracy are written on this cert event. The optional independent significance assessment is omitted because none was formed before viewing the candidate's significance score.
