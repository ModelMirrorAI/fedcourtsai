# Evaluation — gemini-baseline — Balwani v. United States, No. 25-1330 (scotus/73500238, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on the October 5, 2026 order list following the September 28 long conference: one distribution, no call for a response, no CVSG, no relist, no separate writing (Justice Thomas took no part). `actual_granted` = 0.

- `predicted_disposition` = `denied` → **correct = 1**.
- `probability` = 0.01 → **brier_score = 0.0001**.
- **segment_base_rate = 0.051209** on the **`risk_set`** basis: the prediction froze `band = baseline` under `salience_version = sal-v4`, matching the statpack table's heading, so the bracketed `reached` figure is the yardstick. Pooled resolved-weighted over Terms 2017–2024, strictly before the case's Term 2025 and the whole prior window the table renders (caption: 10 of 10 Terms), giving 593 weighted grants over 11,580 weighted petitions, from the unrounded `statpack.json` rates the in-code pool reads (the rendered percentages give 0.05120). The pack holds nothing before 2017, so the configured 10-Term lookback and the rendered window coincide; no divergence to flag.
- **brier_skill_score = 0.962** (baseline Brier 0.002622).

Vote fields are omitted: cert votes are never scored. `claim_scores`, `process_version`, and `base_rate_salience_version` are the harness's.

## What the prediction got right and wrong

Right: everything the docket resolved — denial at the first conference, no response requested, no relist, no CVSG, no writing — and with the sharpest number of the three. Its 1% is also the number that earns the best Brier and skill score here.

## Reasoning quality — 0.55

The score is for the soundness of the analysis, not for landing the number, and the analysis is thin and in one place wrong.

Strengths. It identifies the single most important fact on this docket and draws the right inference from it: the Solicitor General waived, no response has been called for, and the Court rarely grants without first requesting one, which would itself show up as a relist. It correctly says a CVSG is impossible with the United States as respondent, correctly reads the single distribution as a first-conference posture, and correctly predicts denial without writing. That structural chain is the reason the forecast is right and it is stated clearly.

Weaknesses. The anchor is mishandled: it quotes the `baseline` bracketed reached rate "in 2025 is ~3.9%", which is the case's own Term's live slice, the one row the prompt tells a predictor not to pool (the leakage-safe cut is Terms strictly before the case's). On a forward cell this is not leakage, but it is the wrong population and reads as not having applied the rule; the correct pooled anchor is about 5.1%. It also cites the terminal 0-relist figure (1.2%) as a second anchor without noting that terminal figures condition on the petition never advancing. Beyond the waiver point, the substantive assessment is asserted rather than shown: the claims that the issues are "fact-bound," that the Ninth Circuit "applied settled law," and that the petition "does not clearly establish a split" are all true-ish but rest on a read of the questions presented and the first fifty lines of the petition (the log shows no further reading, no retrieval, and no engagement with the Glossip hook the petition leans on, the preservation posture, or the harmless-error ground on QP 2). The whole rationale runs about 250 words with no conditionals spelled out and no stated uncertainties. A sound forecast reached mostly on one correct structural intuition and a thin reading of the record.

## Leakage

Forward cell. The log (22 calls) has capture coverage 0.0: every row is `unobserved`, the engine's standing shape, so each call is graded on its query. The queries are provisioned-record reads (snapshot, context, event, questions presented, the head of the petition), statpack greps, the prediction schema, a `grep -r Balwani` confined to the record directory, and the output writes. No web search, no CourtListener call, no corpus query, no read of `data/qp-topics/`, no query naming this petition's disposition. The reasoning treats the September 28 conference as upcoming. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. The decided-case-forward check passes: the prediction's snapshot is dated September 17, 2026. The candidate's own `retrieval.md` says no retrieval beyond the provisioned inputs and the statpack, which the log corroborates; its `flags.json` is not staged, so that absence carries no weight either way.

## Big case

My independent read is 0.40 (see `big_case.notes`): headline-level public attention, mid-sized procedural doctrinal stakes, and a first-conference denial without writing that confirms low institutional salience. Formed before weighing the candidate's own score.
