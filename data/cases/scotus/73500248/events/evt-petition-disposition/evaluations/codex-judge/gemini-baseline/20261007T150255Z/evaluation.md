# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a **cert-stage** evaluation of Webb v. Trombley, No. 25-1346. The provisioned `outcome.json` records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied` with P(any grant) = 0.01. Accordingly, exact-label correctness is **1** and Brier loss is **(0.01 - 0)^2 = 0.0001**. The outcome establishes the disposition, not the Court's reasons for denying review.

The candidate's own frozen context supplies `baseline`, `sal-v4`, and Term **2025**. The evaluation-time context is not substituted for that context. The committed `metrics/statpack.md` heading matches `sal-v4`; its caption renders all ten pack Terms. Pooling its eight strictly prior rows, **2017–2024**, on the bracketed baseline **reached** rate gives the risk-set baseline:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2017 | 4.7% | 1,643 |
| 2018 | 4.6% | 1,524 |
| 2019 | 4.6% | 1,399 |
| 2020 | 4.5% | 1,739 |
| 2021 | 5.6% | 1,500 |
| 2022 | 5.8% | 1,192 |
| 2023 | 5.9% | 1,312 |
| 2024 | 5.7% | 1,271 |

The sum of displayed rates times denominators is **592.925**, over weighted n **11,580**, yielding **0.05120250431778929**. The numerator is a calculation from rounded displayed rates, not an observed integer count. These are denial-reweighted, paid-segment live/historical-slice estimates, not an unselected population rate. Terms 2025 and 2026 are excluded. No rendered-window truncation or salience-version mismatch applies. Skill is **1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282**. This is one resolved-event comparison, not a claim of aggregate forecasting performance.

## Reasoning quality: 0.65

The rationale identifies the relevant statutory question, the response waiver, the low-risk baseline band, and the absence of a direct circuit conflict as reasons for a low grant probability. The central consensus premise is supported by the provisioned petition's Appendix A, pages 4a–5a, footnote 3: the appellate panel describes agreement among the circuits and its obligation to follow existing circuit precedent. Those are relevant selection considerations, rather than an attempt to predict certiorari solely from which statutory reading seems better.

The analysis is nevertheless thin. It neither distinguishes the petition's asserted disagreements over appellate fees and other settings from the trial-fee question actually presented, nor weighs the preserved legal question and the petitioner's textual objection as countervailing considerations. Its description of the respondent's waiver as showing that the respondent regards the petition as weak is an inference about motive, not an established fact. The cited 4–6% anchor is directionally appropriate but is not pooled explicitly, and the reduction to 1% is not explained beyond two qualitative considerations. These limitations, rather than the terse format itself, drive the score. Correctly forecasting denial does not cure missing analysis.

Only `reasoning.md` is graded for reasoning quality. The forecast document was read for context, but neither its successful ancillary forecasts nor the structured quantitative claims receive a separate reader score or affect this grade.

## Leakage and scope

The harness log records **forward** mode. All 30 calls occurred on September 17, before the outcome's October 5 resolution. It includes statutory searches, an exact-question search, and a caption search for Webb and Trombley. Such case-specific retrieval is permitted for a genuinely open forward event; no query or prose passage shows the Supreme Court disposition already available or known.

Result-capture coverage is **0.0**: every result is unobserved. I do not treat null document dates or digests as evidence that searches returned nothing, and cannot independently reconstruct their contents from hashes or missing results. On the available timing, queries, and reasoning, there is no affirmative evidence of outcome retrieval. Thus `retrieved_outcome_material = false`, influence is `not_applicable`, and `leakage_suspected = false`.

Cert votes, semantic claims, and the forecast document are not scored. Mechanical claim scores and all harness-owned provenance fields are left to the harness. The shared baseline uses the committed pack only; no live corpus was queried or corpus-freshness claim made. The evaluator's provisioned snapshot is dated October 5, whereas the prediction freezes September 17; the later snapshot is not evidence of what the predictor saw.
