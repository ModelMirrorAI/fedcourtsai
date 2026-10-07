# Evaluation: codex-baseline

## Disposition and quantitative scores

The cert-stage outcome records `denied`, `actual_granted: 0`, resolved October 5, 2026. codex-baseline's September 18 prediction assigns P(any grant) = 0.015 and names `denied`. Thus `correct = 1` and Brier = `(0.015 - 0)^2 = 0.000225`.

The baseline uses the prediction's frozen `context.band: elevated`, `salience_version: sal-v4`, and Term 2026, not the evaluator's terminal context. The committed `metrics/statpack.md` heading matches sal-v4. Its caption renders all 10 of 10 available Terms; strictly prior eligible rows are 2017–2025, so no rendered-window divergence needs flagging. The bracketed reached percentages and weighted denominators are:

| Term | Reached rate | Weighted n |
| --- | --- | --- |
| 2025 | 13.5% | 275 |
| 2024 | 17.9% | 336 |
| 2023 | 17.5% | 354 |
| 2022 | 19.0% | 300 |
| 2021 | 20.5% | 342 |
| 2020 | 16.1% | 397 |
| 2019 | 13.8% | 334 |
| 2018 | 15.9% | 347 |
| 2017 | 17.5% | 400 |

The resolved-weighted rate is `sum(rate * n) / sum(n) = 521.511 / 3085 = 0.16904732576985413`; the numerator is a rate-weighted quantity reconstructed from rounded displayed percentages, not an observed grant count. `base_rate_basis = risk_set`. Brier skill is `1 - 0.000225 / baseline^2 = 0.9921265348709908`. This is a descriptive single-cell score, not evidence of general calibration or predictive superiority. The candidate's reported 521/3085 came from its own earlier JSON aggregate read; I use the evaluation contract's current rendered Markdown figures rather than copying that number. No live corpus query or freshness check was made, so these are committed-pack estimates, not a claim about current remote corpus state.

## Reasoning quality: 0.91

The rationale carefully distinguishes grant selection from the merits of the APA dispute. It explains why a broad administrative-record question may nevertheless arrive in a fact-dependent vehicle, treats the petition's factual and doctrinal descriptions as advocacy rather than established law, and explicitly acknowledges missing lower opinions and opposition. The staged log supports targeted historical-authority lookups behind its examination of the alleged split; I have not independently retrieved those opinions or treated the candidate's quotations as a judicial holding in this case.

Its strongest procedural point is the distinction between the earlier veteran-status motion and substantive consideration of certiorari. It retains the frozen elevated band for the baseline while explaining why the two-distribution signal may overstate actual cert attention. Its treatment of the waiver, absence of a response request in the supplied record, and null versus verified-zero amicus information is measured. It also avoids mechanically multiplying correlated aggregate cuts.

The substantial reduction from about 17% to 1.5% is nevertheless judgmental, not supported by an estimated conditional model. The split and vehicle assessment remains limited by the absence of independently examined lower-court opinions and the administrative record. Those limitations keep the score below 1. The ultimate denial does not establish that the Court adopted the rationale or rejected the asserted split; it only resolves the disposition forecast. The shared distribution-history concern is recorded in the cell's flags without changing the frozen baseline.

## Leakage and scope

The harness log says `forward`; all logged calls occurred September 18, before the October 5 disposition. The rationale expressly distinguishes the June 8 motion denial from a cert denial. Capture coverage is 34 of 37 calls. The three unobserved web requests concern general Court rules, not Jones or its disposition. I do not credit their null result fields as evidence that nothing was returned, even though the candidate says no usable content appeared. The captured query trail otherwise concerns provisioned inputs, aggregate context and historical authorities. Nothing affirmatively indicates that the cert outcome surfaced while the case was already decided. Accordingly, outcome-material retrieval is assessed false, influence is `not_applicable`, and leakage suspicion is false, subject to the stated capture limit.

Only `reasoning.md` receives the qualitative score. I read the pointed-to forecast for context but do not grade it or the quantitative claims. This cert cell has no semantic grading or scored votes. Claim scores, process/context stamps, prediction-run linkage and baseline-version stamping are left to the harness. No optional significance score is supplied.
