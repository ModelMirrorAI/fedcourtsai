# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage evaluation of prediction run `20261004T201824Z`. The supplied `outcome.json` records denial on October 5, 2026, with `actual_granted = 0`. The prediction named `denied` and assigned grant probability 0.006: exact-label correctness is 1 and Brier loss is `(0.006 - 0)^2 = 0.000036`.

The prediction freezes Term 2026, band `baseline`, and version `sal-v4`. The committed `metrics/statpack.md` heading matches that version. I use the bracketed reached population, not the terminal population, with `base_rate_basis = risk_set`. The displayed prior-Term rows give rate/denominator pairs: 2025 3.9%/1140; 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643. Pooling produces `637.385 / 12720 = 0.05010888364779874`, approximately 5.0109%. The numerator is reconstructed from rounded published percentages, not an exact grant count. The caption renders all 10 of the pack's 10 Terms; excluding 2026 leaves nine prior Terms and no rendered-window divergence.

Skill against that baseline for this denial is `1 - 0.000036 / 0.05010888364779874^2 = 0.9856625127087469`. This is a single-case comparison, not evidence of aggregate calibration. The baseline describes the committed statpack available in this checkout; I did not query the corpus or establish its live freshness.

## Reasoning quality: 0.90

The rationale gives a strong, record-specific explanation for moving substantially below the reached-band prior. It identifies the undeveloped conflict, sparse operative bias allegations, preservation dispute, finality concerns, and state-law objections without treating them as independent probabilities to multiply. Its treatment of adversarial evidence is particularly sound: the petition asserts preservation, the opposition disputes it, and the underlying documents needed to resolve that dispute independently are not supplied as readable appendices.

The analysis also recognizes that a reasoned state-law order need not answer the narrower allegation of missing federal constitutional analysis. Its finality discussion preserves the exclusive-writ counterargument that the opposition itself calls nonfrivolous, rather than converting the opposition's position into an adjudicated jurisdictional bar. Earlier stay denials are separated from the cert target and receive only limited weight.

The principal limitation is quantitative: the reduction from approximately 5% to 0.6% remains a judgmental adjustment, not a fitted or independently calibrated estimate. The missing reply and appendices leave genuine uncertainty about the vehicle objections. The observed denial supports the outcome forecast but does not establish which asserted obstacle motivated the Court. The score grades the soundness and evidentiary discipline of `reasoning.md`, not the correctness of its separate forecast document or its structured claims.

## Leakage and scope

The retrieval log says `forward`. The October 4 prediction and logged activity precede the October 5 resolution. The queries concern provisioned materials, the statpack, general cert standards, and historical Caperton authority. The two web calls are unobserved; their missing result dates are not proof that they returned nothing, notwithstanding the candidate's report of empty visible responses. Their query content does not seek this case's outcome. The other 22 calls are marked captured, although their staged digest rows are not full result bodies.

No visible query or reasoning passage shows the petition's own cert disposition already known. The earlier application denials resolve a different event. The frozen null cutoff and as-stored snapshot do not convert legitimate forward information into replay leakage. I therefore record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

I read `predicted_reasoning.md` only for context. Votes are unscored on cert cells regardless of their availability. No semantic set is declared here. Mechanical claim scores and provenance stamps are left to the harness. I omit the optional stakes assessment because no independent stakes score was fixed before reading the candidate's prose.
