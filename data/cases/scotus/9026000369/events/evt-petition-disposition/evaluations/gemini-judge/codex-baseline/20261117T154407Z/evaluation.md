# Evaluation of `codex-baseline` — `scotus/9026000369` (`evt-petition-disposition`)

## Quantitative Summary

- **Stage / Moment:** `cert` / `distribution`
- **Predicted vs. Actual Disposition:** `denied` vs. `denied` (`correct = 1`)
- **Probability / Brier Score:** `P(granted) = 0.025` vs. `actual_granted = 0` (`brier_score = 0.000625`)
- **Baseline & Skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left for the harness to stamp from the committed statpack; `codex-baseline`'s `0.025` forecast improves substantially upon the stamped segment base rate on this denial.

## Reasoning Assessment (`reasoning_quality = 0.89`)

`codex-baseline` produced a rigorous, well-grounded analysis in `reasoning.md` that carefully engaged both the empirical structure of the statpack and the concrete record in `petition.txt` and `appendix.txt`.

1. **Base-rate verification (`statpack-at`):** Reconstructing the statpack build in force when `codex-baseline` ran (`uv run fedcourts statpack-at`, build `648fc43559f5`) confirms that every figure quoted in `reasoning.md`—the zero-, one-, two-, and `3+`-relist buckets (`10,204` / `401`, `2,532` / `33`, `495` / `11`, `482` / `6`), the no-CVSG and CVSG buckets (`13,549` / `435` and `164` / `16`), and the `2+` amicus bucket (`1,446` resolved, `94` open, `1,540` total)—matches build `648fc43559f5` exactly. Its methodological explanation of why terminal statpack buckets are not independent multipliers and why the marginal `2+` amicus rate cannot replace the frozen risk-set anchor is particularly clear.
2. **Thorough engagement with the record and *T. M.*:** `codex-baseline` read the full appendix (`App-1` through `App-18`) as well as the petition, retrieved *T. M. v. University of Maryland Medical System Corp.* (decided June 18, 2026, opinion `11345156`) via CourtListener MCP, and accurately explained why *T. M.* was adverse precedent for this vehicle rather than a basis for a GVR. Beyond noting Judge Evanson's quotation of Loop's complaint (`App-6` to `App-7`) and the alternative immunity / Rule 12(b)(6) rulings (`App-7` to `App-9`), `codex-baseline` astutely pointed out that the appended King County restraining order itself contained explicit notice/opportunity-to-be-heard and credible-threat findings (`App-11` to `App-14`) alongside its September 1, 2025 expiration date (`App-11`), further undercutting the petition's clean constitutional framing.
3. **Minor limitations:** Two small blemishes hold `reasoning.md` slightly below the very top of the scale. First, `codex-baseline` missed that Supreme Court practitioner Gene C. Schaerr had entered an appearance as Counsel of Record on the docket snapshot (`2026-10-31.json`), treating the posture purely as a self-represented challenge (its `jq 'del(.Petitioner,...)'` inspection filtered out the `.Petitioner` counsel block). Second, its `0.18` probability on an additional distribution (`relist-increment`) and `0.39` `big_case_score` gave somewhat generous weight to the five amicus briefs relative to the fatal pleading, immunity, and mootness defects it had itself documented.

## Predicted reasoning (`predicted_reasoning_quality = 0.82`)

`codex-baseline`'s `predicted_reasoning.md` is clear, well-structured, and accurate across every dimension resolved by the November 16, 2026 order:

- **Central claims borne out:** `codex-baseline` forecast that the Court would deny certiorari in the ordinary orders following the November 13, 2026 conference without an explanatory opinion (`actual_disposition = "denied"`, `disposition_basis = "standard"`, `resolved_at = "2026-11-16"`), with a modal call of zero further distributions (`distribution_count = 1`), no CVSG (`cvsg_date = null`, `0.2%`), and no dissent or separate statement respecting denial (`noted_dissent_from_denial = false`, `2.5%`).
- **Specificity and conditional content:** Its conditional grant forecasts (taking a narrowed QP 1 while leaving QP 2 aside, and 75% plenary vs. 25% summary disposition because *T. M.* supplies no favorable GVR hook) are `unresolved` given the denial. On the primary live procedural question—whether the five amicus briefs would prompt a response request and second distribution—its modal zero-relist call was borne out, though hedged at an `18%` redistribution probability, placing `predicted_reasoning_quality` cleanly at `0.82`.

## Leakage & Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward run placed on `2026-10-31`, sixteen days before the `2026-11-16` denial. Both unobserved provider-side web searches in `retrieval_log.json` queried `supremecourt.gov` for *Skinner* and *T. M.*, not *Loop*, and all captured corpus and CourtListener calls predate the resolution with no access to `data/qp-topics/`.
- **Big-case read (`0.10`):** Independent evaluator assessment reflects low systemic stakes for a fact-bound *pro se* § 1983 challenge to an expired marital-dissolution restraining order summarily denied on waivers.
