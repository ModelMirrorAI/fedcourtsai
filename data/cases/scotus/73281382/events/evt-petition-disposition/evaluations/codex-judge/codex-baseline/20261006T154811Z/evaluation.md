# Evaluation: codex-baseline

## Outcome and numerical scores

The event is cert-stage. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`, no judgment, and no reported votes. The provisioned October 5 snapshot confirms the petition-denial entry; the separate grant of leave to file an amicus brief does not grant the petition. No live docket or corpus refresh was consulted.

codex-baseline predicted `denied` with P(any grant) = 0.12. Thus **correct = 1** and **Brier = (0.12 - 0)^2 = 0.0144**.

The baseline is keyed to the prediction's frozen `elevated` band, `sal-v4` version, and docket Term 2025, not the evaluator's terminal context. The statpack heading matches that version. Using the bracketed reached rates and weighted resolved denominators for every displayed strictly-prior Term gives:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

The pool is **484.386 / 2,810 = 0.17237935943060498**. It is approximate because the published rates are rounded, and the reconstructed numerator is not an exact integer grant count. The pack describes denial-reweighted paid-segment estimates and renders 10 of 10 Terms; 2025 and 2026 are excluded. With `base_rate_basis = risk_set`, baseline Brier is 0.029714643557705703 and **Brier skill = 0.5153904514440745**. No unrendered prior Terms are imputed. These are calculations from the committed table, not current-corpus or aggregate-performance claims.

## Reasoning quality: 0.92

The rationale provides a well-supported case-specific adjustment from a reproducible prior-Term anchor. It distinguishes two distributions from two completed conferences and avoids stacking a mechanical relist premium on the band baseline. It fairly presents both the BIO's purpose-theory preservation objection and the petition's assertion that the underlying Fourth Amendment issue was preserved. The relevant competing positions appear in BIO pages 11–12 and petition pages 25–26. It treats the missing reply and incomplete lower-court materials as limits rather than resolving that dispute by assertion.

It also separates a claimed doctrinal division from opposed holdings, distinguishes ordinary investigative motivation from objectively unlicensed conduct, and explains why a broad question might conceal a fact-bound error-correction request. The response request, dissent below, and amici are treated as reasons for attention rather than proof of four votes. The discussion of alleged exigency appropriately avoids assuming that later circumstances necessarily cure an unlawful initial approach. These strengths concern the soundness of the supplied analysis, not whether a correct denial forecast can retrospectively prove any legal premise.

The remaining limitation is quantification: the move from about 17.24% to 12% is an acknowledged judgmental adjustment, not an empirically estimated likelihood ratio, and the cited authorities were not independently verified. The write-up clearly discloses those boundaries. The outcome contains no explanation of the denial, so neither forfeiture nor the absence of a conflict is established as the Court's actual reason.

Only `reasoning.md` is qualitatively scored. The separate forecast was read for context; its procedural accuracy, quantitative claims, and conditional writing predictions are not folded into this rating.

## Leakage and scoring scope

The harness log says `forward`; prediction and activity dates are September 16, before the October 5 resolution. Of 27 calls, 24 have captured results and three web calls have unobserved results, giving capture coverage 0.8888888888888888. Those web queries/URLs concern general Jardines and Bovat authorities, not this petition's disposition. The candidate reports no usable web content, but unobserved telemetry cannot independently establish failed or empty retrieval. The general-authority CourtListener lookup is also described in the candidate's retrieval note. Neither the queries nor the rationale indicates outcome exposure.

The log's directory-search command expressly excludes the labeling-artifact path; naming an excluded path is not evidence that its contents were read. No candidate-specific post-resolution material appears. I assess `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, with the stated capture limitations. The evaluator's later snapshot is not evidence of the prediction's own input boundary.

Cert votes and semantic propositions are not scored. Harness-owned quantitative claims and provenance remain absent. No independent big-case assessment is supplied.
