# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a cert-stage event. The authoritative outcome records denial on October 5, 2026, with binary grant outcome 0. codex-baseline's September 17 prediction selected `denied` and assigned 0.01 to any grant, including summary relief. Its exact-label correctness is **1** and its Brier score is **0.0001**, calculated as `(0.01 - 0)^2`. The outcome does not establish the Court's substantive rationale.

The candidate's frozen context supplies Term 2025, `baseline`, and `sal-v4`; the statpack's salience-band heading matches. I use the **reached** risk-set figures and record `base_rate_basis = risk_set`.

| Prior Term | Reached rate | Weighted resolved denominator |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Resolved-weighted pooling gives `592.925 / 11580 = 0.05120250431778929`. This is reconstructed from rounded percentages; 592.925 is not an observed count. The case's own Term 2025 and the later 2026 row do not enter. The caption reports 10 of 10 pack Terms rendered; every displayed strictly-prior row is included, with no rendered-window omission. Brier skill is `1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282`. This measures this one forecast against its baseline, not general performance or calibration.

The figures are from the committed denial-reweighted live/historical rollup. No remote-corpus freshness is established by this evaluation. The candidate's frozen snapshot date is September 16, 2026, and the evaluator's snapshot is dated October 5; these identify the respective inputs rather than a corpus-wide newest-pull date.

## Reasoning quality: 0.90

The rationale carefully separates the case's actual posture from generic cert statistics. It selects the frozen, version-matched, strictly-prior reached-band baseline and expressly declines to treat terminal zero-relist and no-CVSG buckets as forward hazards. It also correctly treats a July distribution for a September conference as a future scheduled consideration, not a completed relist or a hold.

The case-specific analysis is grounded and qualified. It recognizes that the petition mentions disagreement over manifest disregard but does not develop competing holdings on a question necessary to the judgment. It identifies the lower court's assumed federal-standard analysis as a vehicle concern without claiming to have established an independent state-ground bar. The petition's printed pages 6–7 and 12–13 support those distinctions. It separates the two arbitrations and distinguishes allegations concerning an arbitrator from the separate appellate-neutrality issue. It treats the lack of a BIO or underlying opinion as an evidentiary limitation rather than a concession. The discussion of the historical concurrence is presented as a caution against the petition's categorical reading, not as proof that one circuit's interpretation governs this case.

The remaining limitations concern the foundation for the exact probability. The adjustment to 1% is judgmental rather than estimated from a demonstrated comparison group, and the lower-court opinion, appendix, and respondent's substantive account were not independently available. I have not re-fetched the concurrence; the assessment rests on the staged rationale, provisioned petition, and logged authority lookup, not a new verification of that authority. These limits prevent treating the account as fully established, but the rationale states them substantially more carefully than it states its conclusions. The quality score rewards that analytical discipline, not the fact that denial happened.

Only the explanatory analysis in `reasoning.md` informs this grade. The predicted court-reasoning document, the auxiliary quantitative forecasts embedded in the rationale, and the structured claims remain unscored here.

## Leakage assessment

The log records `forward`, 29 calls, and capture coverage `28/29 = 0.9655172413793104`. The prediction was written before the October 5 resolution. Its local case reads concern the September 16 snapshot and provisioned petition. External lookups are directed to general certiorari standards and the historical Commonwealth Coatings authority, including the concurrence read. No visible query seeks this petition's later docket or disposition, and the rationale treats the conference as forthcoming.

The web-search row is `unobserved`. Its visible query concerns general certiorari standards; the retrieval note also reports a general query about the concurrence. The assertion that the search yielded no usable content is the candidate's report, not independently captured result evidence. I do not equate that unobserved result with a failed or empty result. On the visible query subjects, chronology, and reasoning there is no affirmative outcome exposure: `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`. Collapsed `other` tool labels and redaction markers are not themselves suspicious.

## Scope

No cert vote score is allowed, and this event declares no semantic set. No merits judgment, vote, semantic, or mechanical claim grade is supplied. The forecast document was read only as context. Harness-owned process, context, linkage, and salience-version stamps remain unwritten.
