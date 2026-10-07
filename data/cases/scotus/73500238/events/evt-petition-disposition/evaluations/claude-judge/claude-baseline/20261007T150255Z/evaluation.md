# Evaluation — claude-baseline — Balwani v. United States, No. 25-1330 (scotus/73500238, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on the October 5, 2026 order list following the September 28 long conference: one distribution, no call for a response, no CVSG, no relist, no separate writing (Justice Thomas took no part). `actual_granted` = 0.

- `predicted_disposition` = `denied` → **correct = 1**.
- `probability` = 0.02 → **brier_score = 0.0004**.
- **segment_base_rate = 0.051209** on the **`risk_set`** basis: the prediction froze `band = baseline` under `salience_version = sal-v4`, matching the statpack table's heading, so the bracketed `reached` figure is the yardstick. Pooled resolved-weighted over Terms 2017–2024, strictly before the case's Term 2025 and the whole prior window the table renders (caption: 10 of 10 Terms), giving 593 weighted grants over 11,580 weighted petitions, from the unrounded `statpack.json` rates the in-code pool reads (the rendered percentages give 0.05120). The pack holds nothing before 2017, so the configured 10-Term lookback and the rendered window coincide; no divergence to flag.
- **brier_skill_score = 0.847** (baseline Brier 0.002622).

Vote fields are omitted: cert votes are never scored. `claim_scores`, `process_version`, and `base_rate_salience_version` are the harness's.

## What the prediction got right and wrong

Right: every observable the docket resolved — denial on the order list after the long conference, no call for a response, no further distribution, no CVSG, no separate writing — and the forecast document said in advance that a call for a response would be the signal the forecast was wrong, which is exactly the right falsifier. The 2% sits between the other two candidates; a point lower would have been justified by its own argument, but the number is well calibrated to the stated decomposition.

## Reasoning quality — 0.92

Strengths. The anchor is exactly right and correctly justified: the sal-v4 `baseline` bracketed reached rate pooled over 2017–2024 (about 5.1% on n = 11,580), with the terminal relist-0 and terminal-band figures named and set aside for the right reason. The dominant adjustment is the one that actually decided this docket, and it is argued structurally rather than asserted: the government waived eight days before distribution, the summer window in which chambers call for a response on a waived petition passed with no call, and a grant therefore required a call, a brief in opposition, and a redistribution, each individually unlikely. The substantive assessment is grounded in the Ninth Circuit's amended opinion read through CourtListener rather than in the petition's description of it: the panel applied plain error because the Napue claim was not raised as such at trial, assumed without deciding that a correction duty existed, said the record was unclear whether the testimony was more than a mistaken recollection, and found no effect on substantial rights; QP 2 was decided on harmlessness and the word "gatekeep" does not appear; no judge requested an en banc vote; a unanimous, ideologically mixed panel. Each of those is a real reason a Court interested in the question would wait for a cleaner vehicle, and the Glossip reliance is correctly characterized as a confessed violation on state postconviction review rather than a preservation ruling. The 2% is decomposed transparently (about 8% chance of a post-conference call, about 20% conditional on it, plus a small residual) and the uncertainties section is candid about what it could not check (a Holmes companion petition; the corpus `response_filed_at` field being null on every granted prior, so the waiver effect could not be measured). Conditionals are kept straight throughout.

Weaknesses. "The Court cannot grant a petition on which the respondent has not been heard" is stated as a rule in the forecast document; it is a near-universal practice rather than a formal bar, and the rationale elsewhere treats it as a practice, so this is a wording slip rather than a legal error. The four corpus queries characterized the corpus's shape without surfacing a close prior, as the candidate itself notes, so the corpus work added little beyond confirming a limitation. Minor points against an otherwise exemplary rationale.

## Leakage

Forward cell. The log (36 calls, capture coverage 1.0, no throttling) shows the provisioned record, prompt, schemas, and statpack read; four `fedcourts query` calls over 2020s granted and denied priors (latest retrieved document date 2025-02-11); three CourtListener searches, two for a Holmes companion petition on the SCOTUS docket index (0 results) and one that located the Ninth Circuit's amended opinion in United States v. Holmes; then the cluster, opinion list, first chunk, and four in-document searches of that opinion (dated 2025-12-22). The latest retrieved document date is 2025-12-22, well before the October 5, 2026 denial. No query names this petition's disposition, no read of `data/qp-topics/`. The candidate discloses in both prose documents and `retrieval.md` that nothing retrieved touched the disposition, and the log corroborates it. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. The decided-case-forward check passes: the prediction's snapshot is dated September 17, 2026, before the conference.

## Big case

My independent read is 0.40 (see `big_case.notes`): headline-level public attention, mid-sized procedural doctrinal stakes, and a first-conference denial without writing that confirms low institutional salience. Formed before weighing the candidate's own score.
