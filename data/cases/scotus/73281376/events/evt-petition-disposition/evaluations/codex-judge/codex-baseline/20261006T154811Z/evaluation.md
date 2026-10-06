# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition evaluation. The staged prediction is run `20260917T214606Z`, dated September 17, 2026. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The denial label matches exactly: **correct = 1**. At P(any grant) = 0.12, **Brier = (0.12 - 0)^2 = 0.0144**.

The baseline uses this prediction's frozen `elevated` band, `sal-v4` version, and docket Term 2025, not the evaluator's terminal context. The committed `metrics/statpack.md` heading matches sal-v4. Pooling its bracketed reached figures for every displayed strictly prior Term gives:

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

The displayed-rate weighted sum is 484.386 over 2,810, yielding **segment_base_rate = 0.172379359430605**, basis `risk_set`. The table renders 10 of 10 Terms; Terms 2025 and 2026 are excluded. These are rounded, denial-reweighted historical estimates, not exact grant counts or a fresh corpus measurement. No live corpus was consulted. The slight difference from the candidate's 484/2,810 anchor reflects its stated use of unrounded JSON fields rather than this evaluation's required rendered table. **Brier skill = 1 - 0.0144 / baseline^2 = 0.5153904514440745**. This describes one outcome, not population calibration.

## Reasoning quality: 0.92

The analysis distinguishes a contested delegation-of-policymaking theory from automatic municipal liability. The provisioned petition appendix, pages 23a–26a, supports that distinction: the majority discusses the counties' contracts, policy/custom, moving-force causation, and further proceedings rather than imposing final liability merely because a contractor was hired. The candidate identifies concrete weaknesses in the asserted circuit conflict, particularly the Fifth Circuit issue that the BIO discusses at pages 12–13, while acknowledging which authorities it did not independently inspect.

Its treatment of advocacy is especially sound. It labels the preservation objection as the BIO's argument, does not pretend to have read unavailable lower-court briefs or the relevant truncated dissent passage, and separates that uncertainty from the remand posture visible in the appendix. It also recognizes that the response request preceded the first scheduled conference: two distributions do not establish two substantive conferences. The downward adjustment from the frozen band anchor is therefore supported by case-specific reasoning rather than by simply assuming denial is common.

The residual limitation is quantitative: the precise adjustment to 12% is judgmental rather than tied to measured conditional effects, and material reply/supporting arguments remain unavailable. The correct denial does not establish that the Court adopted any of these reasons; the outcome supplies no explanatory opinion. The score evaluates `reasoning.md` alone. The forecast document and structured claims were read for context but receive no additional qualitative or numerical score here.

## Leakage and scope

The harness records `forward`. The prediction and all logged activity occurred on September 17, before the October 5 resolution. The log has 33 calls, with captured-result coverage 31/33. The two unobserved web calls concern general precedent, not the petition's disposition; their missing results are not evidence of empty responses. The other external research concerns a 2023 authority. Neither the query record nor the reasoning reveals this petition's outcome. Accordingly, retrieved outcome material is false, influence is `not_applicable`, and leakage suspected is false.

Cert votes are not scored. No semantic grades are declared for this stage, and claim scores and provenance stamps remain the harness's. No independent big-case assessment is entered because a stakes judgment was not fixed before the candidates' own assessments were encountered.
