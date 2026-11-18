# Evaluation of `gemini-baseline` — `scotus/9026000369` (`evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** Certiorari (`cert`), arrival (`opened_at: 2026-09-17`, resolved `2026-11-16`).
- **Outcome:** `denied` (`actual_granted = 0`, `disposition_basis = standard`, `noted_dissent_from_denial = false`, `distribution_count = 1`, `cvsg_date = null`).
- **Prediction:** `predicted_disposition = denied`, `probability = 0.001` (`correct = 1`, `brier_score = 0.000001`). The baseline and skill record are stamped by the harness against the stamped segment base rate.

## Reasoning Quality (`0.52`)

`gemini-baseline` reached a well-calibrated headline probability (`0.001`) on `reasoning.md`, but its legal analysis is cursory and skipped reading the body of the provisioned petition.

1. **What held up:** Verified against the historical statpack build in force when `gemini-baseline` ran on September 27, 2026 (`2420d5dd72e1`, `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, `sal-v4`, rather than the later `sal-v8` committed pack), `gemini-baseline` properly referenced the `baseline` band's `reached` rate pooled over OT2017–OT2025 before adjusting sharply below the stamped segment base rate. It also correctly noted the arrival-time absence of docket signals, the *pro se* filing posture, and the extreme unlikelihood of Supreme Court review for a § 1983 / *Rooker-Feldman* collateral attack on a state family-law arbitration dispute.
2. **Analytical superficiality:** `reasoning.md` is a single brief paragraph reflecting only the cover page and questions presented (`gemini-baseline` read only the first 50 lines of `petition.txt`). As a result, it failed to identify almost every concrete case-specific feature documented in the petition:
   - It did not mention that the Ninth Circuit decision below was an **unpublished memorandum**.
   - Rather than examining the petition's cited authorities to check whether a split existed, it relied on the generic truism that the Court rarely grants *pro se* cases lacking a split.
   - It overlooked *T.M. v. University of Maryland Medical System Corp.*, No. 25-197 (decided June 18, 2026, and addressed at pp. 15–16 of the petition).
   - It missed both that QP2 was never reached below due to the Rule 12(b)(1) dismissal and that sovereign, judicial, and arbitral immunities independently barred claims against Washington, its Attorney General, JAMS, and the retired-judge arbitrator.

## Predicted reasoning

`predicted_reasoning.md` earned `0.55`, sitting near the `0.5` anchor ("right in direction but generic — it commits to little beyond the outcome itself"). Every resolved statement in the six-sentence forecast held—zero relists (`distribution_count = 1`), no CVSG (`cvsg_date = null`), no summary GVR, and a clean denial without noted dissent (`noted_dissent_from_denial = false`)—while its conditional QP1-over-QP2 selection remained unresolved upon denial. However, the document offered no specific commitments on briefing/waiver trajectory or conference timing, mischaracterized QP2's defect as merely "fact-bound" rather than unreached below, and asserted there was "no intervening precedent regarding Rooker-Feldman" without noticing the Court's June 2026 decision in *T.M.* discussed in the petition itself.

## Leakage Assessment

Clean `forward` cell (`leakage_suspected = false`, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`). The prediction ran on `2026-09-27` while the case was unresolved (decided `2026-11-16`). Every row in `retrieval_log.json` carries `result_capture: unobserved` (`result_capture_coverage = 0.0`, an engine telemetry characteristic), and grading each call on its query confirms `gemini-baseline` accessed only local prompts, schemas, provisioned case files, `metrics/statpack.md`, and two prior-era `fedcourts query` invocations.
