# Evaluation — codex-baseline

## Result

The prediction names `denied`, exactly matching the outcome: `correct = 1`. Its P(grant) of 0.01 gives Brier `(0.01 - 0)**2 = 0.0001` and Brier skill `0.961856758794282` against the common baseline below.

## Reasoning quality: 0.89

The rationale is case-specific and appropriately qualified. It distinguishes the petitioner's account from established facts, explains the narrow state-statute reliance dispute, identifies the lack of a demonstrated conflict, and treats the reply-brief timing as a possible preservation problem rather than a proven default. It correctly limits what can be inferred from a response waiver and from missing opposition material. It identifies the frozen risk-set band and prior-Term cut, and separates terminal statistical cuts from a forward conditional probability.

The principal limitation is evidentiary: the author did not read the appendix or full opinion below, so the vehicle and reliance analysis remains based on the petition's presentation. The adjustment from approximately 5.12% to 1% is a reasoned subjective judgment, not an empirically estimated conditional rate. The rationale openly acknowledges both limits. The denial earns exact-outcome credit but does not confirm the proposed legal reasons for denying review.

## Leakage

The harness log records `forward`, with calls on September 17, 2026, before this petition's October 5 resolution. It shows reads of the provisioned September 17 snapshot and petition, the statpack, and operational files. The three web calls concern general Supreme Court rules, not this petition's disposition. Their results are `unobserved`: the author's assertion that they yielded no usable content is not independently confirmed by the transcript. Overall capture coverage is 0.875. The queries themselves do not target outcome material, and the rationale contains no already-decided treatment of this petition. Assessment: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

## Source limitation

The staged petition's jurisdiction paragraph says December 19, 2026, but its factual narrative and the docket snapshot identify the lower-court decision as December 19, 2025. The candidate expressly noticed and reconciled that discrepancy. This is an apparent source-date typo, not evidence of a later decision or leakage; the cell-level flag preserves it for maintainers.

## Scoring basis

This is a cert-stage evaluation against `outcome.json`: denied on October 5, 2026, with `actual_granted = 0`. The October 5 provisioned snapshot independently records “Petition DENIED.” A bare denial supplies no merits rationale; it does not establish why the Court declined review or endorse either party's legal position.

The scored prediction freezes Term 2025, band `baseline`, and `salience_version = sal-v4`. The committed `metrics/statpack.md` heading matches that version, so the baseline basis is `risk_set`, not terminal and not the evaluator's decided-docket context. Pooling the bracketed reached rates over every displayed Term strictly before 2025 uses OT2017–OT2024: respectively 4.7% (n=1643), 4.6% (1524), 4.6% (1399), 4.5% (1739), 5.6% (1500), 5.8% (1192), 5.9% (1312), and 5.7% (1271). Their resolved-weighted rate is 592.925 / 11580 = 0.05120250431778929. The fractional numerator reflects multiplication of rounded displayed percentages, not an observed fractional grant count. This is a denial-reweighted paid-segment estimate from the committed pack; no live corpus refresh or corpus-wide freshness claim is made. The caption displays 10 of 10 Terms; 2025 and 2026 are excluded. This evaluator uses the rendered rates rather than importing a candidate's unrounded calculation.

Brier skill uses `1 - probability**2 / baseline**2`. These are single-event scores, not evidence of cohort-level calibration or forecasting skill. Votes are unscored on cert cells. No semantic grades are declared here. The forecast document was read for context but not scored; quantitative claims remain exclusively for the harness. `reasoning_quality` evaluates only `reasoning.md`, independently of outcome accuracy.
