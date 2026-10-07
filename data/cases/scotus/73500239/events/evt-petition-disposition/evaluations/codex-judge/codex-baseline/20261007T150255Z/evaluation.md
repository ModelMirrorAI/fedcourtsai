# Evaluation: codex-baseline

## Outcome and numerical scores

The cert-stage outcome is `denied` on October 5, 2026, with `actual_granted = 0`, consistent with the provisioned October 5 snapshot. The candidate predicted denial with P(any grant) = 0.03. Exact-label correctness is 1; Brier is `(0.03 - 0)^2 = 0.0009`. The outcome establishes the disposition, not the Court's reasons for it.

The candidate froze `baseline` under `sal-v4` and docket Term 2025. The committed statpack's matching salience table supports a `risk_set` baseline using the bracketed reached rates, not terminal-band rates. All displayed strictly-prior rows are pooled: 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643. Weighted denominator is 11,580 and pooled rate is 0.05120250431778929. This is a denial-reweighted live/historical-slice estimate based on rounded displayed percentages. The table shows 10 of 10 Terms, so no table-window divergence requires a flag; 2025 and 2026 are excluded. Skill is `1 - 0.0009 / 0.05120250431778929^2 = 0.6567108291485383`.

These are committed-statpack figures, not a fresh remote corpus measurement. The candidate's own approximately 5.12% anchor agrees with the independently recomputed pool.

## Reasoning quality: 0.92

The rationale makes its information limits unusually clear. It distinguishes a future scheduled conference from an actual relist, a dated snapshot filename from the age of the proceedings within it, a petitioner's account from an independently examined appellate opinion, and general doctrinal importance from an outcome-determinative vehicle. Those distinctions materially support the forecast rather than merely adding detail.

Its central vehicle analysis is supported by the provisioned petition's printed pages 8–9: the petition describes an affirmance for lack of retaliatory causation and says the appellate court did not explicitly address the alternative Garcetti holding. Its analysis of the split likewise tracks the petition's printed page 12 concession that the disagreement is not precisely the proposed threshold rule. The rationale explains why expanding speech protection would not necessarily eliminate the described ground of judgment. It recognizes the upward academic-freedom consideration without equating a reserved question with endorsement of the petitioner's proposed solution.

The baseline choice and strictly-prior pooling are appropriate. The downward adjustment is coherent, although its exact size remains subjective rather than estimated from matched waived-response petitions. The appendix and lower-court opinions were not independently reviewed, and the rationale acknowledges this. Those remaining evidentiary and calibration limits keep the grade below a fully substantiated assessment.

This grade concerns the analysis in `reasoning.md` only. Neither the separate forecast nor its structured claims is graded here; claim-related probability discussions do not add to this score. The successful denial prediction does not prove the Court adopted the candidate's proposed vehicle explanation.

## Leakage and scoring limits

The log records a forward cell with September 17, 2026 calls, before the October 5 denial. Queries concern provisioned documents, the committed statpack, general Supreme Court rules, and the pre-existing Garcetti authority. There is no case-outcome search or assertion that this petition had already been denied. The supplied decided-docket snapshot is used only to evaluate the eventual result, not to infer what the predictor originally received.

Capture coverage is 23/26. The three unobserved calls are a generic rules search and two opens of the rules-guidance page. The candidate's claim that they returned no usable content cannot be verified from uncaptured results; the queries themselves nevertheless do not target this case or its disposition. The older-authority query and the prose provide no evidence of outcome material. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

No vote accuracy or semantic grades are appropriate on this cert cell. Mechanical claim scoring and harness-owned stamps are omitted. No independent big-case assessment is supplied.
