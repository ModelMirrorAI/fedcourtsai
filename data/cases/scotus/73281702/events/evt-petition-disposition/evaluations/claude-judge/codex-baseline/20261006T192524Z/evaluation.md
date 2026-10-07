# Evaluation of codex-baseline — Trice v. Texas, No. 25-1195 (scotus/73281702), evt-petition-disposition

## Outcome and scores

The petition was **denied** on October 5, 2026, after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `noted_dissent_from_denial` false, `distribution_count` 2). The event's stage is `cert`.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.12 − 0)² = **0.0144**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries band `elevated` under `sal-v4`, matching the heading of the statpack's "Segment base rate by salience band (sal-v4)" table, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before the case's Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so no window divergence needs flagging): 484.4 / 2810 = 0.1724.
- `brier_skill_score` = 1 − 0.0144 / 0.1724² = **0.52**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not written — cert cell.
- `claim_scores`, `process_version`, `base_rate_salience_version`: left to the harness.

## Reasoning quality: 0.80

A careful, well-sourced rationale. It computed the anchor exactly as the contract asks (484 / 2,810 = 17.22 percent over OT2017–OT2024, risk-set figure, explicitly excluding the case's own Term and the terminal figures), and it is the only candidate that went to the primary source on the disputed point, reading Richardson v. United States at 526 U.S. 820–22 through CourtListener and reporting accurately that the majority both notes the special proof difficulties of child-abuse prosecutions and treats unanimity's incorporation as then-unsettled, which supports the petition's premise without invalidating the statute. The reading of the docket sequence is correct and important: the May 26 response request preceded the May 28 conference, so the two distributions are one response-driven redistribution, not a demonstrated relist, and the candidate drew the right inference. It also caught the facial-challenge posture from the appendix as a vehicle disadvantage. The 7 percent writing-on-denial estimate and the modal "unexplained denial" path are what happened.

Deductions: the prose is more cautious than discriminating in places ("a substantial constitutional argument that cannot be dismissed merely by labeling the underlying incidents as means" is asserted without being weighed against the BIO's Schad argument), and the number lands 2 points above claude-baseline's without the rationale identifying what offsets the Richardson dictum and the uniform lower-court authority the BIO collects. The repeated disclaimers about what the adjustment is not are honest but take the place of saying what it is.

## Leakage: forward, not applicable

Mode `forward`. The prediction was created September 17, 2026 and the petition was decided October 5, 2026, so the case was genuinely open. The log (result capture coverage 0.94) has two `unobserved` web-search rows; graded on their queries, both seek the Richardson opinion (a 1999 precedent), not this case. The CourtListener calls read that same opinion. Two in-memory fetches retrieved this petition's own reply brief, already listed on the provisioned snapshot. One early shell `find` named `data/qp-topics` only inside a `-not -path` exclusion, so it did not read that tree; I note it for completeness and do not treat it as a read. Nothing queried this docket's disposition and nothing postdates resolution. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read is 0.35 (see `evaluation.json`): a real post-Ramos question with reach beyond Texas, but a splitless petition with no amici, denied silently after one full-briefing conference.
