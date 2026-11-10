# Evaluation of `gemini-baseline` (`scotus/9026000351`, `evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage:** `cert` (arrival moment)
- **Predicted disposition / probability:** `denied` (`probability = 0.001`, `granted = 0`)
- **Actual outcome:** `denied` (`actual_granted = 0`, resolved `2026-11-09` after 1 distribution, no CVSG, no noted dissent)
- **Correct:** `1`
- **Brier score:** `0.000001`
- **Baseline & skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for the harness to stamp from the committed statpack (`risk_set` basis under the prediction's frozen `sal-v4` `baseline` band). Adjusting from the stamped segment base rate down to 0.1% on a denied petition yields positive skill over the baseline and the lowest Brier score among the three candidates.

## Reasoning Quality (`0.68`)

`gemini-baseline` reached the right headline conclusion (`P(grant) = 0.001`, `denied`) and gave the most realistic `big_case_score` (`0.1`) among the candidates, but its analysis in `reasoning.md` was thin:

1. **Base-rate anchoring and high-level posture:** Verified against the statpack build in force at prediction time (`2420d5dd72e1`, rebuilt via `uv run fedcourts statpack-at`), `gemini-baseline` properly referenced the `sal-v4` `baseline` reached (risk-set) rate across the preceding Terms and correctly identified from `2026-09-17.json` and `questions-presented.txt` that the petitioner is proceeding pro se on a paid docket, bringing a third-party collateral attack on the Federal Circuit Judicial Council's suspension of Judge Pauline Newman via the Tucker Act, and that the Solicitor General would likely waive response.
2. **Omission of `petition.txt` and specific vehicle bars:** As `retrieval_log.json` shows, `gemini-baseline` read `questions-presented.txt` and `documents.json` but never opened `petition.txt`. Consequently, its four-paragraph rationale missed the concrete holdings below and the specific preservation bars disclosed in the petition: that the Court of Federal Claims dismissed sua sponte for lack of a money-mandating source of law under 28 U.S.C. § 1491(a)(1), that the Federal Circuit granted summary affirmance under binding precedent, that the petition's own footnote conceded neither court below addressed QP 1 (§ 354), and that the Supreme Court had already denied mandamus on the recusal issue in No. 25-1217.
3. **No rationale for auxiliary claim probabilities:** `reasoning.md` did not discuss how `gemini-baseline` arrived at its declared claim probabilities (`relist-increment` = 0.99, `cvsg-increment` = 0.001, `summary-disposition-route` = 0.05, `dissent-from-denial` = 0.01).

## Predicted reasoning (`0.75`)

`gemini-baseline`'s brief forecast document (`predicted_reasoning.md`) got the core unconditional claims right:

- **Waiver, single distribution, and denial (borne out):** Correctly predicted that the petition would be distributed once following the respondent's likely waiver of the right to respond, with zero further relists, and denied (`2026-11-09.json` records the October 16, 2026 waiver, October 21, 2026 distribution, `distribution_count: 1`, and November 9, 2026 denial).
- **No CVSG and no dissent from denial (borne out):** Correctly forecast no CVSG because the United States is the named respondent (`cvsg_date: null`) and no dissent or statement respecting denial (`noted_dissent_from_denial: false`).
- **Conditional grant claim (unresolved, though weakly grounded):** Suggested that if granted, the Court would likely address QP 1 regarding the constitutionality of 28 U.S.C. § 354 and that a GVR was improbable. While untested because certiorari was denied, this conditional claim overlooked that neither lower court reached QP 1 (a fact stated in the petition text that `gemini-baseline` did not read).

The `0.75` grade credits `gemini-baseline` for accurately forecasting the waiver, single distribution, absence of CVSG, and unexplained denial without dissent, while reflecting the brevity of the document and its unexamined conditional assumption on QP 1.

## Leakage Assessment

- **Mode:** `forward` (predicted `2026-09-27`, cutoff `2026-09-17`; resolved `2026-11-09`)
- **Retrieved outcome material:** `false`
- **Influenced prediction:** `not_applicable` (`leakage_suspected: false`)
- **Notes:** The prediction ran in forward mode more than a month before the case was distributed or decided. In `retrieval_log.json`, all calls carry `result_capture: "unobserved"` (`result_capture_coverage: 0.0`), which is the engine's standing telemetry shape; grading the calls by their queries confirms they were strictly local reads of the prompt, `event.yaml`, `context.json`, `2026-09-17.json`, `questions-presented.txt`, `documents.json`, and `metrics/statpack.md`, with no external searches or outcome material.
