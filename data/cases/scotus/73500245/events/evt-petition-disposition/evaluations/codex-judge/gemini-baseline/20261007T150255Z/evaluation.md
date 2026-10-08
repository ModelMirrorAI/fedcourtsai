# Evaluation — gemini-baseline

## Result

The prediction names `denied`, exactly matching the outcome: `correct = 1`. Its P(grant) of 0.002 gives Brier `(0.002 - 0)**2 = 0.000004` and Brier skill `0.9984742703517713` against the common baseline below.

## Reasoning quality: 0.50

The short rationale correctly identifies the procedural-due-process subject, the baseline band, a roughly 5% prior rate, and the respondent's July 1 waiver. A downward adjustment for a narrow dispute is coherent, but the analysis does not substantiate the magnitude of its reduction to 0.2%. Calling the waiver a “definitive signal” of respondent beliefs overstates what the docket records. The possibility of a later response request is not meaningfully integrated into the probability rationale.

The document does not engage the petition's specific reliance argument, its account of the distinction between retention of funds and other disciplinary charges, or the possible federal-issue preservation problem. The captured query list names the questions presented and document manifest but contains no petition-body read; this is consistent with the rationale's limited substantive engagement, though the unobserved results prevent a complete reconstruction of what was displayed. A concise rationale is not penalized for brevity itself; the deduction is for unsupported certainty and omitted case-specific analysis. Correctly predicting a denial does not cure those limitations or establish that 0.2% was well calibrated.

## Leakage

The harness log records `forward`; its calls are on September 18, 2026, before the October 5 resolution. Every logged result is `unobserved`, with capture coverage 0.0. This is a telemetry limitation, not a defect or proof that nothing was returned. Assessment rests on the queries and prose: the queries name the provisioned September 17 snapshot, context, event, document manifest, questions presented, statpack, and operational output/validation steps. No query seeks the petition's disposition or external subsequent history, and the prose does not presuppose a decided case. Assessment: `retrieved_outcome_material = false` on the visible evidence, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is not a claim that uncaptured result contents were inspected.

## Source limitation

The staged petition contains an apparent lower-court decision-date typo, documented in the cell-level flag. The candidate does not rely on that date; it does not affect the mechanical score or leakage assessment.

## Scoring basis

This is a cert-stage evaluation against `outcome.json`: denied on October 5, 2026, with `actual_granted = 0`. The October 5 provisioned snapshot independently records “Petition DENIED.” A bare denial supplies no merits rationale; it does not establish why the Court declined review or endorse either party's legal position.

The scored prediction freezes Term 2025, band `baseline`, and `salience_version = sal-v4`. The committed `metrics/statpack.md` heading matches that version, so the baseline basis is `risk_set`, not terminal and not the evaluator's decided-docket context. Pooling the bracketed reached rates over every displayed Term strictly before 2025 uses OT2017–OT2024: respectively 4.7% (n=1643), 4.6% (1524), 4.6% (1399), 4.5% (1739), 5.6% (1500), 5.8% (1192), 5.9% (1312), and 5.7% (1271). Their resolved-weighted rate is 592.925 / 11580 = 0.05120250431778929. The fractional numerator reflects multiplication of rounded displayed percentages, not an observed fractional grant count. This is a denial-reweighted paid-segment estimate from the committed pack; no live corpus refresh or corpus-wide freshness claim is made. The caption displays 10 of 10 Terms; 2025 and 2026 are excluded. This evaluator uses the rendered rates rather than importing a candidate's unrounded calculation.

Brier skill uses `1 - probability**2 / baseline**2`. These are single-event scores, not evidence of cohort-level calibration or forecasting skill. Votes are unscored on cert cells. No semantic grades are declared here. The forecast document was read for context but not scored; quantitative claims remain exclusively for the harness. `reasoning_quality` evaluates only `reasoning.md`, independently of outcome accuracy.
