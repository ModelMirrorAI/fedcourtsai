# Evaluation: gemini-baseline

## Result and numerical score

This is a cert-stage evaluation. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The September 16 prediction names `denied`, so exact-label correctness is **1**. Its grant probability is 0.05, giving **Brier = (0.05 - 0)^2 = 0.0025**. Denial confirms the label, not the substantive correctness of the lower court or any particular explanation for the Court's decision.

The scored prediction freezes `context.band = baseline`, `salience_version = sal-v4`, and Term 2025. The committed statpack's matching sal-v4 table supplies the bracketed reached rates; the evaluator's decided-docket context is not used to assign the band. Pooling all displayed Terms strictly before 2025 gives:

| Term | Reached rate | Weighted resolved n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The weighted numerator is 592.925 and denominator 11,580: **segment base rate = 0.05120250431778929**, on the **risk_set** basis. This is an approximate denial-reweighted private-petitioner risk-set estimate reconstructed from rounded published percentages, not an exact raw-count grant rate. The caption renders 10 of 10 pack Terms; 2025 and 2026 are excluded, leaving eight eligible rows, with no additional pack-window truncation. **Brier skill = 1 - 0.0025 / 0.05120250431778929^2 = 0.04641896985705086.** This is one observation's comparison, not evidence of general calibration or aggregate skill.

Source vintage is the committed statpack supplied to this evaluation, not a refreshed corpus measurement. The prediction froze a September 16 snapshot; the evaluator's snapshot is named October 5. No corpus query or corpus-wide freshness measurement was performed, and no present-day corpus-state claim is made.

## Reasoning quality: 0.65

The rationale reasonably identifies a private, fact-intensive dispute, weakly developed conflict allegations, and only an initial distribution. Those observations support a denial forecast independently of the realized result. It keeps a nonzero grant chance and identifies uncertainty about a genuine conflict rather than claiming certainty.

The analysis is nevertheless thin. Its approximate 5–6% anchor lacks an explicit pooling calculation or reached-versus-terminal explanation. Its 1.2% zero-relist comparison uses a grant-only figure rather than clearly accounting for the GVR component of the any-grant target; a terminal zero-relist group is also not the same population as petitions currently awaiting their first conference. The proposed upward adjustment from that figure because the First Amendment issue could attract attention is weakly grounded. It does not examine the private-action problem, state-procedure posture, or possible finality issues developed in the supplied petition, nor clearly distinguish missing opposition material from established absence. These omissions limit the explanation for retaining a probability near the broad risk-set anchor.

The score concerns only the analytical soundness of `reasoning.md`. It is not a grade of the separate forecast, the mechanical claims, the stakes score, or success on this single outcome.

## Leakage assessment

The harness log records forward mode and 31 calls on September 16, before the October 5 resolution. The queries show provisioned-file reads, a statpack read, and two topical corpus-query attempts restricted to decisions before September 16. The reasoning does not presuppose the disposition. Nothing establishes that an already-decided case was provisioned forward, so `influenced_prediction = not_applicable`, `retrieved_outcome_material = false`, and `leakage_suspected = false`.

Capture coverage is 0.0: every result is unobserved. That is a telemetry limitation, not evidence that the calls failed or returned nothing. The candidate's statement that there was no retrieval beyond provisioned inputs does not disclose the two query attempts. A cell-level data-quality flag records that discrepancy; successful retrieval and result contents cannot be established from this log. It does not establish outcome leakage or change the computed score.

## Unscored fields

The pointed-to `predicted_reasoning.md` was read for context only. Mechanical claim scores remain for the harness. Cert votes are not scored; no semantic set is declared on this stage. No vote-accuracy, semantic-grades, or harness-owned stamps are written.
