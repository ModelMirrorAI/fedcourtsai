# Evaluation: claude-baseline

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

P(grant) = 0.015, so Brier = (0.015 - 0)^2 = **0.000225**. Skill against the common baseline is **0.9141777072871345**, calculated as 1 - 0.000225 / baseline^2. This single realized score does not establish calibration or aggregate performance.

## Reasoning quality: 0.88

The analysis selects the proper prior-Term risk-set anchor and moves from a general grant rate to specific vehicle considerations. Its strongest contribution is the reported lower-court research distinguishing the petition's asserted split from the panel's preservation and evidentiary grounds. The captured log confirms retrieval of the identified lower-court opinion and relevant chunks, although it supplies hashes rather than the full returned text for independent quotation checking. The provisioned petition itself corroborates the important distinction between the disputed core-customer theory and the panel's reliance on actual switching and purchases outside the proposed channel. Treating pleading-stage aftermarket reasoning and a fractured comparator as imperfect support for a square conflict is a discriminating rationale, not merely a low-base-rate guess.

It also separates a response waiver from a possible later response request, explains uncertainty about the response-request path, and acknowledges that terminal procedural buckets are not prospective hazards. The main weaknesses are the subjective 5% response-request and 15–20% conditional-grant estimates, whose product is nearer 0.75–1% than the final 1.5% absent an explicit numerical bridge, and weak proxies such as firm geography, petition length, or amicus institutional identity. References to perceived Court appetite and a hypothetical pool memorandum go beyond directly demonstrated evidence. Those reservations keep the score below the top of the scale; they do not undo the materially stronger conflict and vehicle analysis. The Court's bare denial does not verify that forfeiture or any other proposed reason actually drove its action.

## Leakage

The log is forward with result-capture coverage 1.0. The target-case CourtListener search returned a lower-court opinion dated January 13, 2026; the September 18 reads of that opinion and docket metadata preceded the October 5 cert denial. The metadata lookup is not forbidden post-cutoff retrieval in a genuinely open forward cell. Its cited date does not indicate the denial had occurred, and the reasoning describes the case as still pending. The general corpus query returned unrelated prior cases according to the retrieval note; nothing in its query or the reasoning points to this petition's outcome. There is no evidence of a mis-provisioned already-decided forward case. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
