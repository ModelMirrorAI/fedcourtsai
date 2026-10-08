# Evaluation: claude-baseline

## Outcome and numerical scores

This is a cert-stage petition disposition. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The prediction names `denied`, so **correct = 1**. Its grant probability was 0.012, giving **Brier = (0.012 - 0)^2 = 0.000144**. The outcome establishes the disposition, not the Court's unstated reasons for declining review.

The prediction itself freezes `baseline`, `sal-v4`, and Term 2025. The committed statpack's sal-v4 table matches that version. I use its bracketed baseline **reached** rates, not terminal rates or the evaluator's decided-docket band. Every displayed strictly prior Term contributes:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2017 | 4.7% | 1643 |
| 2018 | 4.6% | 1524 |
| 2019 | 4.6% | 1399 |
| 2020 | 4.5% | 1739 |
| 2021 | 5.6% | 1500 |
| 2022 | 5.8% | 1192 |
| 2023 | 5.9% | 1312 |
| 2024 | 5.7% | 1271 |

The weighted sum of the displayed rates is 592.925 over 11,580, yielding **segment_base_rate = 0.05120250431778929**, with **base_rate_basis = risk_set**. The numerator is a rate-weighted quantity, not an integer grant count: these published percentages are rounded denial-reweighted estimates. Skill is **1 - 0.000144 / 0.05120250431778929^2 = 0.9450737326637661**. This is a single-cell comparison, not evidence of calibration or general predictive performance. The caption renders 10 of 10 Terms; 2025 and 2026 are excluded, and there is no hidden-window divergence. These are committed-statpack figures, not a refreshed corpus census.

## Reasoning quality: 0.80

The rationale makes a defensible distinction between a potentially interesting process-liability question and an unsuitable vehicle. Its two central obstacles are supported by the provisioned petition's Appendix A, pages 8a-12a: inability to perform the desired job's essential functions and the alternative conclusion that a reasonable reassignment was provided. It also recognizes that the petition's characterization of a circuit conflict does not by itself show that this panel decided that conflict. The matched prior-Term risk-set anchor, explicit downward adjustment, attention to the respondent's waiver, and acknowledgment of uncertainty make the analysis substantially more than a base-rate guess.

The strongest deductions are more reliable than some subsidiary ones. The categorical inference about why the government waived is not established by the waiver itself. Inferring cert prospects from counsel profile using a selected sample of grants has no comparable denied-petition denominator. Statements that the third question has support in no circuit and that counsel lacks evident Supreme Court practice go beyond what the documented checks establish. These considerations, and the judgmental size of the probability adjustment, keep the score below an exceptionally well-supported analysis. Correctly predicting denial does not verify those assertions.

Only `reasoning.md` is qualitatively scored. The forecast document was read for context; neither its realized accuracy nor the quantitative claims contributes to this quality score. Claim scoring remains with the harness. Vote accuracy and semantic grades are omitted because this is cert, not merits. No independent big-case assessment is supplied.

## Leakage assessment

The harness log identifies forward mode. Its 28 calls have 100% result-capture coverage and September 17 timestamps. The prediction reads a September 17 snapshot, before both the scheduled September 28 conference and the recorded October 5 denial. The log includes a general granted-prior corpus query and two docket searches. The candidate reports both searches returned no results; the staged log supplies capture markers and digests, not their full result bodies, so that report is not independently reconstructed here.

There is no affirmative evidence that this petition's disposition appeared in those calls or shaped the analysis. Searching its docket number in a genuinely unresolved forward cell is permitted. The evaluator's October 5 snapshot is not mistaken for the earlier prediction's input. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
