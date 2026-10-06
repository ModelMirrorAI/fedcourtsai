# Evaluation of gemini-baseline — scotus/73281632, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition (No. 25-1144, Daisey Trust v. FHFA) was **denied** on 2026-10-05 at the long conference, with no relist and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `noted_dissent_from_denial: false`, `distribution_count: 2`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.03 − 0)² = **0.0009**.
- `segment_base_rate` = **0.1724** on the `risk_set` basis. The prediction's frozen context carries `band: elevated` with `salience_version: sal-v4`, matching the statpack table heading, so the bracketed `reached` figures apply. Pooled resolved-weighted over the eight rendered Terms strictly before Term 2025 (2017–2024; the caption renders 10 of 10 Terms, so the rendered window is the pack's): 484.4 / 2810 ≈ 0.1724.
- `brier_skill_score` = 1 − 0.0009 / 0.1724² = **0.970**.
- No `vote_accuracy`, no `semantic_grades` (cert cell). `claim_scores` is the harness's.

## Reasoning quality: 0.62

What drove the score. The rationale reaches the right conclusion on the right grounds: no circuit split; the Ninth Circuit applied two very recent controlling decisions (CFSA, Consumers' Research); the petition's argument rests on dissents; and the BIO's standing and claim-preclusion objections make the vehicle poor. It reads the response request after the SG's waiver as the attention signal it is, and attributes it plausibly to Justices who dissented in the funding cases. It correctly reads the second distribution as a re-set rather than a relist. The number it lands on was the best calibrated of the three, but the score here grades the soundness of the analysis, not the result.

Deductions, which are substantial. The rationale is three short paragraphs and does not engage the petition's actual distinguishing argument (that CFSA's reasoning leaned on the CFPB funding cap, which FHFA's statute lacks), so the reader cannot tell whether the predictor judged that argument weak or never weighed it. It quotes the band rate as "around 15-18%" rather than pooling the table, which is adequate for direction but not for the anchor-and-adjust structure the cell asks for. It presents the BIO's standing argument as "strong" without noting that the panel expressly upheld standing, so the vehicle discussion takes the respondent's side without saying so. It does not mention the absence of amici, the petitioner class, or the unanimous published panel, which the other candidates used. The forecast is sound but thin, and its stated reasons underdetermine the size of the discount from the band rate to 3%.

## Leakage

Forward cell. Every marker in the log is `unobserved` (capture coverage 0.0), an engine's standing shape, so each call is graded on its query: provisioned reads, one corpus query with topical terms (Appropriations Clause, funding mechanism, FHFA), one CourtListener opinion search on FHFA and the Appropriations Clause, and the write-out. No query names this docket's disposition or reaches past the event date; no `data/qp-topics/` read. Nothing was credited as having returned empty. The reasoning cites nothing post-dating the snapshot. `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent read is 0.3 (see `big_case.notes`). The staged `prediction.json` carries the predictor's `big_case_score`, so I had seen it before writing; my read rests on the questions presented, the docket, and the outcome.
