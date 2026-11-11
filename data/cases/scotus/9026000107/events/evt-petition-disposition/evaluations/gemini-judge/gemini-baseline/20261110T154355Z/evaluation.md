# Evaluation of `gemini-baseline`

## Overview and quantitative summary

- **Event:** `scotus/9026000107` / `evt-petition-disposition` (cert stage, distribution moment)
- **Outcome:** `denied` (`actual_granted = 0`), resolved on November 9, 2026 after 2 distributions (`distribution_count = 2`), no CVSG, and no noted dissent from denial.
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.35` (`correct = 1`, `brier_score = 0.1225`).
- **Base-rate calibration:** Graded against the statpack build in force at the candidate's run time (`1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, reconstructed via `fedcourts statpack-at`), which differs from the currently committed statpack (now under `sal-v8`). In `reasoning.md`, `gemini-baseline` stated that the `baseline` salience band "carries a base rate of less than 1%." Even against the historical `sal-v4` statpack in force at prediction time, that misreads the table: the risk-set (`reached`) rate for a frozen `baseline` band was ~5.0% (the stamped segment base rate), and even the terminal `baseline` rate exceeded 1% in almost every prior Term (only OT2017 and OT2025 were below 1%, at 0.6% and 0.9%).

## Reasoning quality (`reasoning_quality = 0.42`)

`gemini-baseline`'s two-paragraph `reasoning.md` was superficial and omitted critical counterweights in the provisioned record:

1. **Misstated base-rate anchor:** `gemini-baseline` claimed the `baseline` band base rate was "less than 1%" rather than pooling the bracketed `reached` risk-set rate (~5.0%) as required for a prediction carrying a frozen `context.band`.
2. **Did not read the Brief in Opposition or Petition text:** The retrieval log confirms that `gemini-baseline` read only `questions-presented.txt`, `documents.json`, and the docket snapshot, never opening `petition.txt` or `brief-in-opposition.txt`. Consequently, `gemini-baseline` accepted the Questions Presented at face value ("clearly outlines two distinct circuit splits") and missed the major vehicle obstacles: the unpublished per curiam nature of the Fourth Circuit's decision, the County's factual argument that Walls never submitted a formal waiver application, and the stale/state-intermediate makeup of the alleged split.
3. **Over-aggressive upward jump and uncalibrated `big_case_score`:** Because it ignored the vehicle defects and the BIO, `gemini-baseline` jumped to `P(grant) = 0.35` and `dissent-from-denial = 0.35`, and assigned an inflated `big_case_score = 0.85` with `big_case_rationale: null`.

## Predicted reasoning (`predicted_reasoning_quality = 0.58`)

`gemini-baseline`'s short forecast document (`predicted_reasoning.md`) got the direction of the procedural steps right but was relatively generic:

- **Further distribution and no CVSG (borne out):** Correctly explained that because the Court requested a response on the same day as the first distribution and the BIO was filed October 1, at least one further distribution would occur (`distribution_count` reached 2 on October 21), and that no CVSG would issue in a local land-use dispute.
- **Conditional grant and denial claims:** Framed Question 1 as the likelier grant focus and noted that a dissent from denial was "plausible" without committing to specific timing, conference windows, or doctrinal analysis beyond restating the Questions Presented. On the rubric, a forecast that is right in direction on the realized procedural calls but brief and largely generic sits slightly above the 0.50 anchor at **0.58**.

## Leakage assessment

- **Mode:** `forward` (prediction timestamp `2026-10-06T00:00:00Z`, tool calls around `00:46–00:48Z`; event resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. All tool calls in `retrieval_log.json` carry `result_capture: "unobserved"` (`result_capture_coverage = 0.0`), which is the standing telemetry shape for that engine. Inspecting the queries directly shows only reads of provisioned case files and `metrics/statpack.md`, with no external searches, and the case was unresolved when predicted.
