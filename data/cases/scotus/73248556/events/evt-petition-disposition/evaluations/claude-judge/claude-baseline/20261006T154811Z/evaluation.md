# Evaluation of claude-baseline — scotus/73248556 evt-petition-disposition

## Outcome and cell

United States v. Hembree, No. 25-1219, a Solicitor General petition from the Fifth Circuit asking the Court to hold the case for United States v. Hemani (No. 24-1234) and then grant, vacate and remand. The petition was distributed once (July 15, 2026, for the September 28 long conference) and **denied on October 5, 2026** on the first order list of OT2026, with no noted dissent and no CVSG (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1, `noted_dissent_from_denial` false). Stage is cert (`event.yaml`).

## Baseline

The prediction froze `band` = `federal` under `salience_version` = `sal-v4`, and the statpack table heading is `(sal-v4)`, so the basis is `risk_set`. Pooling the bracketed `reached` figures for `federal` over the rendered Terms strictly before the case Term (OT2025): OT2017 through OT2024, weighted denominator 181, about 132 weighted grants, pooled rate **0.7295**. The table renders 10 of 10 Terms, so the rendered window is the whole pack and the configured ten-Term lookback is not truncated by rendering; the pack simply holds nothing before OT2017. OT2025 (52.4%, n=21) is the case's own Term and is excluded. Baseline Brier against a denial: (0.7295)^2 = 0.5322.

## Scores

- `correct` = 1: predicted `denied`, outcome `denied`.
- `brier_score` = (0.07 - 0)^2 = 0.0049.
- `brier_skill_score` = 1 - 0.0049 / 0.5322 = 0.9908.
- `reasoning_quality` = 0.90.

## What drove the reasoning grade

This is the most complete analysis of the three. It pools the band anchor correctly (federal reached rows OT2017 to OT2024, n=181, about 73%, own Term excluded), states why the anchor's population does not describe this petition (the federal rate is carried by SG petitions seeking plenary review or a GVR after a government win, and this is neither), and then independently verifies the two facts the adjustment rests on rather than taking the opposition's word: the Hemani holding and lineup, and the full docket histories of Mitchell, Doucet and Cockerham. The Mitchell comparison is the decisive piece and the rationale recognises it as such: an identical hold-for-Hemani request, held through Hemani, then denied without a GVR. The residual 7% is decomposed into named paths with rough weights, cross-checked against the relist, circuit and CVSG cuts, and the uncertainties section says where the number could be wrong. The outcome bore all of it out, including the ancillary expectations of no relist and no separate writing. Minor deductions: the 7% residual is a little generous given the Mitchell precedent the rationale itself leans on, and the rationale admits it read only excerpts of Hemani, which it correctly discloses.

## Leakage

Forward mode, coverage 1.0, so every call's result was captured. The 45 calls include six web searches, twelve fetches, eight CourtListener MCP calls (five throttled) and two `fedcourts query` runs. Every external lookup concerns the companion Hemani decision or the three comparator dockets; the only legible document dates are 2025-07-24 and 2026-02-06, both well before the October 5, 2026 resolution. One search surfaced this petition's own supremecourt.gov filing and a CRS sidebar describing it as pending, which is ordinary forward signal rather than outcome material, and the candidate's retrieval.md discloses it. No qp-topics read. The case was genuinely open at prediction time (September 16, 2026): `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My own read is 0.4 (see `evaluation.json`): a nationally watched doctrinal question carried by a derivative, single-defendant hold-and-GVR petition. The predictor's score was visible in the staged `prediction.json` before this read was recorded; the read rests on the petition, the opposition and the outcome, not on that field. No agreement number is computed here.

## Not scored here

`claim_scores` is the harness's (cert-v claims scored in code). No votes are scored on a cert cell. No semantic set is declared on a cert cell, so no `semantic_grades` block is written. `predicted_reasoning.md` was read for context only and is not graded.
