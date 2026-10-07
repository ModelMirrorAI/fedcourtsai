# Evaluation: codex-baseline

## Outcome and scores

The cert-stage outcome records denial on October 5, 2026, and `actual_granted = 0`. The September 16 prediction's `denied` label matches exactly: **correct = 1**. Its 0.003 grant probability gives **Brier = 0.000009**.

The prediction freezes `baseline` under `sal-v4`, Term 2025. The committed statpack uses the same version. Its bracketed reached figures for all displayed strictly-prior Terms, 2017–2024, pool to a rounded-rate weighted numerator of 592.925 over 11,580: **segment base rate = 0.05120250431778929**, on the `risk_set` basis. The rate-percent/denominator pairs are 5.7/1271, 5.9/1312, 5.8/1192, 5.6/1500, 4.5/1739, 4.6/1399, 4.6/1524, and 4.7/1643. Skill = 1 - 0.000009 / baseline² = **0.9965671082914854**. Rounded published percentages make the baseline approximate. Terms 2025 and 2026 are excluded; the caption says 10 of 10 pack Terms are displayed, so there is no indicated display truncation.

The statpack is the committed input, not a newly queried census; corpus-wide freshness was not obtained. The petition manifest records a July 17, 2026 fetch, and the prediction's frozen snapshot date is September 16, 2026. The supplied October 5 outcome supplies the evaluation ground truth.

## Reasoning quality: 0.93

The rationale carefully separates the petition's allegations from established facts and its sweeping requested remedies from the narrower judgment it seeks to challenge. The staged questions and the petition's account of the appellate memorandum support this assessment. The candidate identifies specific evidentiary disagreements and missing vehicle support, rather than treating the respondent's prominence or the subject matter's public importance as a sufficient reason for review.

It also distinguishes an absent docket entry from proof of waiver, a single distribution from relist history, and pro se status from an independent substantive defect. Its account of the unavailable lower opinions is appropriately qualified. The prior-Term reached-band calculation is reproducible, and the candidate explicitly recognizes both rounding and the difference between risk-set and terminal rates. These distinctions make the rationale unusually well supported and transparent.

The residual limitation is the size of the discretionary probability reduction. The record supports moving substantially below the band anchor, but it does not identify an empirical comparison group establishing 0.3% rather than another small probability. Missing lower-opinion and opposition text limits independent verification of the asserted vehicle weaknesses. A correct denial prediction does not prove the Court adopted the candidate's account or that its precise probability was calibrated.

The quality score grades `reasoning.md` alone. The forecast document was read only for context; its details and the structured claims are not scored here. The cert event declares no semantic grading set, and no cert vote accuracy is supplied. The optional independent big-case assessment is omitted.

## Leakage

The log records 24 forward-mode calls on September 16, before the October 5 denial. Capture coverage is 0.875: 21 results captured and three web results unobserved. Those three queries concern general Rule 10 material; missing telemetry does not establish that they returned nothing. The captured shell request likewise targets the general rule, not the case's disposition. A search for instruction files excludes the prohibited labeling path, so its textual occurrence is not evidence of a read. The remaining query slices and rationale show no post-resolution material or knowledge of this petition's result. Outcome-material retrieval is false on the available evidence, influence is `not_applicable`, and leakage suspicion is false.
