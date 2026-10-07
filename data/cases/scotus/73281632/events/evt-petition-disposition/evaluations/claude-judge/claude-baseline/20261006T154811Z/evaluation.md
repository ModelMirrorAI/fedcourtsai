# Evaluation of claude-baseline — scotus/73281632, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition (No. 25-1144, Daisey Trust v. FHFA) was **denied** on 2026-10-05 at the long conference, with no relist and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `noted_dissent_from_denial: false`, `distribution_count: 2`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.07 − 0)² = **0.0049**.
- `segment_base_rate` = **0.1724** on the `risk_set` basis. The prediction's frozen context carries `band: elevated` with `salience_version: sal-v4`, matching the statpack table heading, so the bracketed `reached` figures apply. Pooled resolved-weighted over the eight rendered Terms strictly before Term 2025 (2017–2024; the caption renders 10 of 10 Terms, so the rendered window is the pack's): 484.4 / 2810 ≈ 0.1724. The predictor computed the same number.
- `brier_skill_score` = 1 − 0.0049 / 0.1724² = **0.835**.
- No `vote_accuracy`, no `semantic_grades` (cert cell). `claim_scores` is the harness's.

## Reasoning quality: 0.88

What drove the score. This is the most complete rationale of the three. It names the anchor correctly and states what it is (grant family, denial-reweighted, risk-set). It then ranks its adjustments by weight and gives each a concrete basis: the BIO's point that CFSA holds source and purpose sufficient, and Consumers' Research's rejection of a numeric-cap requirement, with the honest observation that the petition's "conflict" is assembled from descriptive passages and dissents; the absence of any split and of any other circuit's decision, which it checked rather than assumed (an opinion search on FHFA and the Appropriations Clause found only the decision below, and two SCOTUS docket searches found no companion petition); the three preserved vehicle objections; and the petitioner-class and attention signals (HOA-sale investor trusts, no repeat Supreme Court counsel, zero amici, unanimous published panel). It weighs the one positive signal, the response request after waiver, explicitly and explains why it keeps the number above the relist-0 floor rather than near the band rate. It correctly reads the two distributions as one displaced setting plus one real one. The uncertainties section is candid and specific (reply brief unread, no conditional cut for response-requested petitions, the corpus query uninformative).

Deductions. Minor. The claim that "at most three Justices have shown sympathy for the cap theory" is a reasonable inference from the two dissents but stated more firmly than the record supports. The read of the panel opinion stopped at the background sections, which it discloses. None of this bears on the direction or size of the call.

## Leakage

Forward cell, capture coverage 1.0. Beyond provisioned reads, one corpus query (recent grants, no topical overlap, disclosed as uninformative) and five CourtListener calls. One SCOTUS docket search named Haddad and FHFA with a filed-after-2025 filter and returned zero results (captured). On 2026-09-17 the petition was pending for the September 28 conference, so no outcome existed to retrieve; the newest document date in the log is 2026-01-02 (the Ninth Circuit opinion). No `data/qp-topics/` read. `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My independent read is 0.3 (see `big_case.notes`). The staged `prediction.json` carries the predictor's `big_case_score`, so I had seen it before writing; my read rests on the questions presented, the docket, and the outcome.
