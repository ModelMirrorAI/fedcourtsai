# Evaluation: codex-baseline

## Outcome and scoring scope

This is a cert-stage petition-disposition cell. The provisioned `outcome.json` records `denied`, `actual_granted = 0`, resolved October 5, 2026. The October 5 snapshot also records "Petition DENIED." These are the scoring ground truth; a denial supplies no explanation endorsing either side's account of the underlying dispute.

The assessed prediction is the blinded candidate's run `20261004T201824Z`. Only `reasoning.md` contributes to reasoning quality. I read the pointed-to `predicted_reasoning.md` for context but did not grade it, the quantitative claims, or their accuracy. No semantic grades or vote accuracy are written on this cert cell. Harness-owned claim scores, provenance, and context are left untouched. No independent big-case score is supplied.

## Baseline

The prediction's own frozen context supplies Term 2026, band `baseline`, and `sal-v4`; the committed `metrics/statpack.md` heading matches. Accordingly `base_rate_basis = risk_set`, using the bracketed reached rates, not the terminal leading rates or the evaluator's decided-docket context.

All rendered strictly prior Terms are pooled with their weighted resolved denominators:

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
| 2025 | 3.9% | 1140 |

The rate is sum(rate * n) / sum(n) = 637.385 / 12720 = 0.05010888364779874. The numerator is an approximation reconstructed from displayed rounded percentages, not an integer observed grant count. These are denial-reweighted paid-segment estimates from the committed live/historical slice, not a fresh corpus measurement. No live corpus freshness or per-case last-pulled date was consulted or inferred. The caption renders 10 of 10 Terms; the empty 2026 row is excluded, leaving nine prior rows and no rendered-window omission to flag.

## Quantitative result

The candidate predicts `denied`, exactly matching the realized label: `correct = 1`.
Its P(any grant) is 0.015; thus Brier = (0.015 - 0)^2 = 0.000225.
Against the baseline above, Brier skill = 1 - 0.000225 / (0.05010888364779874 - 0)^2 = 0.910390704429668.
This is a single-cell descriptive comparison, not a cohort calibration or performance claim.

## Reasoning quality: 0.90

This is a careful, case-specific rationale. It distinguishes the petition's allegations from independently verified facts, acknowledges that the lower opinions and evidentiary record were not retrieved, and explains why fact-centered challenges and uncertain preservation weaken the case for review. It does not treat the response waiver as a concession, pro se status as a merits defect, or a passed conference date as an observed disposition or relist. The asserted dissent supplies a reason not to collapse the probability to zero. These distinctions make the downward adjustment from the proper prior intelligible without treating the subsequent denial as proof of the asserted legal defects.

The rationale reports an exact-data risk-set anchor of 638 / 12720 = 0.0501572327, obtained from the matching committed JSON; the captured query supports that method, although this evaluator pools only the rendered Markdown rates as required. The approximately 0.00004835 difference from my scoring baseline is consistent with displayed percentage rounding, not a wrong band, version, or Term window. I have not independently consulted the JSON or its history. The candidate also appropriately distinguishes the aggregate artifact's commit date from a verified current corpus refresh.

The main remaining limitation is calibration: the evidence supports a low probability, but the precise reduction to 1.5% is a judgment without a matched empirical cohort or sensitivity range. The lower-court dissent and forfeiture ground are still known only through a short petition, leaving uncertainty that further pre-resolution source inspection could have reduced. The analysis explicitly admits those limits. The correct denial does not remove them, and the score rewards the disciplined rationale rather than the result alone.

## Leakage assessment

The harness log says `forward`; 23 of 25 calls are captured, with coverage 0.92. The calls occur October 4, before the October 5 denial. The candidate reads its October 4 snapshot, the petition, and aggregate statistics, and its prose explicitly treats the event as unresolved.

The two web rows are `unobserved`: a generic search about Supreme Court Rule 10 and an open of a general Rule 10 page. I do not treat the candidate's statement that these attempts returned nothing usable as harness-verified failure or empty results. I grade the visible queries themselves; neither seeks this case, its docket, or its outcome. Null returned dates on those rows prove nothing about returned content, but there is no positive indication of outcome-revealing retrieval or reliance.

No logged case-specific post-resolution source or outcome-presupposing passage appears. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is a bounded assessment of the staged evidence, not a claim of complete returned-content visibility.
