# Evaluation of `gemini-baseline`

## Overview and Outcome

- **Case:** *Mihal Emberton v. Superior Court of California, City and County of San Francisco, et al.*, No. 26-290 (`scotus/9026000290`)
- **Event:** `evt-petition-arrival-disposition` (`stage: cert`, `moment: arrival`)
- **Outcome:** Petition `denied` on November 9, 2026 (`actual_granted: 0`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: denied`, `probability: 0.001` (`correct: 1`, `brier_score: 0.000001`).

## Quantitative and Base-Rate Assessment

`gemini-baseline` predicted `denied` with `P(grant) = 0.001`, earning `correct = 1` and a Brier score of `0.000001`. Per the cert-stage evaluation contract, `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null here for the harness (`stamp-cell`) to stamp from the stamped segment base rate.

To check `gemini-baseline`'s base-rate reference against the statpack in force at prediction time (`20260927T201651Z`), I rebuilt that statpack using `fedcourts statpack-at` (commit `2420d5dd72e1`, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`). Under `sal-v4` (frozen in the candidate's `context`), the pooled `baseline` risk-set (`reached`) rate across prior Terms OT2017–OT2025 is approximately 5.0%, matching `gemini-baseline`'s citation of roughly 5% (bracketed `reached` rate) before adjusting sharply downward for the pro se, localized nature of the dispute.

## Reasoning Quality (`0.85`)

`reasoning.md` is concise and well-grounded in the provisioned record (`reasoning_quality = 0.85`):

- **Strengths:** Correctly identifies the `baseline` caption class floor and the ~5% pooled bracketed `reached` base rate, then justifies a sharp downward adjustment to `0.001` based on the pro se posture, the underlying dispute over local San Francisco code-enforcement citations for a fence and trellis, the implausible Fourth Amendment theory that "plain view" visual observation from outside the property constitutes an unconstitutional search seizing "knowledge" or "data" (contrary to *California v. Ciraolo*), the pleading-stage dismissals below, the absence of any genuine split, and poor vehicle posture.
- **Limitations:** While accurate on every core point, `reasoning.md` is brief and does not unpack the specific state-court procedural posture (an unexplained California Court of Appeal extraordinary writ denial following a sustained demurrer to a seventh amended complaint, raising finality/reviewability problems under 28 U.S.C. § 1257) or explain the mechanics of the arrival-moment distribution claim in `reasoning.md`.

*(Note: Quantitative claim probabilities in `prediction.json` are scored in code by the harness and did not influence `reasoning_quality`.)*

## Predicted reasoning (`0.75`)

`predicted_reasoning.md` forecasts a clean denial without relists, without a CVSG, and without any separate writing or dissent from denial. All of its unconditional central claims were borne out by the November 9, 2026 order list following the single distribution for the November 6, 2026 conference. Its conditional observations (that a summary GVR is unlikely for lack of an intervening decision, and that if granted the Court would likely take the first question presented) were not tested by the denial. The document receives `0.75` rather than higher because it is relatively brief and generic on the conference timeline and procedural mechanics compared to a maximally specific trajectory forecast.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-09-27T20:16:51Z`; distributed `2026-10-21`; resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely open at prediction time, and `retrieval_log.json` shows only local file reads of the prompt, provisioned case documents, snapshot `2026-09-04.json`, and `metrics/statpack.md`.
