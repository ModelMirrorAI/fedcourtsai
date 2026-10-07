# Evaluation: claude-baseline

## Outcome and quantitative scores

The cert-stage outcome is `denied`, resolved October 5, 2026, with `actual_granted = 0`. The September 16 prediction names the same disposition: **correct = 1**. Its grant probability **0.022** yields Brier loss `(0.022 - 0)^2 = 0.000484`.

The prediction freezes `baseline`, `sal-v4`, and OT2025. The matching statpack table therefore supplies a risk-set, not terminal, baseline. The displayed strictly-prior baseline `reached` rows are OT2024 5.7% at n=1271; OT2023 5.9% at n=1312; OT2022 5.8% at n=1192; OT2021 5.6% at n=1500; OT2020 4.5% at n=1739; OT2019 4.6% at n=1399; OT2018 4.6% at n=1524; OT2017 4.7% at n=1643. Resolved-weighted pooling gives **592.925 / 11,580 = 0.05120250431778929**. The fractional numerator comes from displayed rounded rates and weighted denominators, not an integer grant count. These are denial-reweighted live/historical-slice estimates. The table displays all ten pack terms, and all eight preceding OT2025 are used; there is no window mismatch.

Thus `base_rate_basis = risk_set` and skill is `1 - 0.000484 / 0.05120250431778929^2 = 0.815386712564325`. The candidate's approximately 5.1% anchor is consistent with this calculation. The evaluation uses the committed artifact, not a newly queried corpus; case outcome evidence is the supplied outcome and October 5 snapshot.

## Reasoning quality: 0.82

The main legal analysis is strong. It connects the alleged split to the actual bargaining facts, identifies the independent premature-impasse theory, distinguishes substantial-evidence review from statutory interpretation, and addresses preservation of the consequential-remedies challenge. The staged union opposition's printed pages 7–8 and 19–24 substantiate those vehicle arguments as arguments in the record. The rationale also recognizes that the federal respondent opposed rather than sought remand, discloses retrieving that filing, and explains why denial of the separate Macy's petition weakens the proposed hold route without eliminating future possibilities.

The principal reservation is evidentiary overconfidence at the margins. The rationale tends to resolve disputed characterizations of the underlying opinion firmly despite acknowledging that it did not read that opinion itself. An earlier emergency-stay denial is weak and procedurally different evidence of cert interest; silence about dissent does not establish any Justice's merits view. Absence of amici likewise gives only indirect evidence of review prospects or stakes. A few selected labor-case outcomes from broad, capped corpus queries do not establish a well-matched empirical comparison group. These points warrant discounting the force of the downward adjustment, not discarding the substantive vehicle analysis.

The 2.2% choice remains an explicit judgmental adjustment rather than a fitted estimate. The score is based on that rationale's support and calibration, not the fact that its probability produced a small realized Brier loss. The bare denial does not validate the candidate's account of the Court's reasons. Ancillary claim probabilities and the separate forecast document do not enter this qualitative score.

## Leakage and scoring boundaries

The prediction is forward, and its 36 logged calls all occurred on September 16, before the October 5 resolution. Result-capture coverage is 1.0. Visible retrieval includes the predecision federal opposition, broad corpus queries for other labor cases, and CourtListener searches concerning Macy's; the one extracted document date is May 14, 2026. The log also includes an example-artifact lookup, but its query does not establish access to this petition's eventual outcome. The staged log provides query slices and result digests rather than full result bodies, so capture is not proof of exhaustive substantive visibility.

The disclosed Macy's denial and this litigation's separate emergency-stay denial are not the cert outcome being predicted. No visible query, date, or passage treats this petition as already denied. Outcome-material retrieval is therefore false on the available record, influence is `not_applicable`, and leakage is not suspected. Differences in lawful forward retrieval are not leakage.

The pointed-to forecast was read but not graded. No cert vote accuracy or semantic grades are written, and claim scores remain the harness's. The optional big-case assessment is omitted because an independent assessment was not formed before candidate exposure.
