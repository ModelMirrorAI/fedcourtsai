# Evaluation: gemini-baseline

## Outcome and scores

This **cert** event resolved as `denied` on October 5, 2026, with `actual_granted = 0`. gemini-baseline also predicted `denied`: exact-label correctness **1**. The probability **0.01** gives Brier score **0.0001**.

The candidate froze **baseline / sal-v4 / Term 2025**. That version matches the committed `metrics/statpack.md` table. On the **risk_set** basis, use the bracketed reached figures for every rendered Term strictly before 2025: **2017–2024**. From newest to oldest, the rate/denominator pairs are 5.7%/1,271; 5.9%/1,312; 5.8%/1,192; 5.6%/1,500; 4.5%/1,739; 4.6%/1,399; 4.6%/1,524; and 4.7%/1,643. Their resolved-weighted mean is **592.925 / 11,580 = 0.05120250431778929**. The numerator is reconstructed from rounded displayed percentages, not an observed integer count. Brier skill is **0.961856758794282**.

The table renders all 10 of its 10 Terms. Excluding 2025 and 2026 is the strict-prior rule, not a truncated-window anomaly. No version mismatch applies. The baseline uses the committed pack's live/historical-slice, denial-reweighted estimates; I made no fresh corpus query. The prediction snapshot is dated September 16, 2026. These scores on a single denial do not establish calibration or broad performance.

## Reasoning quality: 0.64

The rationale correctly identifies the prior-Term baseline range, response waiver, first long-conference setting, and low-grant direction. It recognizes the dispute as concerning the treatment of factual findings under Rule 52(a), rather than mistaking the cert event for a merits judgment. A nonzero small probability is consistent with its stated uncertainty.

The analysis is nevertheless thin. It relies heavily on the government's waiver and then treats the absence of an opposition brief as an additional negative, although these are substantially the same procedural observation. It also infers too much about the government's view of a split or vehicle from that waiver. No developed comparison of the petition with the appellate reasoning supports its categorical characterization of the issue as lacking broader legal significance.

The provisioned appendix contains material that would have strengthened the analysis: documentary findings receive deferential review, legal questions remain subject to de novo review, the trial involved expert evidence, and the appellate court gives alternative reasons for treating the dispute as factual. The rationale does not engage those distinctions or explain the downward probability adjustment beyond general waiver and conference observations. The grade reflects these missing analytical links, not brevity alone and not any penalty for unavailable telemetry.

The eventual denial supports the predicted label, but supplies no explanation validating the candidate's causal account. Only `reasoning.md` contributes to this qualitative grade; the forecast document and quantitative claims remain ungraded here.

## Leakage and retrieval-accounting flag

The log is **forward** and every one of its **34 calls is unobserved**. This is a capture limitation, not evidence that the calls failed or returned nothing. The visible targets are provisioned case files, the statpack, and two broad SCOTUS corpus queries with a September 17 cutoff; neither query names this case or seeks its October 5 disposition. The prediction is dated September 17. The rationale does not presuppose an already-known denial. On this evidence, outcome retrieval is **false**, influence is **not_applicable**, and leakage is not suspected.

There is a narrower reporting discrepancy: `retrieval.md` says there was no retrieval beyond provisioned inputs and the statpack, but the harness records two `fedcourts query` attempts. Their results are unobserved, so success, returned documents, and transfer counts cannot be established. The cell-level flag asks that these attempts be accounted for without inventing results or treating them as outcome leakage. This reporting issue does not alter the numerical scores or the reasoning-only qualitative grade.

Cert votes are unscored. No judgment comparison or semantic grades apply. The harness owns quantitative claim scores and provenance stamps. No independent big-case score is supplied.
