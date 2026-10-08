# Evaluation — codex-baseline — Balwani v. United States, No. 25-1330 (scotus/73500238, evt-petition-disposition)

## Outcome and scores

Cert-stage cell. The petition was **denied** on the October 5, 2026 order list following the September 28 long conference: one distribution, no call for a response, no CVSG, no relist, no separate writing (Justice Thomas took no part). `actual_granted` = 0.

- `predicted_disposition` = `denied` → **correct = 1**.
- `probability` = 0.04 → **brier_score = 0.0016**.
- **segment_base_rate = 0.051209** on the **`risk_set`** basis: the prediction froze `band = baseline` under `salience_version = sal-v4`, the statpack's band table is headed sal-v4, so the bracketed `reached` figure is the yardstick. Pooled resolved-weighted over Terms strictly before the case's Term 2025 — Terms 2017–2024, the full prior window the table renders (caption: 10 of 10 Terms, so the rendered window is the pack) — giving 593 weighted grants over 11,580 weighted petitions. Computed from the unrounded `statpack.json` rates the in-code pool reads; the rendered percentages give 0.05120, the same to four places. The in-code 10-Term lookback would reach to 2015, but the pack holds nothing before 2017, so the two pools coincide and there is no window divergence to flag.
- **brier_skill_score = 0.390** (baseline Brier 0.002622).

Vote fields are omitted: cert votes are never scored. `claim_scores`, `process_version`, and `base_rate_salience_version` are the harness's.

## What the prediction got right and wrong

Right: the disposition, the no-CVSG call, the first-conference denial as the modal path, no further distribution, and no writing. The 4% headline was comfortably on the correct side but is the highest of the three candidates on a petition that showed the clearest structural signal against a grant, which is why its skill score is the lowest of the three.

## Reasoning quality — 0.80

Strengths. The information boundary is stated precisely and honestly (forward mode, as-stored snapshot, no BIO because of the waiver, petition facts kept separate from independently checked ones). The anchor is exactly right: the sal-v4 `baseline` bracketed reached rate, pooled over 2017–2024 to 5.12% on n = 11,580, with the terminal ~1% figure explicitly rejected for the right reason. The substantive assessment is the most careful of the three on doctrine: it checked Glossip's majority footnote 10 and Stein through CourtListener, credited the petition's genuine doctrinal hook, and then identified the vehicle problems that in fact mattered — the mix of preserved direct appeals and habeas cases in the claimed split, the panel's assumed-rather-than-decided correction duty, and the petition's own footnote 7 conceding the panel also found the witnesses reliable, which undercuts QP 2's credentials-only premise. It kept conditionals straight (summary route conditional on grant, writing conditional on denial) and did not invent facts.

Weaknesses. It treated the government's waiver with no response call as "a modest negative attention signal" and so stayed at 4%, roughly a 20% haircut from the anchor. The waiver is the dominant signal on this docket: the Court does not, in practice, grant a paid petition on which the respondent has not been heard, so any grant required a call for a response and a redistribution first, and three months of summer had passed with none entered. Correctly weighting that structural point would have moved the number into the low single digits, as the other two candidates did. The 15% relist-increment is also on the high side for a waived, uncalled petition, though the claim is not graded here. These are calibration judgments rather than errors of law, so the mark stays high.

## Leakage

Forward cell. The log (33 calls, capture coverage 0.97) shows the provisioned record, prompt, schemas, and committed statpack being read, two CourtListener authorities (Glossip, Stein) consulted, and one uncaptured hosted web search whose query names Glossip and Rule 702, not this docket. No retrieved document date on or after October 5, 2026, no query for this petition's disposition, no read of `data/qp-topics/`. The reasoning reads the conference as still ahead. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. The decided-case-forward check passes: the prediction's snapshot is dated September 17, 2026, eleven days before the conference.

## Big case

My independent read is 0.40 (see `big_case.notes`): headline-level public attention, mid-sized procedural doctrinal stakes, and a first-conference denial without writing that confirms low institutional salience. Formed before weighing the candidate's own score.
