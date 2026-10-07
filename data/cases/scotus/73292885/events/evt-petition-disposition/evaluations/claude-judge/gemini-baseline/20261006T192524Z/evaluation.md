# Evaluation of gemini-baseline — scotus/73292885, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`), forward mode. Pestarino v. Pestarino, No. 25-1249: a paid, pro se petition from an unpublished Washington Court of Appeals decision affirming a civil protection order; distributed once (June 17, 2026) for the September 28, 2026 long conference. Outcome: **denied** on October 5, 2026, `actual_granted` 0, no noted dissent, one distribution. No opinion slot is staged, as expected on a cert cell.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.01 − 0)² = **0.0001**.
- `segment_base_rate` = **0.0512**, `base_rate_basis` = `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack table heading names sal-v4, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024, eight rows; the caption renders 10 of 10 Terms, so the rendered window is the pack's window and no lookback divergence arises): 593.0 / 11,580 = 5.12%.
- `brier_skill_score` = 1 − 0.0001 / 0.0512² = **0.962**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted/null — cert cell; no semantic set is declared and the prediction carries no `semantic_claims` block.

## Reasoning quality: 0.60

What the rationale gets right: it identifies the frozen baseline band and cites the prior-Term reached rate as its anchor ("approximately 5–6%", which brackets the correct pooled 5.1%); it adjusts downward for the right reasons (pro se, fact-bound family-court grievance, poor vehicle for any Rahimi follow-on); it discloses that the brief in opposition had no extracted text and does not invent its contents; and its retrieval note candidly reports that the CourtListener docket lookup returned a mismatched caption (which I reproduced — see `flags.json`).

What holds the score down: the anchor is quoted as a range rather than pooled from the table, so the reader cannot check the self-selected window; the analysis is a single paragraph that names no record specifics beyond the band and the distribution (no mention of the unpublished opinion below, the state supreme court's denial of review, the absence of any alleged conflict, or the omnibus shape of the question presented); and the Rahimi point is asserted rather than tied to what Rahimi actually left open. The number is well calibrated to the realized outcome and to the stronger candidates' numbers, but the document supporting it is thin, so a reader could not tell a sound 1% from a lucky one from this text alone.

## Leakage

Forward cell, `leakage.influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false. Prediction created 2026-09-16; the conference was 2026-09-28 and the denial 2026-10-05, so no outcome existed to leak. Log mode is `forward`; all 28 calls are `unobserved` (coverage 0.0, this engine's standing shape), so each was graded on its query: the only case-directed calls are a CourtListener name search and two docket-metadata fetches on 2026-09-16, which could not have returned a disposition. No `retrieved_doc_date` anywhere; no `data/qp-topics/` read. Reasoning reads one distribution and a pending conference off the snapshot, not an outcome. No sign of a decided case provisioned forward.

## Big case

My independent read, formed from the record and the outcome: **0.05**. Nominally sweeping question presented, but a pro se private family dispute on an unpublished state opinion, denied silently with no writing. (Formed before weighing the predictor's own score; the panel's rank-agreement is computed elsewhere.)
