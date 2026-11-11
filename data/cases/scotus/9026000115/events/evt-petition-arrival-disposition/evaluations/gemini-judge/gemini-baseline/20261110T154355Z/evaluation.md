# Evaluation of `gemini-baseline` — `scotus/9026000115` (`evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage & Moment:** Certiorari (`cert`), `arrival` moment (`opened_at: 2026-07-24`, resolved `2026-11-09`).
- **Outcome:** Denied (`actual_disposition: "denied"`, `actual_granted: 0`, `distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.01`.
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = 0.0001` (`(0.01 - 0)^2`).
- **Baseline & Skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for harness stamping (`stamp-cell`), which pools the stamped segment base rate from the statpack.

## Reasoning Quality (`reasoning_quality = 0.55`)

`gemini-baseline` reached the right headline conclusion (`predicted_disposition: "denied"`, `probability: 0.01`), beating the stamped segment base rate, and referenced the prediction-time statpack (`ab6fb84c09a6`, digest `sha256:f8abdb31530370551ced5a16ef3db2ecf512b450e040799d9ec5d03b7b9f48c4`, under `sal-v3`), anchoring on the paid scored segment's `baseline` band `reached` rate over prior Terms. However, its analysis had two notable weaknesses:

1. **Omission of `petition.txt` and Appended Opinions:** As confirmed by `retrieval_log.json`, `gemini-baseline` read `questions-presented.txt` and `documents.json` but never opened `petition.txt`. While `questions-presented.txt` was enough to see that the petition challenged a Title VII COVID-19 vaccine summary-judgment ruling and a Rule 56(d) expert-affidavit denial without alleging a circuit split, skipping `petition.txt` meant `gemini-baseline` missed critical vehicle facts in the record: that the Fourth Circuit's decision was an unpublished, unreasoned one-paragraph per curiam opinion without oral argument, that the District Court's Rule 56(d) denial rested on case-specific diligence failures (no Rule 56(d) affidavit and 18+ months of prior discovery), and that the petition erroneously cited 28 U.S.C. § 1257 for jurisdiction.
2. **Misinterpretation of `relist-increment` at Arrival (`distribution_count = 0`):** In `reasoning.md`, `gemini-baseline` wrote that "[t]he probability of a relist (modeled as `relist-increment` from the current zero distributions) is low because the petition lacks the hallmarks of a cert-worthy case that would draw a second look at conference," and set `relist-increment` to `0.15`. At `distribution_count = 0`, however, `relist-increment` resolves to 1 whenever the petition's final `distribution_count` exceeds 0—that is, whenever the petition is distributed at least once for conference, which happens routinely for paid petitions (and happened here on October 14, 2026, `distribution_count: 1`). Conflating the initial distribution increment from zero with a post-conference relist was a clear definition error. In addition, `reasoning.md` did not explain its relatively high `0.08` probability on `dissent-from-denial`.

## Predicted Reasoning (`predicted_reasoning_quality = 0.65`)

`gemini-baseline`'s forecast document (`predicted_reasoning.md`) was brief and somewhat generic, reflecting its reliance on `questions-presented.txt` rather than the full petition and lower-court opinions, though its main testable calls were borne out:

- **Denial Without Relists (`borne-out`):** Forecast that the petition would be denied without any relists (`actual_disposition: "denied"`, `distribution_count: 1`). Note that while `predicted_reasoning.md` did not explicitly state that the petition would be distributed once before denial, its prose prediction of denial without relists held up.
- **No CVSG (`borne-out`):** Forecast no CVSG because the dispute involves a private employer and does not implicate federal interests (`cvsg_date: null`).
- **Unlikely Statement or Dissent from Denial (`borne-out`):** Forecast that a statement or dissent from denial was unlikely given the fact-bound posture (`noted_dissent_from_denial: false`).
- **Conditional Grant Route and Questions (`unresolved`):** Forecast that a summary disposition (GVR) was very unlikely and that if granted, the Court would likely take QPs 1 and 3 and ignore the Rule 56(d) procedural questions (QPs 2 and 4). Because certiorari was denied, this conditional forecast was not tested—though it is worth noting that QP 3 was directed at whether the *District Court* erred rather than the Fourth Circuit, making it an improper question for Supreme Court review.

Because the central testable calls held in direction but the forecast was generic and missed the specific procedural details of the record below, it earns `0.65`.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-08-16T11:11:04Z`; event resolved `2026-11-09`).
- **Audit of `retrieval_log.json`:** All 28 calls carry `result_capture: "unobserved"` (`result_capture_coverage: 0.0`, the engine's standard telemetry shape). Inspection of the logged call queries shows only local reads of project instructions, schemas, the `2026-08-16.json` snapshot, `questions-presented.txt`, and `metrics/statpack.md`, with no external search or post-cutoff access (`retrieved_outcome_material: false`, `influenced_prediction: "not_applicable"`, `leakage_suspected: false`).
