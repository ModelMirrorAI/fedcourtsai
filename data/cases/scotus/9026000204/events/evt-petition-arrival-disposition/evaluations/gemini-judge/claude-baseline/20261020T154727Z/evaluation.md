# Evaluation of `claude-baseline` (`scotus/9026000204` — `evt-petition-arrival-disposition`)

## Quantitative Summary

- **Stage:** `cert` (arrival moment)
- **Predicted Disposition:** `granted` (P(grant) = 0.90)
- **Actual Disposition:** `granted` (`actual_granted` = 1, plenary review, resolved 2026-10-19 after 2 distributions)
- **`correct`:** 1
- **`brier_score`:** 0.01
- **Baseline & Skill:** Because `claude-baseline`'s scored prediction carries a frozen `context.band` (`federal` under `sal-v3`), `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left null for the harness to stamp from the risk-set pool over the stamped segment base rate.

## Reasoning Quality (`0.94`)

`claude-baseline` provided a rigorous, well-structured arrival-stage analysis in `reasoning.md`:

1. **Base-Rate and Posture Discipline:** `claude-baseline` clearly stated the `arrival` moment constraints (no BIO, zero distributions, no CVSG) and anchored properly on the stamped segment base rate for the `federal` salience band.
2. **Doctrinal and Split Analysis:** `claude-baseline` thoroughly documented why this petition stood near the top of the `federal` band: the Fifth Circuit's invalidation of an Act of Congress (26 U.S.C. § 5178(a)(1)(B)) under the Necessary and Proper Clause, the Court's near-uniform practice of reviewing appellate invalidations of federal statutes (citing *Iancu v. Brunetti* and recent SG petitions documented in the petition), and the direct, acknowledged conflict with the Sixth Circuit's decision in *Ream v. Department of the Treasury*, 174 F.4th 480 (2026).
3. **Downside Risk and Vehicle Discussion:** `claude-baseline` explicitly weighed the companion petition in *Ream* (No. 26-93) and epistemic limitations (truncated petition appendix, unfiled BIO). Its downward adjustment from ~0.95 to 0.90 was slightly conservative—largely because holding *McNutt* for *Ream* followed by a GVR would still resolve as `actual_granted = 1` on the binary grant axis, and *McNutt* was the cleaner vehicle where the federal statute had actually been struck down without standing complications—but the reasoning was transparent, coherent, and well-supported by the record.

## Leakage Assessment

- **Mode:** `forward` (prediction timestamp `2026-08-20T18:32:41Z`, nearly two months prior to the `2026-10-19` resolution).
- **Log Review:** `retrieval_log.json` (100% capture coverage) shows reads of the provisioned arrival snapshot (`2026-08-19.json`), the petition text, and `metrics/statpack.md`, three `fedcourts query` calls for historical granted petitions, and two CourtListener docket searches for the pending companion petition *Ream* (No. 26-93). No post-decision material existed or was accessed.
- **Conclusion:** `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.
