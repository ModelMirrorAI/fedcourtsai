# Evaluation of gemini-baseline

## Quantitative Summary

- **Stage:** Certiorari (`cert`), arrival moment (`evt-petition-arrival-disposition`).
- **Outcome:** Denied (`actual_disposition: "denied"`, `actual_granted: 0`) on November 9, 2026, after a single distribution (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.03` (`correct: 1`, `brier_score: 0.0009`).
- **Baseline:** Evaluated against the prediction-time statpack build (`ab6fb84c09a6`, digest `sha256:f8abdb31530370551ced5a16ef3db2ecf512b450e040799d9ec5d03b7b9f48c4`, carrying `sal-v3`, rather than the committed pack). The scored baseline and skill score are computed by the harness as the stamped segment base rate.

## Reasoning Quality (`reasoning_quality`: 0.58)

`gemini-baseline` reached a well-calibrated headline probability (`0.03`) and correctly identified the core structural reasons for denial from the Question Presented and snapshot:
1. **Base-rate use:** In the prediction-time statpack (`ab6fb84c09a6`), the OT2025 `baseline` bracketed `reached` rate was indeed `5.4%` (`n=1176`) and `~6–7%` across prior Terms.
2. **Surface-level document reading & sub-claim error:** As shown in `retrieval_log.json`, `gemini-baseline` read `questions-presented.txt` and `documents.json` but never opened `petition.txt`. Consequently, its rationale missed the concrete procedural vehicle flaws disclosed in the petition's appendix (that the Guam Supreme Court dismissed the appeal only after the AG failed to appoint conflict-free substitute counsel, without reaching the merits of the trial court's conflict findings) and the flawed theory that the Government of Guam itself holds Fourteenth Amendment rights. Moreover, `gemini-baseline` offered no justification in `reasoning.md` for its secondary claims and miscalibrated `relist-increment` at `0.08` — treating it as the probability of a second conference (relist) rather than an increment above the frozen `distribution_count: 0` (which resolves true on the initial distribution to conference).

## Predicted Reasoning (`predicted_reasoning_quality`: 0.85)

In `predicted_reasoning.md`, `gemini-baseline` concisely and accurately forecast the petition's trajectory:
- It predicted that the petition would be denied without relists beyond the initial conference, that a CVSG was highly unlikely, and that there would be no dissent from denial or separate writing. All three predictions matched the realized record (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`, `actual_disposition: "denied"`).
- The prose is slightly more generic than `codex-baseline` and `claude-baseline` because `gemini-baseline` did not inspect `petition.txt`, leaving it to speculate generally that the decision below "likely rests on non-federal grounds."

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-08-16T12:41:36Z`; resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`. Although `result_capture_coverage` is `0.0` (`unobserved`), the prediction ran forward nearly three months before the petition was distributed or decided, and the logged queries were limited to local file reads, a failed `fedcourts query` invocation, and rate-limited CourtListener searches.
