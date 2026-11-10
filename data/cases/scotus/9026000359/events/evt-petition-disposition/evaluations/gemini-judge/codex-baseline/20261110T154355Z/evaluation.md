# Evaluation of `codex-baseline`

## Overview and Quantitative Summary

- **Stage:** `cert` (`evt-petition-disposition`, distribution moment).
- **Predicted vs. Actual Disposition:** Predicted `denied` (`probability = 0.012`); actual outcome `denied` (`actual_granted = 0`) on November 9, 2026 after a single distribution (`distribution_count = 1`, no CVSG, no noted dissent).
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = 0.000144`.
- **Base Rate & Skill:** Left null for the harness to stamp (`stamp-cell` pools the stamped segment base rate from the statpack over prior Terms under the prediction's frozen `context.band = "baseline"` and `salience_version = "sal-v4"`). Graded against the statpack build in force at prediction time (`886549a3ac32`, `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, reconstructed via `fedcourts statpack-at`), `codex-baseline` pooled the exact prior-Term (`2017–2025`, excluding `2026`) `sal-v4` `baseline` reached figures from `statpack.json` (643 grant-family outcomes over 12,877 weighted resolved petitions = 4.9934%) and used that anchor rigorously.

## Reasoning Quality (`0.94`)

`codex-baseline` produced an exceptionally thorough legal and statistical analysis in `reasoning.md`:
1. **Exact Base-Rate Discipline:** Pooled the `sal-v4` `baseline` risk-set rate strictly over Terms 2017–2025 from the statpack in force at prediction time (`886549a3ac32`), explicitly avoiding contamination from the 2026 Term row and avoiding the methodological error of multiplying terminal zero-relist or no-CVSG cuts into the prior.
2. **Deep Doctrinal Engagement with the Sixth Circuit Opinion:** Examined specific pages of the appendix (`App. A14–A31`, `A36–A42`) and explained why each of the petition's five broad questions failed to present a cert-worthy conflict:
   - On procedural/substantive due process, the Sixth Circuit recognized that completed discretionary approvals can create entitlements in principle, but found on this record that further discretionary permits remained under Pontiac's ordinance (`App. A19–A24`).
   - On regulatory takings (`App. A25–A31`), the panel assumed a property interest and evaluated delay, bad faith, causation, and application deficiencies on the summary-judgment record rather than adopting any categorical rule barring delay-based takings claims.
   - On First Amendment retaliation (`App. A38–A42`), the panel assumed a viable constitutional claim and resolved municipal liability under *Monell* because the mayor lacked final zoning authority and the city council never ratified the act.
3. **Calibration:** Adjusted from ~5.0% down to 1.2%, slightly more conservative than `0.005` given the published nature of the Sixth Circuit opinion, though its `big_case_score` of `0.30` was somewhat generous for a routine municipal land-use dispute.

## Predicted Reasoning (`0.88`)

In `predicted_reasoning.md`, `codex-baseline` clearly laid out the expected procedural and substantive trajectory of the petition:
- **Central Claims:** (1) Denial on an order list in November 2026 following the November 6, 2026 conference (`borne-out` — denied November 9, 2026); (2) zero additional distributions beyond the October 14 distribution (`borne-out` — `distribution_count = 1`); (3) no CVSG (`borne-out` — `cvsg_date = null`); and (4) no noted dissent or statement respecting denial (`borne-out` — `noted_dissent_from_denial = false`).
- **Conditional Content:** Its conditional forecast that a grant would narrow review to the fourth question presented (whether deliberate administrative delay in land-use approvals constitutes a compensable taking) and proceed to plenary review rather than summary disposition (`P(summary-disposition route | grant) = 15%`) was well-reasoned and untiggered by the denial.

## Leakage Assessment

- **Mode:** `forward` (prediction placed `2026-10-15T14:51:05Z`, prior to the November 6, 2026 conference and November 9, 2026 resolution).
- **Findings:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. In `retrieval_log.json` (`result_capture_coverage = 0.919`), all local shell commands were captured and inspected only the prompt, schemas, `statpack.md`/`statpack.json`, and the provisioned case record (`find data -name AGENTS.md -not -path 'data/qp-topics/*'` properly excluded `data/qp-topics/`). Three `web-search` calls were `unobserved`, but their logged queries sought only generic Supreme Court Rule 10 text (`site.supremecourt.gov Rule 10 ...`, `2026RulesoftheCourt_WEB.pdf`, and `law.cornell.edu/rules/supct/rule_10`), which `codex-baseline` also candidly disclosed in `retrieval.md`.
