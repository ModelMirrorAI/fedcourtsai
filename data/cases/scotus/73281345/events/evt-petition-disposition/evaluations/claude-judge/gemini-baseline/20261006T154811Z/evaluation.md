# Evaluation — gemini-baseline

**Cell.** Cert stage (`event.yaml` stage `cert`, moment `distribution`), Holly Ann Elkins v. United States, No. 25-1061, Term 2025. Outcome: petition **denied** on 2026-10-05 after two distributions, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0). The candidate's prediction ran forward on the 2026-09-17 snapshot.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0025 | (0.05 − 0)² |
| `segment_base_rate` | 0.1722 | elevated band, bracketed `reached` figure, pooled resolved-weighted over Terms 2017–2024 |
| `base_rate_basis` | `risk_set` | frozen `context.band` `elevated` with `context.salience_version` `sal-v4`; the statpack table heading names `sal-v4` |
| `brier_skill_score` | 0.916 | 1 − 0.0025 / (0.1722 − 0)² |
| `reasoning_quality` | 0.58 | see below |

**Base rate detail.** The prediction's frozen context carries both a band (`elevated`) and a salience version (`sal-v4`), and the committed `metrics/statpack.md` "Segment base rate by salience band (sal-v4)" table matches that version, so the risk-set basis applies. The table renders all 10 Terms the pack holds (2017–2026); the Terms strictly before 2025 are 2017–2024, eight rows. Pooling the bracketed `reached` elevated figures by their `n` (from `statpack.json`'s `prefix_est_grant_rate` × `prefix_weighted_resolved`): 484 / 2810 = 0.17224. The shipped in-code lookback is 10 Terms, which would reach back to 2015, but the pack holds nothing before 2017, so the pack-bounded window and the rendered window coincide and no divergence needs flagging. Vote fields are omitted: a cert cell's votes are never scored.

## What the prediction got right and wrong

The candidate called the denial at 5%, the lowest of the three, and the petition was denied without a relist or a writing. Its procedural calls (no further relist, no CVSG, silence the most probable outcome on denial) matched. The lowest probability earns the best Brier and skill on this cell, but the skill score is a fact about the number, not about the reasoning behind it, and the reasoning is graded separately below. The forecast document and the claims block are not scored here.

## Reasoning quality (0.58)

The rationale is a single paragraph. What it says is sound in direction; what holds the grade down is how little of the record it rests on.

Strengths:

- **Right anchor in the right neighbourhood.** It names the prior-Term elevated rate as about 18%. The pooled figure is 17.2%, so this is a loose read (the 2024 row alone is 17.9%) rather than the pooled arithmetic, but it is the correct table and the correct direction of adjustment.
- **Identified the two decisive points in the brief in opposition.** The alternative instrumentalities on the record (internet, GPS) as a vehicle defect, and the confinement of *Chavarria* to motor vehicles as undercutting the split. Both are the government's strongest arguments and both held up.
- **Correct structural calls.** CVSG at zero because the United States is the respondent; relist discounted because the defect is easy to spot at the first fully briefed conference.

Weaknesses:

- **The evidence base is thin.** The retrieval log shows the questions presented, the snapshot, the statpack, and a `grep` for "vehicle" in the brief in opposition. There is no sign the petition was read, and the rationale does not engage with the petitioner's framing, the amicus, or the petition's answer to the alternative-grounds point. The analysis is the government's brief restated, not an independent weighing.
- **"Clean question" is asserted, then contradicted.** The paragraph opens by calling the question clean and closes by calling the vehicle fatal, without reconciling the two or saying which the Court is likelier to see first.
- **No comparables and no stated limits.** It does not use the recent *Smith* and *Stackhouse* denials the brief cites, does not note that the reply was unprovisioned, and gives no sense of where the forecast could be wrong.
- **The relist reasoning is a sentence**, and the response-request-versus-relist distinction that the other context in the record supports is only implicit in the forecast document, not in the rationale.

The number landed well, but the rationale would have supported anything from 3% to 10% equally; it does not show the work that would make 5% rather than 8% the defensible call.

## Leakage

`mode` `forward`; `retrieved_outcome_material` `false`; `influenced_prediction` `not_applicable`; `leakage_suspected` `false`. The prediction was created 2026-09-17 and the event resolved 2026-10-05, so the case was genuinely open. The log's 28 calls are all `unobserved` (capture coverage 0.0), which is this engine's standing shape rather than a defect, so every call is graded on its query: prompt, schema, snapshot and provisioned-document reads, a statpack read, a `grep` of the brief in opposition, and two `fedcourts query` calls (a topic query for "instrumentality of interstate commerce" and a 2020s era pull with `--full` and a limit of 5). No query names this petition's disposition, no `retrieved_doc_date` is legible on any call, no read under `data/qp-topics/`. Because no results were captured, the absence of outcome material in the log is weaker evidence than on a captured log; the forward mode and the pre-resolution creation date are what carry the `not_applicable` grade. No sign of a decided case provisioned forward.

## Big case

My own read is 0.3: a genuine Commerce Clause question with doctrinal reach across facility-of-interstate-commerce statutes, but a one-decision, non-telephone conflict, alternative jurisdictional hooks on the record, a private criminal petitioner, and a denial without any noted writing. Public stakes are low. The staged `prediction.json` carries the predictor's `big_case_score`, so that number was visible when I read the file; my read above rests on the substance of the record and the outcome, not on it.

## Semantic grades

None. This is a cert cell; no semantic set is declared and no opinion slot is staged.
