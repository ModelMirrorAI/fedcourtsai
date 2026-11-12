# Evaluation of `codex-baseline`

## Overview and Quantitative Scoring

- **Stage / Moment:** Cert (`stage: cert`), arrival moment (`moment: arrival`).
- **Outcome:** `denied` (`actual_granted = 0`), resolved on November 9, 2026 after a single conference distribution (`distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.0025`.
- **Accuracy & Brier Score:** `correct = 1`; `brier_score = (0.0025 - 0)^2 = 0.00000625`.
- **Base-rate reference:** Because the committed statpack was refreshed after `codex-baseline` ran on `2026-08-27T15:51:20Z`, `codex-baseline`'s base-rate figures were checked against the statpack build in force at prediction time (`061c238147aa`, digest `sha256:0d05c670da5896c5e3078e0f81cbb775a2045fc05432d8d957b929849c02f891`, reconstructed via `uv run fedcourts statpack-at`). `codex-baseline` accurately pooled the `sal-v3` `baseline` risk-set rates across OT2017–OT2025 from that build's `statpack.json`—matching the stamped segment base rate methodology—and also appropriately noted the lower Ninth Circuit originating-court cut from that build.

## Reasoning Quality (`0.93`)

Running on August 27, 2026 before `record/documents/` was provisioned, `codex-baseline` conducted thorough pre-petition CourtListener MCP retrieval across both the Ninth Circuit consolidated appeal (`69660612`) and the originating Central District of California docket (`2:24-cv-03455`, docket `68477124`). That investigation uncovered the exact procedural posture later confirmed by the provisioned `appendix.txt`: the district court had dismissed nearly all claims with prejudice in a private real-property dispute, declared the Quaids vexatious litigants, entered a limited prefiling order, and awarded attorneys' fees and costs, and the Ninth Circuit had affirmed in an unpublished May 2026 memorandum after the appeal proceeded pro se.

`codex-baseline` synthesized these facts into a disciplined downward adjustment from the arrival anchor to `0.0025`, correctly treated `relist-increment` (`0.96`) from the arrival moment's zero-distribution baseline as measuring the probability of a single initial conference distribution rather than a post-conference relist, and clearly identified the residual uncertainty from the unprovisioned petition text and unreadable Ninth Circuit memorandum PDF.

## Predicted reasoning (`0.75`)

`codex-baseline`'s `predicted_reasoning.md` made four unconditional central claims and one conditional claim:
1. **Denial of certiorari (`borne-out`):** Forecast that the Court would deny the petition. Confirmed by `actual_disposition: "denied"`.
2. **One initial conference distribution and no second distribution (`borne-out`):** Forecast that from the arrival record's zero-distribution state, the petition would receive one ordinary initial conference distribution (`distribution_count = 1`) and would not be distributed a second time as a true relist. Confirmed by `signals.distribution_count: 1` (distributed October 14, 2026 for the November 6, 2026 conference and denied November 9, 2026).
3. **No CVSG (`borne-out`):** Forecast that the Court would not call for the views of the Solicitor General in this private-party dispute. Confirmed by `signals.cvsg_date: null`.
4. **No dissent or statement on denial (`borne-out`):** Forecast that no Justice would note a dissent or issue a statement respecting the denial. Confirmed by `noted_dissent_from_denial: false`.
5. **Conditional grant route and issue narrowing (`unresolved`):** Forecast that if any relief were granted, it would likely be a summary disposition / GVR narrowed to a procedural issue concerning the dismissal or vexatious-litigant prefiling order rather than plenary review of the property dispute. Untested because certiorari was denied.

Every testable central claim was borne out, including the exact single-distribution trajectory (`distribution_count = 1`), and the conditional discussion reflected concrete details from the lower-court orders (`2:24-cv-03455`).

## Leakage Assessment

- **Mode:** `forward` (`2026-08-27T15:56:42Z`, on docketing day and over two months before the `2026-11-09` denial).
- **Findings:** `retrieval_log.json` (`result_capture_coverage: 0.532`, 62 calls) shows local file reads of the prompt, schemas, event metadata, context, snapshot `2026-08-28.json`, and `metrics/statpack.{md,json}`, plus CourtListener MCP lookups of the Ninth Circuit and C.D. Cal. dockets with `retrieved_doc_date`s no later than `2026-07-02`. No outcome material existed or was retrieved (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`).
