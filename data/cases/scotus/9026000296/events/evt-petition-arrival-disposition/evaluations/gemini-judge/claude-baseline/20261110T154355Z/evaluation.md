# Evaluation of `claude-baseline`

## Overview and Quantitative Summary

- **Stage & Moment:** Cert stage (`cert`), arrival moment (`evt-petition-arrival-disposition`).
- **Outcome:** Petition `denied` on November 9, 2026 (`actual_granted = 0`, `distribution_count = 1`, `cvsg_date = null`, `noted_dissent_from_denial = false`).
- **Prediction:** `predicted_disposition = "denied"`, `probability = 0.012` (`correct = 1`, `brier_score = 0.000144`).
- **Baseline & Skill:** The harness stamps the segment base rate and Brier skill score from the committed statpack. `claude-baseline` conditioned on its frozen `baseline` arrival band (`sal-v4`, strictly prior Terms OT2017–OT2025) and adjusted decisively downward below the stamped segment base rate to `0.012`.

## Reasoning Quality (`0.93`)

`claude-baseline` delivered the strongest and most thorough analysis in the panel (`reasoning.md`):

1. **Independent Verification of the Decision Below:** Recognizing that only `petition.txt` and `questions-presented.txt` were provisioned in `record/documents/` at the time of the arrival run (the separate appendix was fetched later), `claude-baseline` used CourtListener MCP to locate and read the Ninth Circuit's published June 3, 2026 disciplinary opinion (*Lnu v. Blanche*, No. 24-4790, 177 F.4th 1014, cluster 10869591). That allowed `claude-baseline` to test the petition's framing against the panel's actual text—specifically noting that the Ninth Circuit expressly stated it limited its sanctions "to the issues identified in the Order to Show Cause," observed that both attorneys waived an evidentiary hearing by never requesting one, and grounded its candor findings in existing professional-conduct rules rather than inventing a retroactive standalone rule under FRAP 47(b).
2. **Doctrinal Precision:** `claude-baseline` connected the notice issue not only to *In re Ruffalo*, 390 U.S. 544 (1968), and *In re Snyder*, 472 U.S. 634 (1985), but also to *Zauderer v. Office of Disciplinary Counsel*, 471 U.S. 626 (1985), which cabined *Ruffalo* to prejudicial surprise, and checked post-1986 Supreme Court case law to confirm how rarely the Court grants plenary review of federal appellate bar-discipline orders.
3. **Sound Base-Rate Conditioning and Calibration:** `claude-baseline` properly pooled the `sal-v4` arrival `reached` rate for `baseline` across OT2017–OT2025, explicitly avoided the terminal zero-relist rate Trap, and justified moving well below the stamped segment base rate to `0.012` based on the absence of any circuit split on either Question Presented, the error-correction posture, and the deeply unsympathetic facts (undisputed AI-fabricated citations across three appeals).

## Predicted Reasoning (`0.95`)

`claude-baseline`'s forecast document (`predicted_reasoning.md`) was remarkably specific on the procedural path and timing, and every unconditional commitment was borne out on the docket:

- **Denial (`borne-out`):** Correctly forecast that the petition would be denied.
- **SG Waiver and Single Conference Distribution (`borne-out`):** Specifically forecast that the Solicitor General would waive the right to respond (rather than file a brief in opposition) and that the petition would be distributed once for a conference in late October or November 2026 and denied at that single conference without a relist. In fact, the SG waived on September 18, 2026, and the petition was distributed once on October 14, 2026 for the November 6, 2026 conference and denied without a relist.
- **No CVSG (`borne-out`):** Correctly forecast no CVSG because the federal government was already the respondent represented by the Solicitor General.
- **First-Half-of-November Timing and No Separate Writing (`borne-out`):** Specifically forecast that denial would issue "by the end of November 2026, most likely on an order list in the first half of November," with no separate writing respecting denial. The denial issued on the November 9, 2026 order list with no noted dissent or statement.
- **Conditional Grant Scope and Route (`unresolved`):** Forecast that if the Court acted at all, it would take Question 1 (*Ruffalo*) rather than Question 2, via summary reversal or plenary review rather than a GVR; untested given the denial.

## Leakage Assessment

- **Mode:** `forward` (run on September 27, 2026, more than six weeks before the November 9, 2026 denial).
- **Findings:** Clean (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`). The harness log (`result_capture_coverage = 1.0`) shows only local reads of the September 9, 2026 snapshot, petition text, and statpack, two generic `fedcourts query` calls, and CourtListener lookups for the June 3, 2026 Ninth Circuit order below, historical *Ruffalo* decisions, and SCOTUS docket 26-296 (which returned 0 results at the time). Note that the September 18, 2026 waiver was not yet in the September 9, 2026 truncated arrival snapshot and was not retrieved on CourtListener, so `claude-baseline`'s call that the SG would waive was a genuine forward prediction.
