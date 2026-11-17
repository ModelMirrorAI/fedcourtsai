# Evaluation of `codex-baseline` — `scotus/9026000369` (`evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** Certiorari (`cert`), arrival (`opened_at: 2026-09-17`, resolved `2026-11-16`).
- **Outcome:** `denied` (`actual_granted = 0`, `disposition_basis = standard`, `noted_dissent_from_denial = false`, `distribution_count = 1`, `cvsg_date = null`).
- **Prediction:** `predicted_disposition = denied`, `probability = 0.012` (`correct = 1`, `brier_score = 0.000144`). The baseline and skill record are stamped by the harness against the stamped segment base rate.

## Reasoning Quality (`0.78`)

`codex-baseline` wrote a careful, methodologically transparent analysis in `reasoning.md`, tempered by two notable vehicle omissions.

1. **Base-rate discipline:** Verified against the historical statpack build in force when `codex-baseline` ran on September 27, 2026 (`2420d5dd72e1`, `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, `sal-v4`, rather than the later `sal-v8` committed pack), `codex-baseline` accurately pooled the `baseline` risk-set (`reached`) denominator and rates across strictly prior Terms OT2017–OT2025 from `statpack.json`, correctly recognizing that a state respondent does not place a private petitioner in the `state` band and avoiding the terminal zero-relist trap before adjusting downward below the stamped segment base rate.
2. **Strengths in legal and record analysis:**
   - Correctly noted that `appendix.txt` was not yet provisioned on September 27, 2026, and treated the petition's factual characterizations with appropriate caution—specifically warning that the petition's claim to be an "ideal vehicle" did not establish what relief the complaint actually requested (`appendix.txt` later proved that skepticism right: Loop's complaint expressly asked the district court to review the state court decision and enjoin the restraining order).
   - Accurately diagnosed the lack of a developed inter-circuit split, noting that the Ninth and Third Circuit cases cited in the petition largely supported petitioner's stated rule, making QP1 look like case-specific misapplication of an unpublished memorandum.
   - Identified that QP2 could not be reached without first overcoming the jurisdictional dismissal on QP1, and verified *T.M. v. University of Maryland Medical System Corp.*, No. 25-197 (June 2026), via CourtListener to confirm its timing holding offered no basis for a GVR.
3. **Omissions:** Despite reading both the `2026-09-18.json` snapshot and the petition's cover page, `codex-baseline` never noted in `reasoning.md` that the petition was filed *pro se*—missing the single strongest empirical downward adjustment on a paid arrival petition (and thus leaving `P = 0.012` twice as high as `claude-baseline` and twelve times `gemini-baseline`). It also overlooked the facial sovereign, judicial, and arbitral immunity obstacles posed by suing the State of Washington, its Attorney General, JAMS, and a retired-judge arbitrator under § 1983, which formed the district court's alternative Rule 12(b)(6) dismissal ground.

## Predicted reasoning

`predicted_reasoning.md` earned `0.78`. All four resolved central claims were borne out: certiorari was denied without separate writing (`actual_disposition = denied`, `noted_dissent_from_denial = false`), the petition went through a single initial distribution following waivers and was denied without relist in November 2026 (`distribution_count = 1`, distributed October 28, denied November 16), and no CVSG issued (`cvsg_date = null`). Its conditional grant-scope and plenary-versus-summary passage remained unresolved upon denial (while its point that *T.M.* did not warrant a GVR held). Compared with top-of-scale forecasts, `codex-baseline` hedged somewhat more broadly on path and timing ("after the response deadline or a waiver", "November or December 2026, with briefing extensions potentially moving it into early 2027"), placing it solidly just above the `0.75` anchor.

## Leakage Assessment

Clean `forward` cell (`leakage_suspected = false`, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`). The prediction ran on `2026-09-27` while the petition was open (resolved `2026-11-16`). In `retrieval_log.json` (`result_capture_coverage = 0.923`), 24 of 26 calls are captured and the two `unobserved` `web-search` calls queried only the June 2026 Supreme Court opinion in *T.M. v. University of Maryland Medical System Corp.* (No. 25-197), not *Loop*.
