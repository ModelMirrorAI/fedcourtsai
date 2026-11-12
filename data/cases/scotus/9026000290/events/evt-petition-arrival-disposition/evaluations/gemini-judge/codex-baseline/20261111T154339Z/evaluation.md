# Evaluation of `codex-baseline`

## Overview and Outcome

- **Case:** *Mihal Emberton v. Superior Court of California, City and County of San Francisco, et al.*, No. 26-290 (`scotus/9026000290`)
- **Event:** `evt-petition-arrival-disposition` (`stage: cert`, `moment: arrival`)
- **Outcome:** Petition `denied` on November 9, 2026 (`actual_granted: 0`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: denied`, `probability: 0.004` (`correct: 1`, `brier_score: 0.000016`).

## Quantitative and Base-Rate Assessment

`codex-baseline` predicted `denied` with `P(grant) = 0.004`, earning `correct = 1` and a Brier score of `0.000016`. Per the cert-stage evaluation contract, `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null here for the harness (`stamp-cell`) to stamp from the stamped segment base rate.

To verify `codex-baseline`'s base-rate calculation against the statpack in force at prediction time (`20260927T182226Z`), I rebuilt that statpack via `fedcourts statpack-at` (commit `2420d5dd72e1`, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`). `codex-baseline` pooled the unrounded `sal-v4` `baseline` risk-set (`reached`) rates over strictly prior Terms OT2017–OT2025 from `statpack.json`, obtaining `638 / 12,720 = 5.0157%`, and explicitly avoided the terminal baseline rate and the terminal zero-relist bucket. This base-rate handling is exact and methodologically rigorous.

## Reasoning Quality (`0.96`)

`reasoning.md` is thorough, disciplined, and legally perceptive (`reasoning_quality = 0.96`):

- **Base-rate and moment discipline:** Properly distinguishes the arrival risk-set anchor (`baseline` `reached` rate under `sal-v4`) from terminal cuts, notes that zero distributions at arrival is the moment's definition rather than negative conference history, and refrains from inferring respondent concession from the pre-deadline absence of a BIO.
- **Doctrinal and vehicle analysis:** Accurately identifies why the petition's juxtaposition of *Ciraolo*/*Dow*/*Marshall* against *Boyd*/*Katz*/*Kyllo*/*Horton* (and Ninth Circuit curtilage case law) does not establish a genuine appellate conflict; pinpoints the severe vehicle and finality obstacles under 28 U.S.C. § 1257(a) arising from an unexplained California Court of Appeal writ denial following an order sustaining a demurrer to a seventh amended complaint with and without leave to amend; and notes that the substantive trial court order is not reproduced in the appendix.
- **Calibration:** Explains the downward move from the ~5.02% class floor to `0.004` clearly and calibrates the secondary claims coherently.

## Predicted reasoning (`0.92`)

`predicted_reasoning.md` is specific, well-structured, and completely borne out across its central claims (`predicted_reasoning_quality = 0.92`). It forecasts that the Court will deny certiorari via an unsigned order after a single initial conference distribution (explaining clearly that from a zero-distribution arrival baseline, the modal path is one distribution and zero further relists), estimates timing in November or December 2026 after the October 5 response deadline (the petition was distributed October 21 and denied November 9, 2026), and predicts no CVSG and no separate statement or dissent from denial. Its conditional discussion of how the Court would narrow the first question presented and proceed via plenary review rather than a summary GVR if cert were granted is well-reasoned and appropriately marked conditional.

## Leakage Assessment

- **Mode:** `forward` (prediction run `20260927T182226Z`, created `2026-09-27T19:12:09Z`; distributed `2026-10-21`; resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was unresolved when predicted. `retrieval_log.json` shows local shell/file reads of the prompt, schemas, provisioned case files, and statpack, plus five `unobserved` web-search calls for general legal authorities (Supreme Court Rule 10 and 28 U.S.C. § 1257) that did not query this case and which `codex-baseline` candidly disclosed in `retrieval.md`.
