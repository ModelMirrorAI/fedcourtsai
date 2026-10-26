# Evaluation of `codex-baseline` — `scotus/73550516` (`evt-petition-disposition`)

## Stage and Outcome Summary

- **Stage:** `cert` (`moment: distribution`)
- **Realized outcome:** `actual_disposition = "dismissed"`, `actual_granted = 0` (joint stipulation to dismiss under Rule 46 filed October 19, 2026; dismissed October 20, 2026). The docket recorded no further distributions beyond the initial August 12, 2026 distribution (`signals.distribution_count = 1`), no CVSG (`signals.cvsg_date = null`), and no separate writings (`noted_dissent_from_denial = null`).
- **Prediction summary:** `predicted_disposition = "denied"`, `granted = 0`, `probability = 0.24`.
- **Headline scores:**
  - `correct = 0`: On a cert cell, `correct` requires an exact label match between `predicted_disposition` (`"denied"`) and `actual_disposition` (`"dismissed"`). Although `codex-baseline` rightly predicted that certiorari would not be granted (`granted = 0` vs. `actual_granted = 0`), the voluntary Rule 46 dismissal rather than a conference denial makes the exact disposition label match `0`.
  - `brier_score = 0.0576`: `(0.24 - 0)^2 = 0.0576`.
  - **Baseline and skill:** Because the scored prediction carries a frozen `context.band` (`baseline` under `sal-v4`), `segment_base_rate`, `brier_skill_score`, `base_rate_basis`, and `claim_scores` are left for `stamp-cell` to compute against the stamped segment base rate.

## What `codex-baseline` Got Right and Wrong

- **What went right:**
  - **Thorough engagement with the provisioned record:** `codex-baseline` read the entire 45-page petition and appendices (`petition.txt`), including the unpublished two-page Fifth Circuit per curiam below (Appendix A), the controlling published opinion in *Town of Vinton v. Indian Harbor Insurance Co.*, 161 F.4th 282 (5th Cir. 2025) (Appendix B), the en banc denial order (Appendix C), and Judge Milazzo's Eastern District of Louisiana order (Appendix D). It even caught an internal error in the petition's factual statement (which claimed removal to the Western District of Louisiana when Appendices A and D establish the case came from the Eastern District of Louisiana, No. 2:23-cv-2060).
  - **Independent verification of cited precedent:** Using CourtListener MCP, `codex-baseline` verified *GE Energy Power Conversion France SAS, Corp. v. Outokumpu Stainless USA, LLC*, 590 U.S. 432, 445 (2020), confirming that Section IV expressly reserved which body of law governs equitable estoppel under the New York Convention, and inspected *Setty v. Shrinivas Sugandhalaya LLP*, 3 F.4th 1166 (9th Cir. 2021), noting both the majority's federal-substantive-law rule and Judge Bea's dissent.
  - **Sound doctrinal and vehicle analysis:** Rather than taking the petitioner's 4-1 circuit-split framing at face value, `codex-baseline` analyzed the threshold contract-construction obstacle highlighted in *Town of Vinton*: the policy's Allocation Endorsement ("shall be constructed as a separate contract between [Apex] and each of the Insurers") and the interaction with Louisiana's anti-arbitration statute, La. R.S. § 22:868, under *Police Jury of Calcasieu Parish v. Indian Harbor Insurance Co.*, 395 So. 3d 717 (La. 2024). It also properly recognized that this petition was explicitly postured as a hold vehicle behind *Indian Harbor Insurance Co. v. Town of Vinton*, making a plenary grant here unlikely and any grant-family outcome primarily derivative (via a GVR if the lead petition were granted and reversed).
  - **Restrained redistribution estimate:** Among the three candidates, `codex-baseline` gave the most measured probability for `relist-increment` (`0.70`), recognizing that the snapshot lacked post-August 17 filings and leaving substantial probability mass for a non-redistributed path.
- **What it missed:**
  - `codex-baseline` did not look up the lead *Indian Harbor v. Town of Vinton* Supreme Court docket (which had been docketed as No. 25-1383 after the extension application No. 25-A1099 cited in the petition), and it did not explicitly discuss the possibility of a pre-redistribution Rule 46 voluntary dismissal in `reasoning.md` or `predicted_reasoning.md`. Its `0.24` grant-family probability was also slightly on the generous side for a follower vehicle, though well-explained given the August 17 call for a response and the reserved *GE Energy* question.

## Reasoning Quality (`0.88`)

`codex-baseline` earns `0.88` for a careful, well-structured, and legally grounded analysis. It anchored properly on the strictly prior cohort relative to the stamped segment base rate, avoided double-counting terminal base-rate slices, verified key appellate authorities directly rather than relying solely on petitioner advocacy, and clearly separated plenary-grant prospects from derivative hold-and-GVR prospects.

## Leakage Audit

- **Mode:** `forward` (run on 2026-10-06, prior to the 2026-10-20 resolution).
- **Findings:** Clean (`retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`). All 42 tool calls in `retrieval_log.json` were audited; external lookups were restricted to historical opinions (*GE Energy* and *Setty*), no `data/qp-topics/` paths were read, and `retrieval.md` matches the captured log.
