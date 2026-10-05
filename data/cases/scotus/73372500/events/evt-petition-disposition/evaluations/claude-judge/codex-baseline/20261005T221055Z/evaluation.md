# Evaluation of codex-baseline — scotus/73372500, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition (No. 25-1299, Citizens Alliance for Government Integrity v. York County) was distributed once for the September 28, 2026 conference and **denied on October 5, 2026**, with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- `predicted_disposition` = `denied` → `correct` = 1.
- `probability` = 0.025 → `brier_score` = 0.000625.
- `segment_base_rate` = 0.05121 on the `risk_set` basis: the prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, the statpack's band table heading is `sal-v4`, so the bracketed `reached` figures for the baseline band were pooled resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the 2026 row is empty). That is 593 weighted grants over 11,580 weighted resolved. The caption shows 10 of 10 Terms, so the rendered window is the pack's whole window; the configured ten-Term lookback shortens to the same eight Terms. No divergence to flag.
- `brier_skill_score` = 0.762.

## Reasoning quality: 0.80

A careful and candid rationale. The anchor is computed correctly (the same eight prior-Term baseline `reached` rows, about 5.12% over 11,580) and the candidate is explicit that it is an approximation from displayed figures and that it excluded the 2025 and 2026 rows. It correctly declines to use a Fourth Circuit originating-court rate for a petition from a state supreme court, and correctly declines to treat the context's null auxiliary fields as findings. The vehicle analysis covers the right ground: an unpublished refusal of original jurisdiction that selected no federal standard, the independent-state-ground and suitability objections the petition itself recounts, the preservation concession at page 21, the mismatch between a neighbor association and the permit-holder plaintiffs in the asserted split, and the contested state-law predicate. The candidate also verified Philadelphia Newspapers v. Jerome through CourtListener rather than taking the petition's word for what it holds, and correctly limited what it supports.

Where it is weaker than the best rationale here. The discount from the anchor is only to half, and the stated reason, "preserving meaningful nonzero mass for narrow summary relief," gives the clarification-vacatur route more weight than the record supports. The rationale notes the waiver and the absence of a call for a response but treats that as "no affirmative sign" rather than as the structural fact it is: the Court does not grant, or vacate and remand, on a paid petition without first obtaining a response, so every grant route ran through a post-conference call for a response that the rationale never prices. The candidate also chose not to retrieve the docketed supplemental brief and said so, which is honest but left a provisioned-snapshot signal unexamined when a forward cell could have read it. Given the outcome, 2.5% was a defensible conservative shading rather than a mistake, and the document is explicit about every limitation it carried.

## Leakage: forward, not applicable

The retrieval log records `mode: forward`. The prediction was created 2026-09-16 against a 2026-09-16 snapshot; the conference was 2026-09-28 and the denial 2026-10-05, so the case was genuinely open and no disposition existed to retrieve. The log (28 calls, coverage 0.93) shows provisioned reads, statpack reads, two unobserved web searches and three CourtListener calls, all aimed at the 1978 Philadelphia Newspapers opinion and never at this petition; one file find explicitly excluded `data/qp-topics/`. No `retrieved_doc_date` on or after resolution, and the reasoning states that it sought no disposition or subsequent history of this petition. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My independent read is 0.12: a local permitting dispute brought by a neighborhood group through an unexplained state-court refusal of original jurisdiction, with no amici, no CVSG, and a denial without writing. The circuit disagreement is real but this vehicle could not have reached it. The predictors' `big_case_score` values were visible in the staged `prediction.json` before this read was written down; the read rests on the record and the outcome.

## Not scored here

The `claims` block and `predicted_reasoning.md` were read for context only; the harness scores the claims in code. No `semantic_grades` block is written: this is a cert cell and no semantic set is declared. `vote_accuracy` is omitted on a cert cell.
