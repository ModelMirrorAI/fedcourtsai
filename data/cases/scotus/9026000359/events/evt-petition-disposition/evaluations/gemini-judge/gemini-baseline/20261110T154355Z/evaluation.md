# Evaluation of `gemini-baseline`

## Overview and Quantitative Summary

- **Stage:** `cert` (`evt-petition-disposition`, distribution moment).
- **Predicted vs. Actual Disposition:** Predicted `denied` (`probability = 0.005`); actual outcome `denied` (`actual_granted = 0`) on November 9, 2026 after a single distribution (`distribution_count = 1`, no CVSG, no noted dissent).
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = 0.000025`.
- **Base Rate & Skill:** Left null for the harness to stamp (`stamp-cell` pools the stamped segment base rate from the statpack over prior Terms under the prediction's frozen `context.band = "baseline"` and `salience_version = "sal-v4"`). Graded against the statpack build in force at prediction time (`886549a3ac32`, `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, reconstructed via `fedcourts statpack-at`), `gemini-baseline` cited `~0.9%` as the prior-Term salience band rate for `baseline`—which is the 2025 single-Term *terminal* rate (`0.9% (n=989)`) rather than the pooled multi-Term bracketed *reached* (risk-set) rate (`~5.0%`) that the `sal-v4` table specifies for predictions carrying a frozen band.

## Reasoning Quality (`0.58`)

While `gemini-baseline` arrived at a well-calibrated final probability (`0.005`) and correctly identified the core reasons why the petition would be denied (fact-bound local medical-marijuana permitting dispute, broad error-correction questions presented with no circuit split, and respondent's waiver of a response), two clear defects in `reasoning.md` lower its score:
1. **Factual Misreading of Publication Status Below:** `gemini-baseline` twice stated that the Sixth Circuit decision was "unpublished." In fact, the petition (`petition.txt` p. 1: "The decision of the United States Court of Appeals for the Sixth Circuit ... is reported") and the appendix (`appendix.txt` p. A1: `RECOMMENDED FOR PUBLICATION Pursuant to Sixth Circuit I.O.P. 32.1(b)`, File Name `26a0176p.06`) both explicitly state that the Sixth Circuit opinion was published. (The district court opinion was unreported, and `gemini-baseline` appears to have misread its own grep check on `NOT RECOMMENDED FOR PUBLICATION` coming up empty.)
2. **Base-Rate Anchor Error:** As noted above, `gemini-baseline` anchored on `~0.9%` (the single-Term 2025 terminal `baseline` rate in the statpack build `886549a3ac32`) rather than pooling the bracketed `reached` risk-set rate across prior Terms (`~5.0%`). Furthermore, its analysis of the five questions presented did not engage with the independent *Monell* municipal-liability and qualified-immunity grounds in the Sixth Circuit opinion.

## Predicted Reasoning (`0.80`)

In `predicted_reasoning.md`, `gemini-baseline`'s central procedural and outcome forecasts held up cleanly, though the document repeated the erroneous premise that the Sixth Circuit opinion was unpublished and was slightly more concise/generic than its peers:
- **Central Claims:** (1) Outright denial at the first conference (November 6, 2026) with no further relists (`borne-out` — denied November 9, 2026 at `distribution_count = 1`); (2) no CVSG called for due to the absence of a federal interest (`borne-out` — `cvsg_date = null`); and (3) a routine denial with no separate writings or dissents (`borne-out` — `noted_dissent_from_denial = false`).
- **Conditional Content:** Its conditional observation that a grant would focus on the procedural due process or takings questions regarding discretionary municipal licensing and would not take a summary GVR route was reasonable and untiggered by the denial.

## Leakage Assessment

- **Mode:** `forward` (prediction placed `2026-10-15T14:26:02Z`, prior to the November 6, 2026 conference and November 9, 2026 resolution).
- **Findings:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. In `retrieval_log.json`, all calls have `result_capture = "unobserved"` (`result_capture_coverage = 0.0`, the engine's standing telemetry shape), so each call is graded on its query per the prompt's rule. Every logged call is a local shell or file tool reading `AGENTS.md`, `.github/prompts/predict.md`, `metrics/statpack.md`, schemas, or the provisioned files under `data/cases/scotus/9026000359/`. No external search or post-cutoff query occurred.
