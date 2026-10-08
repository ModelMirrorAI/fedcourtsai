# Evaluation: gemini-baseline

## Outcome and scoring scope

This is a cert-stage distribution cell. The provisioned outcome records denial on October 5, 2026, with `actual_granted = 0`, one distribution, no CVSG, and no noted dissent from denial. The candidate predicted `denied`, so `correct = 1`. The unexplained denial does not establish that the Court adopted any candidate's proposed reasons.

Only `reasoning.md` receives the qualitative grade. I read the pointed-to `predicted_reasoning.md` for context but do not grade that forecast or the quantitative claims. Claim scores belong to the harness. Vote accuracy and semantic grades are omitted on this cert cell. No independent big-case assessment was formed before viewing the candidates' scores, so that optional field is omitted.

## Common baseline

The scored prediction freezes `context.band = baseline`, `context.salience_version = sal-v4`, and `context.term = 2025`. These, not the evaluator's terminal context, select the baseline. The committed `metrics/statpack.md` heading matches sal-v4. I pool its bracketed reached rates, weighted by their resolved denominators, over all displayed Terms strictly before 2025:

| Term | Reached rate | Weighted resolved n |
| --- | --- | --- |
| 2017 | 4.7% | 1,643 |
| 2018 | 4.6% | 1,524 |
| 2019 | 4.6% | 1,399 |
| 2020 | 4.5% | 1,739 |
| 2021 | 5.6% | 1,500 |
| 2022 | 5.8% | 1,192 |
| 2023 | 5.9% | 1,312 |
| 2024 | 5.7% | 1,271 |

The denominator is 11,580 and the resulting rate is 0.05120250431778929, with `base_rate_basis = risk_set`. This is an approximation from published rounded percentages, not an integer grant-count reconstruction. The caption renders 10 of 10 Terms, so there is no hidden-window divergence to flag. Terms 2025 and 2026 are excluded. The table describes denial-reweighted live/historical-slice estimates, not a census or an independently refreshed corpus. I made no live-corpus freshness claim or corpus query. codex-baseline's cited exact JSON-based rate differs slightly because it uses unrounded inputs; that is not a substantive disagreement with this required Markdown-table calculation.

## Quantitative result

P(grant) = 0.012, so Brier = (0.012 - 0)^2 = **0.000144**. Skill against the common baseline is **0.9450737326637661**, calculated as 1 - 0.000144 / baseline^2. This single realized score does not establish calibration or aggregate performance.

## Reasoning quality: 0.67

The rationale identifies relevant supplied-record features: the response waiver, limited visible institutional support, and the case-specific evidentiary character of the market-definition dispute. It allows a future response request rather than treating the waiver as an already-final disposition. The low grant probability is directionally coherent with that analysis and the observed outcome.

The analysis is nevertheless thin on the petition's central asserted conflict. It does not disentangle the competing readings of the cited precedents, the procedural posture differences, or the claimed preservation problem. The categorical assertion about a response being required is insufficiently qualified in the rationale; the waiver supports a procedural inference, not independent proof of the petition's merits. The inference from counsel or amicus institutional status is also weakly substantiated, especially without reviewing the amicus text. Its 5% response-request estimate and 1.2% final probability are subjective and not tied to a clearly justified conditional grant estimate. Finally, it anchors on OT2024 alone at 5.7% rather than the full displayed strictly-prior-Term pool. These limitations, not the unscored forecast document or claims, drive the moderate grade despite the excellent realized Brier score.

## Leakage

The harness log labels the prediction forward. Calls and prose are dated September 18, before the October 5 disposition. The query strings concern general waiver and antitrust subjects; they do not seek this petition's subsequent disposition. All 25 marked call results are unobserved, so I do not equate missing result dates with proof of empty returns. The self-report says the corpus queries failed for unsupported free-text syntax, but the result capture cannot independently verify that claim. Neither the log's queries nor the reasoning shows this case's denial already known. `retrieved_outcome_material = false` reflects no affirmative exposure evidence, with this capture limitation; `influenced_prediction = not_applicable` and `leakage_suspected = false` follow the ordinary forward rule.
