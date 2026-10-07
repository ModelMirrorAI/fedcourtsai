# Evaluation: codex-baseline

## Outcome and numerical scores

This cert-stage event resolved in denial on October 5, 2026; `actual_granted = 0`. codex-baseline's September 17 prediction named `denied` and assigned any-grant probability 0.025. Thus `correct = 1` and Brier = `(0.025 - 0)^2 = 0.000625`.

The prediction freezes Term 2025 and the `baseline` band under `sal-v4`, matching the committed statpack's band-table heading. Using its bracketed reached rates for all displayed prior Terms gives: 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643 (rate/weighted resolved n). The executed weighted calculation is 0.05120250431778929 over n = 11,580, recorded as `risk_set`, not a terminal-band rate. The table displays 10 of 10 Terms, so there is no rendered-window discrepancy; Terms 2025 and 2026 are excluded. The numerical precision is computational, not evidence that the displayed rounded rates are exact.

Skill = `1 - 0.000625 / 0.05120250431778929^2 = 0.7616047424642627`. This event beats that baseline, which is not a general performance claim. The baseline is the committed statpack read October 7; no fresh corpus state was queried.

## Reasoning quality: 0.90

This grade concerns only `reasoning.md`. The analysis carefully distinguishes the frozen information set from later retrieval, correctly pools the prior-Term reached rates, and does not mistake two notices for one conference for an additional relist. It acknowledges the response request as positive evidence while addressing why a lower probability can still be warranted. It connects the petition's unpublished, Curtis-controlled affirmance to the reported denial of the lead petition, identifies potential preservation, immunity, and private-actor problems, and considers the reply's answers rather than treating the oppositions as uncontested fact.

The supplied petition excerpts corroborate the unpublished and Curtis-controlled posture. The staged log corroborates the fixed-URL retrieval routes for the two oppositions and reply. Particularly helpful is the rationale's explicit separation of respondents' assertions from independently established holdings, its disclosure that the Curtis denial was reported in the briefs rather than independently verified, and its recognition that the final adjustment is judgmental. These are reasons for the quality grade independent of the correct prediction or low Brier score.

The remaining weakness is the calibration bridge: neither the weight of the response request nor the downward vehicle adjustments is estimated, and the move from approximately 5.1% to 2.5% remains discretionary. The analysis relies on selected brief excerpts and does not independently establish every preservation or immunity proposition. The related denial is informative about review selection but not an adjudication of the present questions. The actual denial supplies no explanatory merits opinion that would resolve these analytical uncertainties. The limitations are openly acknowledged, which improves the rationale's reliability without making it complete.

## Leakage assessment

The harness records forward mode and September 17 tool activity, before the October 5 resolution. The log shows the August 24 State and Shriners opposition URLs and the September 14 reply URL. These are pre-decision materials, not the present petition's disposition. The reported June 1 Curtis denial concerns a separate case and is legitimate forward context even though it influences the forecast.

Capture coverage is 25/27, approximately 0.9259. The two unobserved web rows name the State BIO URL; the candidate describes them as empty opens, but their uncaptured results cannot independently substantiate emptiness. A subsequent captured command targets that same pre-decision document. The neutral `other` call class is not suspicious by itself; its query slices reveal the operational and retrieval commands. The logged instruction-file search explicitly excludes topic-label contents and is not evidence of reading them. No observed query or rationale shows this petition's future outcome being sought or known. Retrieved outcome material is false, influence `not_applicable`, and leakage suspected false.

## Scope

The forecast document was read solely for context. Neither its content nor the quantitative claims affects reasoning quality; mechanical scoring remains the harness's responsibility. There is no cert-stage vote accuracy or semantic grading. No independent big-case assessment or harness-owned provenance and telemetry is written.
