# Evaluation: claude-baseline

## Outcome and numerical scores

This is a cert-stage evaluation of Marion Alexander Lindsey v. South Carolina. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied`, so exact-label correctness is **1**. Its probability of any grant was **0.08**; Brier loss is `(0.08 - 0)^2 = 0.0064`.

The candidate's own frozen context supplies Term **2025**, band **baseline**, and salience version **sal-v4**. That version matches the committed Markdown statpack. I use the bracketed baseline **reached** rates for all displayed strictly-prior Terms, **2017–2024**, rather than terminal rates or the evaluator's decided-docket band. Weighted denominators sum to **11,580**. Multiplying the displayed, rounded rates by those denominators yields **592.925** weighted grant equivalents, not an integer count: the resulting baseline is **0.05120250431778929**. The table renders 10 of 10 Terms; 2025 and 2026 are excluded. No rendered-window divergence is present.

The basis is `risk_set`. Skill is `1 - 0.0064 / 0.05120250431778929^2 = -1.4411674371659498`. The candidate correctly called denial but assigned more probability to a grant than this baseline, producing greater loss on this event. This single observation does not establish cohort calibration or general forecasting skill. These are calculations from the committed statpack, not claims about freshly queried corpus state. The case snapshot consulted is dated October 5, 2026; the candidate's frozen snapshot date is September 15, 2026.

## Reasoning quality: 0.86

The rationale substantially engages both sides of the supplied record. It separates the claimed cumulative-prejudice conflict from the vehicle objection that the state court neither adopted the disputed categorical rule nor was asked to resolve it. The supplied opposition, printed pages 16–22, supports treating preservation, aggregation already performed, and assumed versus established deficiencies as serious contested obstacles. The candidate also distinguishes the proposed-order question from an automatic entitlement to review and acknowledges the missing reply and its limited reading of the state opinion. Its explicit reached-band anchor and caution against multiplying marginal capital and relist associations are strengths.

The main limitations are the relatively categorical description of a real split, the qualitative conversion of those considerations into a 1.5-fold probability adjustment, and broad assertions about recent capital grants and the Court deferring to ongoing habeas proceedings without a demonstrated comparable-case analysis. The independent state-opinion and federal-habeas retrieval is documented, but I do not treat the candidate's account of that material as independently reverified here. These limitations lower the grade without making the overall vehicle analysis unsound.

Denial is consistent with the forecast but supplies no explanation establishing that the Court adopted any particular vehicle or merits argument. This grade concerns only the analysis in `reasoning.md`; the forecast document and structured claims were read for context and are not scored into it. No vote accuracy or semantic grades are written on this cert cell; mechanical claim scores belong to the harness.

## Leakage

The harness log records **forward** mode and **29/29 captured calls**. The prediction was made September 16, before the October 5 resolution. Logged case-related searches concern the earlier state opinion, the separate federal habeas docket and execution timing. The legible retrieved dates include November 5, 2025, February 10 and June 26, 2026, with a separate corpus-prior result dated September 10, 2026. None supplies the disposition of this cert petition. A final status-filter command's reference to an excluded labeling path is not a read of the labeling artifacts. The reasoning does not presuppose denial as an accomplished fact. I record no outcome material observed, influence `not_applicable`, and `leakage_suspected = false`.
