# Evaluation: gemini-baseline — Majestic Realty Co. v. Salazar, No. 25-1322 (evt-petition-disposition)

## Outcome and scores

The event is a **cert** cell (`event.yaml` stage `cert`). The petition was **denied** on the October 5, 2026 order list after a single distribution for the September 28 long conference, with no relist, no CVSG, and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`, `noted_dissent_from_denial: false`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.03 − 0)² = **0.0009**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading. Pooled bracketed `reached` figure for `baseline`, resolved-weighted over the rendered Terms strictly before OT2025 (OT2017–OT2024; n = 11,580): 0.0512. The caption renders 10 of 10 Terms, so the rendered window is the pack's whole window and the in-code 10-Term lookback pools the same eight rows. No window divergence to flag.
- `brier_skill_score` = 1 − 0.0009 / 0.0512² = **+0.66**. The best Brier and the only positive skill on this cell.

Votes are not scored on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.40

**What it got right.** The candidate located the right anchor ("the statpack's `baseline` bracketed `reached` rate for the prior Terms (2017-2024) is roughly 4-6%"), correctly read the docket state (one distribution for the long conference, no relist, no CVSG), correctly judged that the federal government has no interest here, and named Justices Thomas and Alito as the plausible authors of any dissent from denial. The headline number was close to the realized outcome.

**Where it fell short.** `reasoning_quality` grades the soundness of the analysis, not the number, and this rationale is a single paragraph that does not engage the case. The move from a 4–6% anchor to 0.03 — below the band rate — rests on one argument: petitions rarely get granted off a first distribution at the long conference, and "if the Court is interested, it will relist it." That is true but is already inside the bracketed reached rate, which is the grant rate of every private paid petition that reached a first distribution; the first-distribution vantage point is the population the anchor describes, not a reason to go below it. A case-specific reason to undershoot the anchor existed — the interlocutory state-court posture, the absence of any split on the federal question, and Cedar Point's and Moody's express preservation of PruneYard — but the rationale names none of them (the forecast document mentions only that "the vehicle is from a state court"). "It has zero relists right now" is uninformative before the conference has met. There is no indication the candidate read the brief in opposition or the petition beyond the questions presented, and the retrieval log shows it read only the questions-presented file among the documents. The candidate's number was right for reasons it did not state.

**Net.** Correct direction, correct anchor, a defensible heuristic, but thin: no vehicle analysis, no doctrinal analysis, and the one argument offered for undershooting the anchor double-counts what the anchor already conditions on. The forecast document was read for context only and is not scored.

## Leakage

`mode: forward` per the staged retrieval log. The prediction was created 2026-09-17, before the conference. Every call in the log is `unobserved` (`result_capture_coverage` 0.0), which is this engine's standing telemetry shape, so each call is graded on its query: all 27 are local reads of the provisioned record, the prompt, schemas and the statpack, plus output writes and `validate`. No web, MCP or corpus call; no query names this docket's disposition; no `data/qp-topics/` read; no `retrieved_doc_date` anywhere. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. Not a mis-provisioned forward cell.

## Big case

My own read is 0.5 (see `evaluation.json`). I note for the record that I saw the candidates' `big_case_score` values while reading the staged `prediction.json` files before I had written my read down; my number is formed from the record and the outcome and I did not adjust it toward theirs.
