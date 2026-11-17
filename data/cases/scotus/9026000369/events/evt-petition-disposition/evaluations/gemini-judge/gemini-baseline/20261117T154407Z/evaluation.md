# Evaluation of `gemini-baseline` — `scotus/9026000369` (`evt-petition-disposition`)

## Quantitative Summary

- **Stage / Moment:** `cert` / `distribution`
- **Predicted vs. Actual Disposition:** `denied` vs. `denied` (`correct = 1`)
- **Probability / Brier Score:** `P(granted) = 0.01` vs. `actual_granted = 0` (`brier_score = 0.0001`)
- **Baseline & Skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left for the harness to stamp from the committed statpack; `gemini-baseline`'s `0.01` forecast substantially outperforms the stamped segment base rate on this resolved denial.

## Reasoning Assessment (`reasoning_quality = 0.95`)

`gemini-baseline` delivered an exemplary cert-stage analysis in `reasoning.md`, combining disciplined base-rate conditioning with exhaustive reading of the provisioned petition, appendix, docket snapshot, and directly relevant June 2026 Supreme Court precedent.

1. **Base-rate verification (`statpack-at`):** Reconstructing the statpack build in force when `gemini-baseline` ran (`uv run fedcourts statpack-at`, build `648fc43559f5`) confirms that every figure cited in `reasoning.md`—the frozen `baseline` risk-set anchor, the modern discretionary-cert proportions (`44,772` resolved), the Ninth Circuit paid-segment slice (`n = 5,514`), the zero-relist bucket (`n = 10,204` resolved, `401` open), and the `2+` amicus bucket (`n = 1,446` resolved)—matches build `648fc43559f5` to the digit. Crucially, `gemini-baseline` correctly explained why the marginal `2+` amicus table in the statpack is heavily confounded by relisted, CFR, and CVSG petitions and cannot be applied unadjusted to a once-distributed waived petition.
2. **Doctrinal and record mastery:** `gemini-baseline` retrieved and read *T. M. v. University of Maryland Medical System Corp.*, No. 25-197 (decided June 18, 2026, opinion `11345156`), and demonstrated how *T. M.* directly undercut the petition: four months earlier, the Court had reaffirmed *Rooker-Feldman* where a state-court litigant with pending state appeals sued in federal district court to declare a state order unconstitutional and enjoin its enforcement. Pairing *T. M.* with Judge Evanson's verbatim quotation of Loop's operative *pro se* complaint (`appendix.txt`, App-6 to App-7, explicitly asking the district court *"to review the Washington State decision that affirmed an arbitration award"* and enjoin the restraining order), `gemini-baseline` showed that QP 1 faced an insurmountable pleading and preservation barrier (`Padgett v. Wright`, App-2).
3. **Comprehensive vehicle analysis:** `gemini-baseline` identified every independent ground blocking plenary review or a GVR: QP 2 was never passed upon below; the district court dismissed on alternative Rule 12(b)(6) grounds of sovereign/judicial immunity (*In re Castillo*) and arbitral immunity (*Sacks v. Dietrich*, App-7 to App-8); the February 23, 2024 restraining order expired by its own terms on September 1, 2025 (App-3, App-11) while the child (16 in February 2024) reached majority; and Loop's parallel Washington appellate litigation had concluded (`petition.txt` at ii–iii), creating severe mootness and preclusion obstacles. It also accurately distinguished Loop's *pro se* filing of `petition.txt` from Gene C. Schaerr's subsequent docket appearance alongside five amici, resisted overreacting to waived-case amicus filings (`relist-increment = 0.04`), and placed `P(granted)` sharply at `0.01`. (Calling the Ninth Circuit disposition a "two-paragraph" rather than three-paragraph memorandum at App-2 is entirely inconsequential.)

## Predicted reasoning (`predicted_reasoning_quality = 0.88`)

`gemini-baseline`'s `predicted_reasoning.md` made crisp, specific, and unhedged commitments on every dimension the realized order tested:

- **Central claims borne out:** (1) Immediate denial on the Monday order list following the November 13, 2026 Conference without a CFR, relist, or redistribution (`relist-increment = 0.04`), which was non-trivial given five amicus briefs and experienced Supreme Court counsel on the docket (`resolved_at = 2026-11-16`, `distribution_count = 1`); (2) no CVSG (`cvsg_date = null`); and (3) a standard unsigned denial order with no noted dissent or separate statement (`disposition_basis = "standard"`, `noted_dissent_from_denial = false`).
- **Conditional claims unresolved:** Two sections—limiting review to QP 1 rather than QP 2 if granted, and favoring plenary review (75%) over summary disposition (25%) conditional on a grant—never took effect because certiorari was denied, earning neither credit nor penalty under the rubric. Because every testable commitment was specific, discriminating against the plausible CFR/redistribution alternative, and completely borne out, while two substantial sections remained conditional on an unrealized grant, the forecast document grades near the top of the scale at `0.88`.

## Leakage & Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward run placed on `2026-10-31`, sixteen days prior to the `2026-11-16` denial. Inspection of `retrieval_log.json` and prose confirms zero access to `data/qp-topics/` and no outcome-revealing material.
- **Big-case read (`0.10`):** Independent evaluator assessment reflects low systemic stakes for a fact-bound, vehicle-impaired collateral challenge to an expired domestic-relations restraining order summarily denied on waivers, tempered slightly by five thematic amicus filings.
