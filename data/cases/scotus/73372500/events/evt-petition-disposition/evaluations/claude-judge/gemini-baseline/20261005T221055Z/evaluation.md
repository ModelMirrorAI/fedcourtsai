# Evaluation of gemini-baseline — scotus/73372500, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition (No. 25-1299, Citizens Alliance for Government Integrity v. York County) was distributed once for the September 28, 2026 conference and **denied on October 5, 2026**, with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- `predicted_disposition` = `denied` → `correct` = 1.
- `probability` = 0.005 → `brier_score` = 0.000025.
- `segment_base_rate` = 0.05121 on the `risk_set` basis: the prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, the statpack's band table heading is `sal-v4`, so the bracketed `reached` figures for the baseline band were pooled resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the 2026 row is empty). That is 593 weighted grants over 11,580 weighted resolved. The caption shows 10 of 10 Terms, so the rendered window is the pack's whole window; the configured ten-Term lookback (2015–2024) reaches two Terms the pack does not hold and so shortens to the same eight Terms. No divergence to flag.
- `brier_skill_score` = 0.990.

## Reasoning quality: 0.62

What is right. The rationale names the two features that actually decided this petition: an unexplained one-page state-court order that the petition itself concedes may rest on an adequate and independent state ground, and respondents' waiver with no call for a response. It identifies substantive due process in local zoning as a disfavored area and predicts a swift first-conference denial, which is exactly what happened. It discloses that it read the petition text to confirm the vehicle problem.

What holds it back. The analysis is thin for the size of the adjustment it makes. It drops from a roughly 5% band anchor to 0.5% on two sentences, and the anchor itself is stated as a range of 3.9% to 5.7% that includes the 2025 row, the case's own Term, rather than pooling the strictly-prior Terms the statpack caption and the predict contract call for. It does not engage with the September 11 supplemental brief that was on the provisioned snapshot, does not consider whether the petitioner (a neighbor association, not a permit holder) even fits the split it invokes, and does not address the fair-presentation problem the petition itself flags. The reading of waiver as the respondents' "confidence" is a fair inference but is asserted rather than connected to the Court's practice of calling for a response before any grant. The number was well placed, but the document supplies less of the reasoning that justifies it than the other candidates did.

## Leakage: forward, not applicable

The retrieval log records `mode: forward`. The prediction was created 2026-09-16 against a 2026-09-16 snapshot; the conference was 2026-09-28 and the denial 2026-10-05, so the case was genuinely open and no disposition existed to retrieve. Every call in the log is `unobserved` (coverage 0.0), so each was graded on its query: provisioned reads, statpack greps, petition greps, and two CourtListener searches on the case caption, all timestamped 2026-09-16. No `retrieved_doc_date` on or after resolution, no read under `data/qp-topics/`, and the reasoning cites nothing later than the snapshot. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The candidate's `flags.json` is not staged, so its absence here proves nothing either way.

## Big case

My independent read is 0.12: a local permitting dispute brought by a neighborhood group through an unexplained state-court refusal of original jurisdiction, with no amici, no CVSG, and a denial without writing. The circuit disagreement is real but this vehicle could not have reached it. The predictors' `big_case_score` values were visible in the staged `prediction.json` before this read was written down; the read rests on the record and the outcome.

## Not scored here

The `claims` block and `predicted_reasoning.md` were read for context only; the harness scores the claims in code. No `semantic_grades` block is written: this is a cert cell and no semantic set is declared. `vote_accuracy` is omitted on a cert cell.
