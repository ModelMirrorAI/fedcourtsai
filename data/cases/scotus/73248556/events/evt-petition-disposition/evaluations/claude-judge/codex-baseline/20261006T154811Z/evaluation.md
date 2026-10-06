# Evaluation of codex-baseline — scotus/73248556 evt-petition-disposition

## Outcome and cell

United States v. Hembree, No. 25-1219, a Solicitor General petition from the Fifth Circuit asking the Court to hold the case for United States v. Hemani (No. 24-1234) and then grant, vacate and remand. The petition was distributed once (July 15, 2026, for the September 28 long conference) and **denied on October 5, 2026** on the first order list of OT2026, with no noted dissent and no CVSG (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1, `noted_dissent_from_denial` false). Stage is cert (`event.yaml`).

## Baseline

The prediction froze `band` = `federal` under `salience_version` = `sal-v4`, and the statpack table heading is `(sal-v4)`, so the basis is `risk_set`. Pooling the bracketed `reached` figures for `federal` over the rendered Terms strictly before the case Term (OT2025): OT2017 through OT2024, weighted denominator 181, about 132 weighted grants, pooled rate **0.7295**. The table renders 10 of 10 Terms, so the rendered window is the whole pack and the configured ten-Term lookback is not truncated by rendering; the pack simply holds nothing before OT2017. OT2025 (52.4%, n=21) is the case's own Term and is excluded. Baseline Brier against a denial: (0.7295)^2 = 0.5322.

## Scores

- `correct` = 1: predicted `denied`, outcome `denied`.
- `brier_score` = (0.18 - 0)^2 = 0.0324.
- `brier_skill_score` = 1 - 0.0324 / 0.5322 = 0.9391.
- `reasoning_quality` = 0.70.

## What drove the reasoning grade

The record reading is careful and well documented: the anchor is pooled correctly (federal reached rows OT2017 to OT2024, 132/181, 72.9%, own Term excluded), the rationale explains why neither the whole-table rate nor the terminal relist and CVSG cuts substitute for it, it reads the petition's appendix for what the Fifth Circuit actually relied on, it notices an internal heading error in the appendix and handles it sensibly, and it is scrupulous about provenance (what was verified, what was not, what came from an adversarial filing). The direction of the adjustment is right and the denial call was clear. The grade is held to 0.70 by the substance of the adjustment itself. The rationale discounts the opposition's list of identical denials because they are "not merits precedent", but the question here is cert behaviour, not merits law, and three denials of the same government request on the same issue, one of them after Hemani, are the most direct evidence available of what the Court would do; declining to weight them is why 0.18 sits where it does. The rationale also keeps "substantial GVR probability" on the ground that an intervening opinion can justify reconsideration even if the respondent says it changes nothing, without engaging the point that Hemani went against the petitioner and disclaimed the provision at issue, which makes a GVR "in light of" it an unusual remedy. Its attempts to verify Hemani failed and it says so candidly, which is a point for integrity, though it meant the one check that would have tightened the number was not made.

## Leakage

Forward mode, coverage 0.88. The 26 calls are mostly local reads of the provisioned inputs, prompt, schemas and statpack (collapsed as `other`, this engine's call shape), one CourtListener search for the Hemani opinion that returned metadata and no text, and three unobserved web searches for the Hemani PDF, graded on their queries, which name only the companion case. No retrieved_doc_date, nothing naming this petition's disposition, no qp-topics read, and retrieval.md discloses that no lookup sought this case's outcome. The case was genuinely open at prediction time (September 16, 2026): `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My own read is 0.4 (see `evaluation.json`): a nationally watched doctrinal question carried by a derivative, single-defendant hold-and-GVR petition. The predictor's score was visible in the staged `prediction.json` before this read was recorded; the read rests on the petition, the opposition and the outcome, not on that field. No agreement number is computed here.

## Not scored here

`claim_scores` is the harness's (cert-v claims scored in code). No votes are scored on a cert cell. No semantic set is declared on a cert cell, so no `semantic_grades` block is written. `predicted_reasoning.md` was read for context only and is not graded.
