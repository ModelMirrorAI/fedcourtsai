# Evaluation: codex-baseline

## Assessment of the rationale

The denied label is correct (correct = 1). With P(grant) = 0.02, Brier = (0.02 - 0)^2 = 0.0004 and skill against the rendered risk-set baseline is 0.8474270351771281.

Reasoning quality: 0.88. The analysis distinguishes grant probability from the merits, anchors on the correctly versioned prior-Term risk set, and explains its downward adjustment with specific features of the supplied petition: first-impression/error-correction framing rather than a demonstrated square conflict, the reported nonprecedential decision, intertwined state and federal theories, and transactional complexity. It treats respondent waivers as a modest signal rather than a resolution, acknowledges the one-sided petition and missing separate lower opinion, and preserves the financing-stakes counterargument. Its discussion of the historical notice precedent expressly limits the analogy rather than claiming it resolves the special-assessment issue.

The principal limits are the subjective size of the reduction to 2% and incomplete independent examination of the lower court's grounds. The candidate's approximately 5.1209% anchor uses unrounded aggregate inputs; the evaluator's 5.12025% uses the required rendered table. That rounding difference is immaterial and is not a salience-version or window mismatch. The denial makes the outcome call correct but does not verify the candidate's proposed explanation of why review was unattractive.

## Baseline and scoring boundary

This is a cert-stage evaluation against outcome.json: denied, actual_granted = 0, resolved October 5, 2026. The provisioned October 5 snapshot independently records “Petition DENIED.” A denial supplies no substantive explanation for the Court's decision; it does not establish that any proposed jurisdictional or merits rationale was adopted.

The prediction froze Term 2025, band baseline, and salience_version sal-v4. The committed metrics/statpack.md heading matches sal-v4. I use the bracketed reached rates, with base_rate_basis = risk_set, pooling every displayed Term strictly before 2025: 2017–2024. In descending Term order the rate/weighted-n pairs are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. Their resolved-weighted pool is 592.925 / 11580 = 0.05120250431778929. This is an approximation from the rendered percentages, not an integer grant count. The table renders all ten of its ten Terms, so there is no truncated-window discrepancy. Terms 2025 and 2026 are excluded; the October 2026 resolution does not change the prediction's docket-number Term. This describes the committed pack read in this cell, not a refreshed corpus estimate.

I grade reasoning.md only. The forecast document was read for context but not scored, and the quantitative claims are left to the harness. No vote accuracy or semantic grades are written on this cert cell. No independent big-case assessment is supplied.

## Leakage assessment

Mode is forward. All recorded calls occurred September 17, before the October 5 disposition. The log covers the September 17 input snapshot, petition materials, aggregate tables, general rules, and historical precedent. Its capture coverage is 28/31, approximately 90.3%. Three web calls are unobserved: the general Rule 10 search and two rules-guidance opens. The candidate reports no usable results, but the log itself cannot establish that; the visible queries are nevertheless not outcome-seeking. No query or prose shows this petition already decided. Thus retrieved_outcome_material = false, influenced_prediction = not_applicable, and leakage_suspected = false. This is an evidence-limited forward assessment, not proof of the contents of uncaptured results.
