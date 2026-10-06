# Evaluation of codex-baseline — scotus/73281632, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition (No. 25-1144, Daisey Trust v. FHFA) was **denied** on 2026-10-05 at the long conference, with no relist and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `noted_dissent_from_denial: false`, `distribution_count: 2`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.07 − 0)² = **0.0049**.
- `segment_base_rate` = **0.1724** on the `risk_set` basis. The prediction's frozen context carries `band: elevated` with `salience_version: sal-v4`, and the statpack's band table heading is sal-v4, so the bracketed `reached` figures apply. Pooled resolved-weighted over the eight rendered Terms strictly before the case's Term 2025 (2017–2024; the caption renders 10 of 10 Terms, so the rendered window is the pack's): 484.4 / 2810 ≈ 0.1724. This matches the predictor's own anchor.
- `brier_skill_score` = 1 − 0.0049 / 0.1724² = **0.835**.
- No `vote_accuracy`, no `semantic_grades` (cert cell). `claim_scores` is the harness's.

## Reasoning quality: 0.84

What drove the score. The rationale is sound and well-disciplined. It anchors on the correct frozen band and version, pools the right Terms, and states that the pooled figure is a weighting of rounded rates. It reads the petition's actual cert argument (that CFSA's reasoning leaned on the CFPB cap, leaving room to distinguish FHFA) rather than caricaturing it, and then answers it with the majority reasoning of CFSA (source and purpose suffice) and Consumers' Research (qualitative limits suffice), both confirmed against the opinion text rather than recalled. It correctly reads the second distribution as the re-set after the response request rather than a relist, which is exactly what happened. It treats the BIO's vehicle points (standing, claim preclusion, preservation of QP 2) as contested arguments, noting the panel upheld standing, and still counts them as reasons the Court would wait for a cleaner vehicle. The discount from 17% to 7% is explained and proportionate.

Deductions. The discussion is somewhat abstract about why the response request after an SG waiver did not move the number more (it was the only affirmative attention signal, and the rationale mentions it but does not weigh it against the base rate for response-requested petitions, which it rightly admits the pack does not give). It also did not read the reply brief, which it discloses. Neither affected the direction.

## Leakage

Forward cell. The log shows reads of provisioned inputs, four CourtListener calls on the two controlling precedents (both pre-dating the judgment below), and three unobserved web searches aimed at general precedent pages, none naming this docket. No document dated on or after the resolution, no query for this petition's disposition, no `data/qp-topics/` read. `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent read is 0.3 (see `big_case.notes`): institutionally interesting if granted, but a question the Court had settled in the previous two Terms, with no amicus support and a denial at the first substantive conference without writing. I note that the staged `prediction.json` carries the predictor's `big_case_score`, so I had seen it before writing my read; the read is formed from the questions presented, the docket, and the outcome, not from that number.
