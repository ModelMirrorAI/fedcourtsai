# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage distribution cell for Watson v. Mason, docket 25-1279. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot also records "Petition DENIED." codex-baseline predicted denial with P(any grant) = 0.008 on September 16, 2026. Exact-label correctness is 1 and the Brier score is `(0.008 - 0)^2 = 0.000064`.

The prediction's own frozen context supplies Term 2025, band `baseline`, and version `sal-v4`, matching the committed statpack heading. I use the bracketed reached figures, not the terminal figures or the evaluator's decided-docket context. Prior-Term inputs, as (rate, weighted resolved n), are 2024 (5.7%, 1271), 2023 (5.9%, 1312), 2022 (5.8%, 1192), 2021 (5.6%, 1500), 2020 (4.5%, 1739), 2019 (4.6%, 1399), 2018 (4.6%, 1524), and 2017 (4.7%, 1643). Terms 2025 and 2026 are excluded. Pooling yields 592.925 approximate weighted grants / 11580 = 0.05120250431778929. These are denial-reweighted estimates calculated from rounded displayed rates, not exact grant counts. The caption renders 10 of 10 Terms, so there is no omitted-window discrepancy to flag. This describes the committed pack supplied to the cell, not a freshly queried corpus.

The basis is `risk_set`; skill is `1 - 0.000064 / 0.05120250431778929^2 = 0.9755883256283405`. This is one resolved observation, not evidence of aggregate calibration.

## Reasoning quality: 0.92

The rationale carefully distinguishes the unpublished certificate-of-appealability vehicle from plenary review of the underlying conviction. It identifies the petition's failure to supply concrete contrary jurisdictions, distinguishes asserted state-law inconsistency from the federal issue requiring review, and treats the petitioner's account of the verdict and instructions as allegations rather than independently established findings. It correctly separates an initial summer distribution from a relist and does not treat a response waiver as a merits concession. Its frozen-band anchor and weighted arithmetic are reproducible from the supplied table.

The account also acknowledges the missing appendix and COA reasoning and preserves a nonzero chance of intervention. The main limitation is that the reduction from roughly 5.12% to 0.8% remains a qualitative judgment, without matched historical cases or an empirical estimate of those adjustments. The observed denial supports the disposition call but does not establish the Court's reasons or adjudicate the constitutional allegations. The score rewards analytic discipline rather than mere outcome agreement.

## Leakage and scoring boundaries

The harness log identifies a forward prediction. All 35 calls occurred on September 16, before the October 5 resolution. Twenty-six results are captured and nine browser results unobserved (coverage 0.7428571428571429). Those unobserved calls target general authorities; their missing dates or digests do not prove that nothing was returned. The logged query set and prose show no retrieval or knowledge of this petition's eventual denial. Thus outcome material is false, influence is `not_applicable`, and leakage is not suspected. The decided snapshot available to this evaluator is not attributed retrospectively to the predictor.

I read the forecast for context only. Neither it nor the quantitative claims, including discussion of those claims inside the rationale, receives a separate qualitative outcome grade. Claim scores remain the harness's. Cert votes are not scored; no merits judgment or semantic grade applies. No independent big-case score is supplied.
