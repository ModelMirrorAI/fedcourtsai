# Evaluation of claude-baseline — Trice v. Texas, No. 25-1195 (scotus/73281702), evt-petition-disposition

## Outcome and scores

The petition was **denied** on October 5, 2026, after the September 28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `noted_dissent_from_denial` false, `distribution_count` 2). The event's stage is `cert`.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = (0.10 − 0)² = **0.0100**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries band `elevated` under `sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" table is the same version, so the bracketed `reached` figure applies. Pooled resolved-weighted over every rendered Term strictly before the case's Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so the rendered window is the whole pack and no window divergence needs flagging): 484.4 / 2810 = 0.1724.
- `brier_skill_score` = 1 − 0.0100 / 0.1724² = **0.66**.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not written — cert cell.
- `claim_scores`, `process_version`, `base_rate_salience_version`: left to the harness.

## Reasoning quality: 0.85

This is a model cert-stage rationale. It read every provisioned document plus the September 15 reply, stated the posture accurately (every docket fact it cites — waiver May 7, distribution May 12 for the May 28 conference, response requested May 26, extension, BIO July 24, redistribution August 12 for September 28, reply September 15 — matches the snapshot), pooled the correct anchor (about 17 percent over OT2017–OT2024, risk-set figure, which is exactly the rate I score against), and then adjusted with legal substance rather than vibes: no split and none claimed; Richardson's own dictum distinguishing state course-of-conduct child-abuse statutes; the Schad means/elements framework as a legislative choice § 21.02(d) states expressly; a thin, amicus-free petition; vehicle problems (facial challenge, concurrent sentences on other counts). The up-adjustments were properly weighed and explicitly not double counted against the band rate that already prices the CFR. The paragraph on what would move it to 0.25 versus 0.05 is a genuine statement of the uncertainty, and the outcome (a straight denial off the long conference, no writing) is the modal path it named.

What keeps it from higher: the "prior denials" point is admitted to be from memory and could not be verified through CourtListener, and the candidate rightly down-weights it, but it is still carried as an adjustment. The corpus query it ran was generic and, by its own account, did not inform the number. Neither is a flaw in the analysis so much as a limit on how much of it was retrieval-backed, and the candidate said so plainly, which counts for it.

## Leakage: forward, not applicable

Mode `forward`. The prediction was created September 17, 2026 and the petition was decided October 5, 2026, so the case was genuinely open and this was not a mis-provisioned decided case. The log (result capture coverage 1.0) shows: a `fedcourts query` returning recent generic SCOTUS rows (document date 2026-09-17, pre-resolution); three CourtListener searches on the legal topic, the only dated hit a June 2025 opinion in an unrelated Texas habeas case; a web fetch of this petition's reply brief, which was already listed on the provisioned snapshot. One shell call read the candidate's own prediction for a different case as a format reference, which is not material about this case. Nothing queried this docket's disposition, nothing postdates resolution, and no call touched `data/qp-topics/`. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read is 0.35 (see `evaluation.json`): a real post-Ramos question with reach across several states' continuous-abuse statutes, but a splitless petition with no amici, denied silently after one full-briefing conference.
