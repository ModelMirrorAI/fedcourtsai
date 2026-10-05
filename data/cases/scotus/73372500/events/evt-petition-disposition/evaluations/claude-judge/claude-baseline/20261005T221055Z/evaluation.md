# Evaluation of claude-baseline — scotus/73372500, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition (No. 25-1299, Citizens Alliance for Government Integrity v. York County) was distributed once for the September 28, 2026 conference and **denied on October 5, 2026**, with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- `predicted_disposition` = `denied` → `correct` = 1.
- `probability` = 0.006 → `brier_score` = 0.000036.
- `segment_base_rate` = 0.05121 on the `risk_set` basis: the prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, the statpack's band table heading is `sal-v4`, so the bracketed `reached` figures for the baseline band were pooled resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the 2026 row is empty). That is 593 weighted grants over 11,580 weighted resolved. The caption shows 10 of 10 Terms, so the rendered window is the pack's whole window; the configured ten-Term lookback shortens to the same eight Terms. No divergence to flag.
- `brier_skill_score` = 0.986.

## Reasoning quality: 0.90

This is a well-constructed rationale. The anchor is computed correctly: the same eight prior-Term baseline `reached` rows, pooled to roughly 5.1% over 11,580, which matches my own computation to the rounding. The downward adjustments are ranked by weight and each is tied to something in the record. The heaviest, that respondents waived and the Court did not call for a response, is the right one: the Court does not grant a paid petition without first obtaining a response, so any grant path required a post-conference call for a response followed by a grant, and the rationale prices that compound event rather than hand-waving it. The adequate-and-independent-state-ground point is grounded in the specific posture (a discretionary refusal of original jurisdiction under the state court's own Key v. Currie practice) rather than asserted generically. The observation that the petitioner is a neighbor association with no property interest of its own, and so does not fit the owner-versus-government split it describes, is the sharpest point any candidate made and goes directly to whether the question presented could be answered in this vehicle. The fair-presentation problem, the still-live state litigation, and the advocacy signals round it out.

Two things deserve credit beyond the headline. The candidate fetched the September 11 supplemental brief that the snapshot listed but the record did not provision, read it, and concluded it reported only lower-court developments and no intervening decision of this Court, so it could not supply a GVR basis. That is the kind of diligence that would have mattered had the brief said otherwise. And the "why not lower still" section states a floor and a reason for it, which keeps the number from collapsing to zero on vibes.

Minor reservations. "Grant rates are at their lowest" at the long conference is a per-petition observation that is true of the denominator but not an independent signal about this petition. The paid-segment relist-0 and CVSG-none cuts quoted beside the anchor are terminal-state descriptive figures, as the candidate half-acknowledges, and do not add much. Neither affects the soundness of the conclusion.

## Leakage: forward, not applicable

The retrieval log records `mode: forward`. The prediction was created 2026-09-16 against a 2026-09-16 snapshot; the conference was 2026-09-28 and the denial 2026-10-05, so the case was genuinely open and no disposition existed to retrieve. The log (23 calls, coverage 1.0) shows provisioned reads, statpack reads, one corpus query for recent granted dockets that was not about this case, a web fetch of this petition's own supplemental brief (a filing dated 2026-09-11, before resolution), and one web search for a possible hold case whose results included a May 2026 local news item about the filing. No `retrieved_doc_date` on or after resolution, no read under `data/qp-topics/`, and the reasoning states that no disposition surfaced and that the conference was in the future. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My independent read is 0.12: a local permitting dispute brought by a neighborhood group through an unexplained state-court refusal of original jurisdiction, with no amici, no CVSG, and a denial without writing. The circuit disagreement is real but this vehicle could not have reached it. The predictors' `big_case_score` values were visible in the staged `prediction.json` before this read was written down; the read rests on the record and the outcome.

## Not scored here

The `claims` block and `predicted_reasoning.md` were read for context only; the harness scores the claims in code. No `semantic_grades` block is written: this is a cert cell and no semantic set is declared. `vote_accuracy` is omitted on a cert cell.
